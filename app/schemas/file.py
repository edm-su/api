from pydantic import BaseModel


class UploadedFile(BaseModel):
    file_path: str
    file_url: str
