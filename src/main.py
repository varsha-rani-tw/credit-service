import uvicorn
import sys
from pathlib import Path

if __name__ == "__main__":
    # Add parent directory to path so we can import app
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)