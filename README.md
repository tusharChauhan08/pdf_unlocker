# PDF Unlocker

A small FastAPI application that accepts one or more PDF files and returns a ZIP file containing unlocked PDFs. The app supports encrypted PDFs using a shared password or per-file passwords provided as JSON.

## Features

- Upload multiple PDF files in one request
- Unlock encrypted PDFs using:
  - a single shared `password`
  - per-file passwords via a JSON `passwords` field
- Returns a ZIP archive containing unlocked files
- Provides file processing results in response headers

## Requirements

- Python 3.11 or later
- `fastapi`
- `uvicorn`
- `pypdf`
- `python-multipart`
- `cryptography`

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the app

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

By default, the server will be available at `http://127.0.0.1:8000`.

## API Usage

### Endpoint

`POST /unlock-pdfs/`

### Form fields

- `files`: One or more PDF files to upload
- `password`: Optional shared password used for all encrypted PDFs
- `passwords`: Optional JSON string for per-file passwords

### `passwords` JSON format

Use a JSON object where each key is a filename and the value is that file's password. You may also include a `default` password for files without a specific match.

Example:

```json
{
  "file1.pdf": "pass1",
  "file2.pdf": "pass2",
  "default": "sharedpass"
}
```

### Response

- If at least one file is unlocked, the response returns a ZIP file named `unlocked_pdfs.zip`.
- If all files fail to process, the API returns a JSON error response with the processing details.

### Example cURL request

```bash
curl -X POST "http://127.0.0.1:8000/unlock-pdfs/" \
  -F "files=@/path/to/file1.pdf" \
  -F "files=@/path/to/file2.pdf" \
  -F "password=sharedpass"
```

### Example cURL request with per-file passwords

```bash
curl -X POST "http://127.0.0.1:8000/unlock-pdfs/" \
  -F "files=@/path/to/file1.pdf" \
  -F "files=@/path/to/file2.pdf" \
  -F 'passwords={"file1.pdf":"pass1","file2.pdf":"pass2"}'
```

## Notes

- If a PDF is already unlocked, it is still included in the output ZIP.
- If a file is encrypted and no correct password is provided, it will be skipped and reported.
- The service sets an `X-Results` header containing JSON results for each processed file.

## License

No license specified. Use at your own risk.
