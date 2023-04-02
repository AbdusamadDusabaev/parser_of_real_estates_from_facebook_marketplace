import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import pathlib
import datetime

from config import google_sheet_id, api_json, page_name


scopes = ["https://www.googleapis.com/auth/spreadsheets"]
log_name = pathlib.Path("logs", f"log-{datetime.datetime.now()}.txt")


def write_log(message):
    with open(log_name, "a", encoding="utf-8") as file:
        file.write(f"[INFO] ({datetime.datetime.now()}) {message}\n")


def get_service_sacc():
    creds_service = ServiceAccountCredentials.from_json_keyfile_dict(api_json, scopes=scopes).authorize(httplib2.Http())
    return build(serviceName="sheets", version="v4", http=creds_service)


def get_sheet():
    service = get_service_sacc()
    sheet = service.spreadsheets()
    return sheet


def get_exist_object_links_and_current_place_id_from_google_sheet() -> dict:
    sheet = get_sheet()
    response = sheet.values().get(spreadsheetId=google_sheet_id, range=f"{page_name}!A2:AS100000").execute()
    links_and_max_place_id = get_links_and_max_places_id(response=response)
    return links_and_max_place_id


def get_links_and_max_places_id(response) -> dict:
    links = list()
    places_id = [0]
    if "values" in list(response.keys()):
        for element in response["values"]:
            links.append(element[6])
            places_id.append(int(element[10]))
    return {"links": links, "id": max(places_id)}


def record_data(element: dict) -> None:
    sheet = get_sheet()
    values = [[element["title"], element["price"], element["address"], element["animal_friendly"],
              element["date_of_publication"], element["description"], element["object_url"],
              element["rating"], element["date_of_registration"], element["date_of_parsing"], element["id"]]]
    body = {"values": values}
    sheet.values().append(spreadsheetId=google_sheet_id, range=f"{page_name}!A1:I1",
                          valueInputOption="RAW", body=body).execute()
    write_log(message="Данные были успешно записаны в Google Sheets\n")
