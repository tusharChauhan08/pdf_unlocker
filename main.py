from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Annotated
from pypdf import PdfReader, PdfWriter
import io
import zipfile
import json

app = FastAPI()

@app.post("/unlock-pdfs/")
async def unlock_pdfs(
    files: Annotated[List[UploadFile], File(description="Upload multiple PDFs")],
    password: Annotated[Optional[str], Form()] = None,  # single password
    passwords: Annotated[Optional[str], Form()] = None  # JSON for per-file passwords
):
    zip_buffer = io.BytesIO()
    results = []
    files_added = 0


    # Parse per-file passwords if provided
    password_map = {}
    if passwords:
        try:
            password_map = json.loads(passwords)
        except:
            return JSONResponse(
                {"error": "Invalid 'passwords' JSON format"},
                status_code=400
            )

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:

        for file in files:
            filename = file.filename

            try:
                content = await file.read()
                reader = PdfReader(io.BytesIO(content))

                print(f"Processing: {filename}")
 
                # Determine password priority:
                # 1. per-file password
                # 2. default from JSON
                # 3. single password field
                file_password = (
                    password_map.get(filename)
                    or password_map.get("default")
                    or password
                )

                # Handle encrypted PDFs
                if reader.is_encrypted:
                    print("Encrypted PDF")

                    if not file_password:
                        results.append({
                            "file": filename,
                            "status": "❌ Password required"
                        })
                        continue

                    if reader.decrypt(file_password) == 0:
                        results.append({
                            "file": filename,
                            "status": "❌ Wrong password"
                        })
                        continue
                    else:
                        print("Password correct")

                else:
                    print("Already unlocked PDF")

                # Remove password
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)

                output_pdf = io.BytesIO()
                writer.write(output_pdf)

                zipf.writestr(filename, output_pdf.getvalue())
                files_added += 1

                if reader.is_encrypted:
                    results.append({
                        "file": filename,
                        "status": "✅ Unlocked"
                    })
                else:
                    results.append({
                        "file": filename,
                        "status": "ℹ️ Already unlocked"
                    })

            except Exception as e:
                print("Error:", str(e))
                results.append({
                    "file": filename,
                    "status": "❌ Corrupt or unsupported PDF"
                })

    # ❌ Prevent empty ZIP
    if files_added == 0:
        return JSONResponse(
            {
                "error": "No files were processed",
                "details": results
            },
            status_code=400
        )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=unlocked_pdfs.zip",
            "X-Results": json.dumps(results)  # optional: frontend can read this
        }
    )
