import os
from io import BytesIO
from typing import List, Optional, Tuple

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None
    BotoCoreError = Exception
    ClientError = Exception


class S3StorageService:
    def __init__(
        self,
        bucket_name: str,
        region_name: str = "eu-central-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self._client = self._build_client()

    def _build_client(self):
        if boto3 is None:
            raise RuntimeError("boto3 is not installed. Run: pip install boto3")

        if self.aws_access_key_id and self.aws_secret_access_key:
            return boto3.client(
                "s3",
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )

        return boto3.client("s3", region_name=self.region_name)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        return filename.replace(" ", "_")

    def build_s3_key(self, filename: str, prefix: str = "uploads/") -> str:
        normalized_prefix = prefix.strip()
        if normalized_prefix and not normalized_prefix.endswith("/"):
            normalized_prefix += "/"
        return f"{normalized_prefix}{self.sanitize_filename(filename)}"

    def upload_bytes(
        self,
        file_bytes: bytes,
        filename: str,
        prefix: str = "uploads/",
        content_type: str = "application/octet-stream",
    ) -> str:
        s3_key = self.build_s3_key(filename=filename, prefix=prefix)

        self._client.upload_fileobj(
            Fileobj=BytesIO(file_bytes),
            Bucket=self.bucket_name,
            Key=s3_key,
            ExtraArgs={"ContentType": content_type},
        )
        return s3_key

    def upload_streamlit_files(self, uploaded_files, prefix: str = "uploads/") -> Tuple[List[str], List[str]]:
        uploaded_keys: List[str] = []
        errors: List[str] = []

        for uploaded_file in uploaded_files:
            try:
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()

                s3_key = self.upload_bytes(
                    file_bytes=file_bytes,
                    filename=uploaded_file.name,
                    prefix=prefix,
                    content_type=uploaded_file.type or "application/vnd.ms-excel",
                )

                uploaded_keys.append(s3_key)
                uploaded_file.seek(0)

            except (ClientError, BotoCoreError, Exception) as exc:
                errors.append(f"{uploaded_file.name}: {exc}")

        return uploaded_keys, errors

    def list_excel_files(self, prefix: str = "") -> List[str]:
        response = self._client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
        )
        keys = [obj["Key"] for obj in response.get("Contents", [])]
        return [key for key in keys if key.lower().endswith((".xlsx", ".xls"))]

    def download_file_bytes(self, s3_key: str) -> bytes:
        buffer = BytesIO()
        self._client.download_fileobj(self.bucket_name, s3_key, buffer)
        return buffer.getvalue()

    def generate_presigned_download_url(self, s3_key: str, expires_in: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_key},
            ExpiresIn=expires_in,
        )