import os
from app import create_app
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the FastAPI app instance
app = create_app()

if __name__ == "__main__":
    # Run the Uvicorn ASGI server
    uvicorn.run(
        "run:app",  # Points to the app object in this file
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,  # Enables auto-reload for development
    )
