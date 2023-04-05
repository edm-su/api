from typing_extensions import Self


class UploadError(Exception):
    message = "Upload error"


class FileIsNotImageError(UploadError):
    message = "File is not an image"


class FileIsTooLargeError(UploadError):
    def __init__(
        self: Self,
        file_size: int,
        max_size: int,
    ) -> None:
        self.message = (
            f"File size is {file_size} bytes, "
            f"but max size is {max_size} bytes"
        )
