import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = os.getenv("GOOGLE_CREDENTIALS_JSON")

import json
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_dict), scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(os.getenv("GOOGLE_SHEET_URL"))

def append_record(manager_name, date, amount, comment):
    try:
        worksheet = spreadsheet.worksheet(manager_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=manager_name, rows="100", cols="5")
        worksheet.append_row(["ID", "Дата", "Сумма", "Комментарий"])
    worksheet.append_row([manager_name, date.strftime("%d.%m.%Y %H:%M"), amount, comment])
