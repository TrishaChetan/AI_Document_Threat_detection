from pathlib import Path
import uuid

from services.analysis_pipeline import AnalysisPipeline


class ScanService:

    def __init__(self):
        self.upload_directory = Path("temp_uploads")
        self.upload_directory.mkdir(parents=True, exist_ok=True)

        self.pipeline = AnalysisPipeline()

    def save_uploaded_file(self, file_bytes: bytes, filename: str) -> Path:

        extension = Path(filename).suffix

        if not extension:
            raise ValueError("Uploaded file must have an extension.")

        unique_name = f"{uuid.uuid4().hex}{extension}"

        destination = self.upload_directory / unique_name

        destination.write_bytes(file_bytes)

        return destination

    def process_scan(self, file_path: Path) -> dict:

        return self.pipeline.run(file_path)


scan_service = ScanService()