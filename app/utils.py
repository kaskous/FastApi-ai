import logging
import os
from typing import Tuple, Dict, Any, Optional, Generator


from .models import FileMetadata
from sqlalchemy.orm import Session
from app.db import get_db
from openai import ChatCompletion
import PyPDF2
from docx import Document

openai_api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)


def process_files(db: Session) -> None:
    """
    Process files in the upload folder and save metadata to the database.

    Args:
        db (Session): The database session.
        upload_folder (str): The path to the upload folder.

    Raises:
        Exception: If an error occurs during processing, the error is logged and re-raised.
    """
    try:
        upload_folder = os.getenv("UPLOAD_FOLDER")
        for filename in os.listdir(upload_folder):
            file_path: str = os.path.join(upload_folder, filename)

            # Check if the current item is a file
            if os.path.isfile(file_path):
                existing_file: Optional[FileMetadata] = (
                    db.query(FileMetadata)
                    .filter_by(name=filename, path=file_path)
                    .first()
                )

                if existing_file:
                    logger.info(
                        f"File '{filename}' already exists in the database. Skipping..."
                    )
                    continue

                file_format: str = filename.split(".")[-1]
                file_size: int = os.path.getsize(file_path)

                new_file: FileMetadata = FileMetadata(
                    name=filename, path=file_path, format=file_format, size=file_size
                )

                db.add(new_file)

        db.commit()
        logger.info(f"Successfully processed files from folder: {upload_folder}")

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        db.rollback()
        raise


def get_file_summary(file_id: int, db: Session) -> Dict[str, Any]:
    """
    Generate a summary for the content of a file using OpenAI's API.

    Args:
        file_id (int): The ID of the file to summarize.
        db (Session): The database session.

    Returns:
        Dict[str, Any]: A dictionary containing the summary or an error message.
    """
    file: Optional[FileMetadata] = db.get(FileMetadata, file_id)
    if not file:
        return {"error": "File not found"}

    content: str = extract_content(file.path, file.format)
    if not content:
        return {"error": "Unable to extract content from the file."}

    try:
        completion: Dict[str, Any] = ChatCompletion.create(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            messages=[{"role": "system", "content": f"Summarize: {content}"}],
        )

        summary: str = completion["choices"][0]["message"]["content"]
        file.summary = summary
        db.commit()
        return {"summary": summary}

    except Exception as e:
        logger.error(f"Error generating summary for file {file_id}: {e}")
        return {"error": "Failed to generate summary."}


def get_file_content(file_id: int, db: Session) -> Dict[str, Any]:
    """
    Retrieve the content of a file.

    Args:
        file_id (int): The ID of the file to retrieve.
        db (Session): The database session.

    Returns:
        Dict[str, Any]: A dictionary containing the file content or an error message.
    """
    file: Optional[FileMetadata] = db.get(FileMetadata, file_id)
    if not file:
        return {"error": "File not found"}
    content: str = extract_content(file.path, file.format)
    if not content:
        return {"error": "Unable to extract content from the file."}

    return {"content": content}


def extract_content(file_path: str, file_format: str) -> str:
    """
    Extract content from a file based on its format.

    Args:
        file_path (str): The path to the file.
        file_format (str): The format of the file (e.g., 'pdf', 'docx', 'txt').

    Returns:
        str: The extracted content as a string, or an empty string if the format is unsupported.
    """
    try:
        if file_format.lower() == "pdf":
            with open(file_path, "rb") as file:
                reader: PyPDF2.PdfReader = PyPDF2.PdfReader(file)
                return "".join(
                    page.extract_text() for page in reader.pages if page.extract_text()
                )

        elif file_format.lower() == "docx":
            doc: Document = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])

        elif file_format.lower() == "txt":
            with open(file_path, "r") as file:
                return file.read()

    except Exception as e:
        logger.error(f"Error extracting content from file {file_path}: {e}")

    return ""
