import json
import logging

from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

logger = logging.getLogger(__name__)


class GDriveManager:
    """Manages Google Drive authentication and file operations."""

    def __init__(self, json_content: str) -> None:
        """
        Initializes the Google Drive manager with service account credentials.

        Args:
            json_content: The JSON string containing the service account credentials.
        """
        self.scope: list[str] = ['https://www.googleapis.com/auth/drive']
        creds_dict: dict = json.loads(json_content)

        self.gauth = GoogleAuth()
        self.gauth.auth_method = 'service'
        self.gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, self.scope
        )
        self.drive = GoogleDrive(self.gauth)

    def download_session_file(self, session_name: str) -> bool:
        """
        Downloads the Telegram session file from Google Drive if it exists.

        Args:
            session_name: The name of the session file (without extension).

        Returns:
            bool: True if the file was successfully downloaded, False otherwise.
        """
        file_name = f'{session_name}.session'
        file_list = self.drive.ListFile({'q': f"title = '{file_name}' and trashed=false"}).GetList()

        if file_list:
            google_file = file_list[0]
            logger.info(f'Downloading session: {google_file["title"]}')
            google_file.GetContentFile(file_name)
            return True
        logger.warning('Session file not found on Google Drive.')
        return False
