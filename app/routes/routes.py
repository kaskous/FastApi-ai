from typing import Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import FileMetadata
from app.utils import get_file_content, get_file_summary, process_files

router = APIRouter()


@router.post("/refresh", response_model=dict)
def refresh_files(db: Session = Depends(get_db)):
    """
    Refresh the file metadata by processing the upload folder.

    Returns:
        dict: A message confirming successful processing.
    """
    process_files(db)
    return {"message": "Files processed successfully."}


@router.get("/files", response_model=List[dict])
def list_files(db: Session = Depends(get_db)):
    """
    List all files stored in the database.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[dict]: A JSON response containing metadata for all files.
    """
    files = db.query(FileMetadata).all()
    return [
        {
            "id": file.id,
            "name": file.name,
            "path": file.path,
            "format": file.format,
            "size": file.size,
        }
        for file in files
    ]


@router.get("/files/{id}/summary", response_model=dict)
def file_summary(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a summary for the specified file.

    Args:
        id (int): The ID of the file.
        db (Session): Database session dependency.

    Returns:
        dict: A JSON response containing the summary or an error message.
    """
    summary = get_file_summary(id, db)
    if "error" in summary:
        # Handle error response
        raise HTTPException(status_code=404, detail=summary["error"])
    return summary


@router.get("/files/{id}/content", response_model=dict)
def file_content(id: int, db: Session = Depends(get_db)):
    """
    Retrieve the content of the specified file.

    Args:
        id (int): The ID of the file.
        db (Session): Database session dependency.

    Returns:
        dict: A JSON response containing the file content or an error message.
    """
    content = get_file_content(id, db)
    if not content:
        raise HTTPException(status_code=404, detail="File not found")
    return content
