import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_name("/root/credentials.json", scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(os.getenv("GOOGLE_SHEET_URL"))

def append_to_named_sheet(sheet_name: str, row: list):
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="10")
        worksheet.append_row(["ID", "Дата", "Сумма", "Комментарий"])
    worksheet.append_row(row)

def get_balance(sheet_name):
    worksheet = spreadsheet.worksheet(sheet_name)
    records = worksheet.get_all_values()
    total = 0.0
    for row in records[1:]:
        try:
            amount = float(row[2])
            total += amount
        except (ValueError, IndexError):
            continue
    return total
