import os
import uuid



class LocalStorageService:
    """
    Dịch vụ lưu trữ file cục bộ (Local Disk Storage) cho các bản vẽ / ảnh 3D upload.
    """

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_bytes: bytes, original_filename: str = "image.png") -> str:
        """
        Lưu file vào đĩa cứng và trả về đường dẫn file.
        """
        ext = os.path.splitext(original_filename)[1] or ".png"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(self.upload_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return file_path
