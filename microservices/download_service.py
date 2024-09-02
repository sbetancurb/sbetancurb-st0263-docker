from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

class DownloadService:
    def __init__(self, directory):
        self.router = APIRouter()
        self.directory = directory

        @self.router.get("/download/{filename}")
        def download_file(filename: str):
            file_path = os.path.join(self.directory, filename)

            if os.path.exists(file_path):
                return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')
            else:
                raise HTTPException(status_code=404, detail="File not found")
