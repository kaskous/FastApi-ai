import os
import tempfile
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.models import FileMetadata
from fastapi.testclient import TestClient
from run import app


# In-memory SQLite database with shared connection
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a single shared connection for the test session
connection = engine.connect()

# Bind the shared connection to the sessionmaker
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)


# Override FastAPI's database dependency
def override_get_db():
    """Override get_db to use the shared TestingSessionLocal."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the override to FastAPI
app.dependency_overrides[get_db] = override_get_db


# Fixture to initialize and tear down the schema
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create and drop tables for the entire test session."""
    Base.metadata.create_all(bind=connection)  # Create schema on the shared connection
    yield
    Base.metadata.drop_all(bind=connection)  # Drop schema after tests


# Test to ensure table creation
def test_table_creation():
    inspector = inspect(connection)  # Use the shared connection
    tables = inspector.get_table_names()
    assert "file_metadata" in tables


# Test the refresh files route
def test_refresh_files_route():
    client = TestClient(app)
    response = client.post("/api/refresh", json={})
    assert response.status_code == 200
    assert response.json() == {"message": "Files processed successfully."}


# Test the list files route
def test_list_files_route():
    client = TestClient(app)
    response = client.get("/api/files")

    assert response.status_code == 200
    assert len(response.json()) == 5


# # Test the file summary route
def test_file_summary_route():
    client = TestClient(app)
    db = next(override_get_db())
    dummy_file = FileMetadata(
        name="dummy.txt", path="/dummy.txt", format="txt", size=10
    )
    db.add(dummy_file)
    db.commit()

    response = client.get(f"/api/files/{dummy_file.id}/summary")
    assert response.status_code == 404


# # Test the file content route
def test_file_content_route():
    client = TestClient(app)
    db = next(override_get_db())

    # Create a temporary directory for the file
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "dummy.txt")

        # Write some content to the file
        with open(file_path, "w") as f:
            f.write("This is a test file content.")

        # Add a dummy file record to the database
        dummy_file = FileMetadata(
            name="dummy.txt",
            path=file_path,
            format="txt",
            size=os.path.getsize(file_path),
        )
        db.add(dummy_file)
        db.commit()

        # Call the route
        response = client.get(f"/api/files/{dummy_file.id}/content")
        assert response.status_code == 200
        assert "error" not in response.json()
        assert response.json()["content"] == "This is a test file content."
