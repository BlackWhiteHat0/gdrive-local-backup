import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from dotenv import load_dotenv
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = os.getenv('FOLDER_ID')
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')

if not FOLDER_ID or not DOWNLOAD_DIR:
    raise ValueError('請在 .env 設定 FOLDER_ID 與 DOWNLOAD_DIR')

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def process_folder(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get('files', [])

    EXPORT_MAP = {
        'application/vnd.google-apps.document':
            ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
        'application/vnd.google-apps.spreadsheet':
            ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),
        'application/vnd.google-apps.presentation':
            ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),
    }

    for f in files:
        file_id, name, mime = f['id'], f['name'], f['mimeType']

        if mime == 'application/vnd.google-apps.folder':
            # 遇到子資料夾 → 遞迴進去處理
            print(f'進入子資料夾：{name}')
            process_folder(service, file_id)
            continue

        if mime in EXPORT_MAP:
            export_mime, ext = EXPORT_MAP[mime]
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            if not name.endswith(ext):
                name = name + ext
        elif mime.startswith('application/vnd.google-apps'):
            print(f'略過無法下載的 Google 檔案：{name}')
            continue
        else:
            request = service.files().get_media(fileId=file_id)

        path = os.path.join(DOWNLOAD_DIR, name)
        with io.FileIO(path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        service.files().delete(fileId=file_id).execute()
        print(f'已下載並刪除：{name}')


def main():
    service = get_service()
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    process_folder(service, FOLDER_ID)

if __name__ == '__main__':
    main()