import time
from selenium import webdriver
from bs4 import BeautifulSoup

from main import init_browser, authorization
from connect import write_log, get_all_object_relevance_from_google_sheet, record_new_all_object_relevance


def run():
    write_log(message="Программа запущена")
    start_time = time.time()
    main()
    stop_time = time.time()
    write_log(message=f"На работу программы ушло {stop_time - start_time} секунд")


def main():
    all_object_relevance = get_all_object_relevance_from_google_sheet()

    if len(all_object_relevance) == 0:
        write_log(message="Таблица пустая. Для проверки релевантности объектов таблицы таблица не должна быть пустой")
        return None
    browser = init_browser()
    authorization(browser=browser)
    new_all_object_relevance = list()
    for object_relevance_dict in all_object_relevance:
        object_url = object_relevance_dict["object_url"]
        object_relevance = object_relevance_dict["object_relevance"]
        if object_relevance == "listing is deleted":
            new_all_object_relevance.append("listing is deleted")
            write_log(message=f"Релевантность объекта {object_url}: listing is deleted")
            continue
        new_object_relevance = get_object_relevance(browser=browser, object_url=object_url)
        new_all_object_relevance.append(new_object_relevance)
        write_log(message=f"Релевантность объекта {object_url}: {new_object_relevance}")
    record_new_all_object_relevance(new_all_object_relevance=new_all_object_relevance)


def get_object_relevance(browser: webdriver.Chrome, object_url: str) -> str:
    browser.get(url=object_url)
    bs_object = BeautifulSoup(browser.page_source, "lxml")

    the_presence_of_redirection = browser.current_url != object_url
    the_presence_of_the_inscription_rented = "rented" in bs_object.text.lower()
    the_presence_of_the_inscription_pending = "pending" in bs_object.text.lower()
    all_checks = [
        the_presence_of_redirection,
        the_presence_of_the_inscription_rented,
        the_presence_of_the_inscription_pending,
    ]

    if any(all_checks):
        object_relevance = "listing is deleted"
        return object_relevance

    object_relevance = "listing is available"
    return object_relevance


if __name__ == "__main__":
    run()
