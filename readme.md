# File Summary API
A RESTful API built using FastAPI to process and summarize document files.

## Requirements

This application fulfills the following functionalities:

- Accepts `.pdf`, `.docx`, and `.txt` file formats for processing.
- Extracts metadata (name, path, format, size) and stores it in a relational database.
- Generates a summary for each file using OpenAI's GPT.
- Provides endpoints for listing metadata, fetching file content, and retrieving summaries.
- Configured with Swagger (OpenAPI) documentation for easy API exploration.

## API Endpoints

### 1. **Refresh Files**
Processes files in the upload directory and updates the database.

**Endpoint**: `POST /api/refresh`

**Response**:
```json
{
  "message": "Files processed successfully."
}
```
<hr/>
### 2. **List Files**

Fetches metadata for all stored files.

- **Endpoint**: `GET /api/files`
- **Response**:
  - A list of file metadata in JSON format:
    - `id`: The unique identifier for the file.
    - `name`: The name of the file.
    - `path`: The file's location on the server.
    - `format`: The file type (e.g., `pdf`, `docx`, `txt`).
    - `size`: The file size in bytes.

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "example.pdf",
    "path": "./uploads/example.pdf",
    "format": "pdf",
    "size": 1024
  },
  {
    "id": 2,
    "name": "example.docx",
    "path": "./uploads/example.docx",
    "format": "docx",
    "size": 2048
  }
]

```
<hr/>
### 3. **Get File Summary**

Generates and retrieves the summary for a specific file.

- **Endpoint**: `GET /api/files/{id}/summary`
- **Response**:
  - Returns the summary of the file content in JSON format.
    - `summary`: The generated summary of the file.

**Example Response**:
```json
{
  "summary": "This document provides an overview of..."
}
```
<hr/>

### 4. **Get File Content**

Fetches the raw content of a specific file.

- **Endpoint**: `GET /api/files/{id}/content`
- **Response**:
  - Returns the raw content of the file in JSON format.
    - `content`: The extracted text of the file.

**Example Response**:
```json
{
  "content": "The complete text of the document."
}
```

<hr/>

## Tech Stack Used

| Technology              | Purpose                                   |
|--------------------------|-------------------------------------------|
| **FastAPI**             | API Framework                            |
| **SQLAlchemy + SQLite** | ORM and Database                         |
| **OpenAI API**          | For file summarization                   |
| **Alembic**             | Database migrations                      |
| **Uvicorn**             | ASGI server                              |
| **Swagger (FastAPI)**   | API documentation                        |

## Running the Application (Non-Dockerized)

The application does not currently use Docker. To run it locally, follow the steps below:

1. **Create a Virtual Environment**:
   Set up a Python virtual environment to manage dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   
2. **Install Dependencies: Install all required dependencies**:

`pip install -r requirements.txt`


3. **Run the Application: Start the application by running the `run.py` file**:

`python run.py`

4. **Access the API: Open your browser and navigate to**:

`http://localhost:8000/docs`

to access the Swagger documentation.


## Running the Tests
To verify the application’s functionality, run the test suite using pytest. The test cases are located in the tests/test_routes.py file.

1. **Install pytest (if not already installed)**:

`pip install pytest`

2. **Run the tests**:

`pytest tests/test_routes.py`
