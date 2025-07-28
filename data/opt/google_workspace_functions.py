from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = "/app/backend/data/opt/service_account.json"
SCOPES_DRIVE = ["https://www.googleapis.com/auth/drive"]
SCOPES_DOCS = ["https://www.googleapis.com/auth/documents"]
SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets"]
SCOPES_SLIDES = ["https://www.googleapis.com/auth/presentations"]

# Google Drive Actions


def list_drive_files():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DRIVE
    )
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(pageSize=10).execute()
    return results.get("files", [])


def upload_file_to_drive(filename, filepath):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DRIVE
    )
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": filename}
    media = MediaFileUpload(filepath, resumable=True)
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    return file.get("id")


def read_drive_file(file_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DRIVE
    )
    service = build("drive", "v3", credentials=creds)
    file = service.files().get(fileId=file_id, fields="name, mimeType").execute()
    return file


# Google Docs Actions


def create_doc(title):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DOCS
    )
    service = build("docs", "v1", credentials=creds)
    doc = service.documents().create(body={"title": title}).execute()
    return doc.get("documentId")


def read_doc(doc_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DOCS
    )
    service = build("docs", "v1", credentials=creds)
    doc = service.documents().get(documentId=doc_id).execute()
    return doc


def edit_doc(doc_id, requests):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_DOCS
    )
    service = build("docs", "v1", credentials=creds)
    result = (
        service.documents()
        .batchUpdate(documentId=doc_id, body={"requests": requests})
        .execute()
    )
    return result


# Google Sheets Actions


def create_sheet(title):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_SHEETS
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = (
        service.spreadsheets().create(body={"properties": {"title": title}}).execute()
    )
    return sheet.get("spreadsheetId")


def read_sheet(sheet_id, range_name):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_SHEETS
    )
    service = build("sheets", "v4", credentials=creds)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_name)
        .execute()
    )
    return result.get("values", [])


def edit_sheet(sheet_id, range_name, values):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_SHEETS
    )
    service = build("sheets", "v4", credentials=creds)
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=sheet_id, range=range_name, valueInputOption="RAW", body=body
        )
        .execute()
    )
    return result


# Google Slides Actions


def create_slide(title):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_SLIDES
    )
    service = build("slides", "v1", credentials=creds)
    slide = service.presentations().create(body={"title": title}).execute()
    return slide.get("presentationId")


def read_slide(slide_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_SLIDES
    )
    service = build("slides", "v1", credentials=creds)
    slide = service.presentations().get(presentationId=slide_id).execute()
    return slide


def edit_slide(slide_id, requests):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES_SLIDES
    )
    service = build("slides", "v1", credentials=creds)
    result = (
        service.presentations()
        .batchUpdate(presentationId=slide_id, body={"requests": requests})
        .execute()
    )
    return result
