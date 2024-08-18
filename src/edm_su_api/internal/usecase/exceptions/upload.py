from typing_extensions import Self


class UploadError(Exception):
    pass


class FileIsNotImageError(UploadError):
    def __init__(self: Self) -> None:
        super().__init__("File is not an image")


class FileIsTooLargeError(UploadError):
    def __init__(
        self: Self,
        file_size: int,
        max_size: int,
    ) -> None:
        super().__init__(
            f"File size is {file_size} bytes, "
            f"but max size is {max_size} bytes",
        )
