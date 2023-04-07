import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import requests

import os
import pathlib
import datetime

from config import google_sheet_id, api_json, page_name, root_server_image_url


scopes = ["https://www.googleapis.com/auth/spreadsheets"]
BASE_DIR = os.path.dirname(os.path.abspath(__name__))
PHOTOS_DIR = pathlib.Path(BASE_DIR, "photos")
log_name = pathlib.Path(BASE_DIR, "logs", f"log-{datetime.datetime.now()}.txt")


def write_log(message: str) -> None:
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
    links_and_max_place_id = get_links_and_max_place_id(response=response)
    return links_and_max_place_id


def get_links_and_max_place_id(response) -> dict:
    links = list()
    places_id = [0]
    if "values" in list(response.keys()):
        for element in response["values"]:
            links.append(element[6])
            places_id.append(int(element[11]))
    links_and_max_place_id = {
        "links": links,
        "id": max(places_id)
    }
    return links_and_max_place_id


def save_images_and_get_image_paths(main_image_url: str, image_urls: list, object_id: str) -> dict:
    current_photos_dir = pathlib.Path(PHOTOS_DIR, object_id)
    os.mkdir(path=current_photos_dir)

    main_image_path = pathlib.Path(current_photos_dir, "main-image.jpg")
    record_image_in_file_system(image_path=main_image_path, image_url=main_image_url)
    server_main_image_url = f"{root_server_image_url}{main_image_path}"

    server_image_urls = list()
    for image_index, image_url in enumerate(image_urls):
        image_path = pathlib.Path(current_photos_dir, f"image-{image_index + 1}.jpg")
        record_image_in_file_system(image_path=image_path, image_url=image_url)
        server_image_url = f"{root_server_image_url}{image_path}"
        server_image_urls.append(server_image_url)

    image_paths = {
        "server_main_image_url": server_main_image_url,
        "server_image_urls": server_image_urls,
    }

    return image_paths


def record_image_in_file_system(image_path: pathlib.Path, image_url: str) -> None:
    response = requests.get(url=image_url)
    with open(image_path, "wb") as file:
        file.write(response.content)


def record_data(object_info: dict) -> None:
    sheet = get_sheet()
    values = [[
        object_info["title"],
        object_info["price"],
        object_info["address"],
        object_info["animal_friendly"],
        object_info["date_of_publication"],
        object_info["description"],
        object_info["object_url"],
        object_info["rating"],
        object_info["author_date_of_registration"],
        object_info["chat_to_author_url"],
        object_info["date_of_parsing"],
        object_info["place_id"],
        object_info["relevance"],
        object_info["main_image_url"],
        *object_info["image_urls"],
    ]]
    body = {"values": values}
    sheet.values().append(spreadsheetId=google_sheet_id, range=f"{page_name}!A1:AH1",
                          valueInputOption="RAW", body=body).execute()
    write_log(message="Данные были успешно записаны в Google Sheets\n")


def get_all_object_relevance_from_google_sheet() -> (list, None):
    sheet = get_sheet()
    response = sheet.values().get(spreadsheetId=google_sheet_id, range=f"{page_name}!A2:AS100000").execute()

    if "values" not in list(response.keys()):
        all_object_relevance = None
        return all_object_relevance

    all_object_relevance = [{"object_url": row[6], "object_relevance": row[12]} for row in response["values"]]
    return all_object_relevance


def record_new_all_object_relevance(new_all_object_relevance: list) -> None:
    sheet = get_sheet()
    body = {
        "valueInputOption": "RAW",
        "data": [
            {
                "range": f"{page_name}!M{index + 2}",
                "values": [[new_object_relevance]]
            }
            for index, new_object_relevance in enumerate(new_all_object_relevance)
        ]
    }
    sheet.values().batchUpdate(spreadsheetId=google_sheet_id, body=body).execute()
    write_log(message="Данные в таблице были успешно обновлены\n")
