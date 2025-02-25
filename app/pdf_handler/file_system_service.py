import os
import logging
import requests
from typing import Union, IO, Optional
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)


class FileSystemService:
    def __init__(self, base_url: str | None):
        load_dotenv()
        self.base_url = os.getenv("FILE_SYSTEM_URL") if base_url is None else base_url

    def upload_file(
            self,
            file_data: Union[bytes, IO[bytes]],
            filename: str,
            content_type: str = "application/pdf"
    ) -> dict:
        """
        Upload a file from memory or file object
        :param file_data: Bytes content or file-like object
        :param filename: Name for the uploaded file
        :param content_type: MIME type of the file
        :return: Server response message
        """
        try:
            url = f"{self.base_url}/upload"

            files = {'file': (filename, file_data, content_type)}
            response = requests.post(url, files=files)

            response.raise_for_status()
            logging.info(f"File {filename} uploaded successfully")
            return response.json()

        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            return {"message": "Failed to upload file"}

    def download_file(
            self,
            filename: str,
            save_path: Optional[Union[str, Path]] = None
    ) -> Union[bytes, str]:
        """
        Download a file from the server
        :param filename: Name of the file to download
        :param save_path: Optional path to save the file (returns bytes if None)
        :return: File bytes or path to saved file
        """
        try:
            url = f"{self.base_url}/download/{filename}"
            response = requests.get(url)
            response.raise_for_status()

            if save_path is None:
                return response.content

            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)

            logging.info(f"File {filename} saved to {save_path}")
            return str(save_path)

        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            raise
