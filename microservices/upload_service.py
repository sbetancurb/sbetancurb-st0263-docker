from fastapi import APIRouter, File, UploadFile, HTTPException
import os

class UploadService:
    def __init__(self, directory):
        self.router = APIRouter()
        self.directory = directory

        @self.router.post("/upload/")
        async def upload_file(file: UploadFile = File(...)):
            file_path = os.path.join(self.directory, file.filename)

            try:
                with open(file_path, "wb") as f:
                    f.write(await file.read())
                return {"filename": file.filename, "message": "File uploaded successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An error occurred while uploading the file: {str(e)}")

