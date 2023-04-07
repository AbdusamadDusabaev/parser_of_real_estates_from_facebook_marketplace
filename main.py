import time
import datetime
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from config import (
    facebook_login, facebook_password,
    limit_of_pages_from_one_run, city_code, filter_words,
    headless_mode
)
from connect import (
    get_exist_object_links_and_current_place_id_from_google_sheet,
    record_data, write_log, save_images_and_get_image_paths
)


domain = "https://www.facebook.com"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"


def run(keywords: list = None) -> None:
    write_log(message="Программа запущена")
    start_time = time.time()
    main(keywords=keywords)
    stop_time = time.time()
    write_log(message=f"На работу программы ушло {stop_time - start_time} секунд")


def main(keywords: list) -> None:
    start_data = get_exist_object_links_and_current_place_id_from_google_sheet()
    exist_object_links = start_data["links"]
    current_place_id = start_data["id"]
    browser = init_browser()
    try:
        authorization(browser=browser)
        all_object_links = get_all_object_links_given_keywords(browser=browser, keywords=keywords)
        new_object_links = get_new_object_links(all_object_links=all_object_links,
                                                exist_object_links=exist_object_links)
        write_log(message=f"Было найдено {len(new_object_links)} записей\n")
        parse_new_object_links(new_object_links=new_object_links, browser=browser, current_place_id=current_place_id)
        write_log(message="END")
    finally:
        browser.close()
        browser.quit()


def init_browser() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-notifications")
    if headless_mode:
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--profile-directory=Profile_1")
    browser = webdriver.Chrome(options=options)
    return browser


def authorization(browser: webdriver.Chrome) -> None:
    write_log(message="Авторизуемся в системе...")
    browser.get(url="https://www.facebook.com/")
    input_credentials_and_login(browser=browser)
    time.sleep(5)
    write_log(message="Авторизация завершена")


def input_credentials_and_login(browser: webdriver.Chrome) -> None:
    login_input = browser.find_element(By.ID, "email")
    login_input.send_keys(facebook_login)
    password_input = browser.find_element(By.ID, "pass")
    password_input.send_keys(facebook_password)
    login_button = browser.find_element(By.TAG_NAME, "button")
    login_button.click()


def get_all_object_links_given_keywords(browser: webdriver.Chrome, keywords: list) -> List[str]:
    current_url_s = get_current_url(keywords=keywords)

    if isinstance(current_url_s, str):
        write_log(message="Собираем ссылки на объекты...")
        all_object_links = get_all_object_links(browser=browser, url=current_url_s)
        return all_object_links

    all_object_links = list()
    for keyword, url in current_url_s.items():
        write_log(message=f"Собираем ссылки на объекты по ключевому слову {keyword}...")
        all_object_links_by_keyword = get_all_object_links(browser=browser, url=url)
        all_object_links.extend(all_object_links_by_keyword)
    return all_object_links


def get_current_url(keywords: list) -> (str, dict):
    if keywords is None:
        current_url = "https://www.facebook.com/marketplace/category/propertyrentals?" \
                      "sortBy=creation_time_descend&exact=false"
        return current_url

    current_urls = dict()
    for keyword in keywords:
        url = f"https://www.facebook.com/marketplace/{city_code}/search?" \
              f"sortBy=creation_time_descend&query={keyword}&exact=false"
        current_urls[keyword] = url
    return current_urls


def get_all_object_links(browser: webdriver.Chrome, url: str) -> List[str]:
    browser.get(url=url)
    roll_pages_of_marketplace(browser=browser)
    bs_object = BeautifulSoup(browser.page_source, "lxml")
    possible_object_links_class = "x3ct3a4"
    possible_object_link_tags = bs_object.find_all(name="div", class_=possible_object_links_class)
    object_links = list()
    for possible_object_link_tag in possible_object_link_tags:
        if possible_object_link_tag.a is not None:
            object_link = domain + possible_object_link_tag.a["href"].split("?")[0]
            object_links.append(object_link)
    return object_links


def roll_pages_of_marketplace(browser: webdriver.Chrome) -> None:
    index = 0
    previous_bs_object = BeautifulSoup(browser.page_source, "lxml")
    while True:
        index += 1
        write_log(message=f"Ссылки со страницы {index} страницы успешно собраны")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        current_bs_object = BeautifulSoup(browser.page_source, "lxml")
        if current_bs_object == previous_bs_object or index == limit_of_pages_from_one_run:
            return None
        previous_bs_object = current_bs_object


def get_new_object_links(all_object_links: List[str], exist_object_links: List[str]) -> List[str]:
    new_object_links = list()
    for object_link in all_object_links:
        if object_link not in exist_object_links:
            new_object_links.append(object_link)
    return new_object_links


def parse_new_object_links(new_object_links: List[str], browser: webdriver.Chrome, current_place_id: int) -> None:
    for object_link in new_object_links:
        try:
            object_info = get_object_info(browser=browser, object_url=object_link)
            object_is_valid = check_valid_object(description=object_info["description"])
            if object_is_valid:
                current_place_id += 1
                object_info["date_of_parsing"] = str(datetime.date.today())
                object_info["place_id"] = str(current_place_id)
                write_log(message=str(object_info))
                object_id = object_link.split("/")[-2]
                new_image_urls = save_images_and_get_image_paths(main_image_url=object_info["main_image_url"],
                                                                 image_urls=object_info["image_urls"],
                                                                 object_id=object_id)
                object_info["main_image_url"] = new_image_urls["server_main_image_url"]
                object_info["image_urls"] = new_image_urls["server_image_urls"]
                record_data(object_info=object_info)
        except Exception as ex:
            print(object_link)
            print(ex)
            continue


def get_object_info(browser: webdriver.Chrome, object_url: str) -> dict:
    write_log(message=f"Обрабатываем объект {object_url}")
    browser.get(object_url)
    open_all_description(browser=browser)

    bs_object = BeautifulSoup(browser.page_source, "lxml")
    title = bs_object.find(name="title").text.replace("Marketplace -", "").replace("| Facebook", "").strip()
    price = get_price(bs_object=bs_object)
    description = get_description(bs_object=bs_object)
    all_image_urls = get_all_image_urls(bs_object=bs_object)
    main_image_url = all_image_urls[0] if len(all_image_urls) > 0 else ""
    image_urls = all_image_urls[1:]
    option_class = get_option_class(bs_object=bs_object)
    animal_friendly = get_animal_friendly(bs_object=bs_object)
    address = bs_object.find(name="span", class_=option_class).text.strip()
    date_of_publication = get_date_of_publication(bs_object=bs_object, option_class=option_class)
    rating = get_rating(bs_object=bs_object)
    chat_to_author_url = get_chat_to_author_url(bs_object=bs_object)
    author_date_of_registration = get_author_date_of_registration(bs_object=bs_object)

    object_info = {
        "title": title,
        "price": price,
        "object_url": object_url,
        "description": description,
        "animal_friendly": animal_friendly,
        "address": address,
        "date_of_publication": date_of_publication,
        "rating": rating,
        "chat_to_author_url": chat_to_author_url,
        "author_date_of_registration": author_date_of_registration,
        "relevance": "listing is available",
        "main_image_url": main_image_url,
        "image_urls": image_urls,
    }

    return object_info


def check_valid_object(description: str) -> bool:
    if len(filter_words) == 0:
        return True
    for filter_word in filter_words:
        if filter_word.lower() in description.lower():
            return True
    return False


def open_all_description(browser: webdriver.Chrome) -> None:
    bs_object = BeautifulSoup(browser.page_source, "lxml")
    description = bs_object.find(name="div", class_="xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a").text
    check = "See more" in description
    while check:
        click_on_see_more(browser=browser)
        bs_object = BeautifulSoup(browser.page_source, "lxml")
        description = bs_object.find(name="div", class_="xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a").text
        check = description.endswith("See more")


def click_on_see_more(browser: webdriver.Chrome) -> None:
    try:
        show_all_description = browser.find_elements(By.TAG_NAME, "span")
        for el in show_all_description:
            if el.text == "See more":
                browser.execute_script("arguments[0].click();", el)
                time.sleep(2)
                break
    except Exception as ex:
        print(f"[ERROR] {ex}")
        pass


def get_price(bs_object: BeautifulSoup) -> str:
    possible_price_tag_classes = ["x1anpbxc", "x1xmf6yo"]
    for possible_price_tag_class in possible_price_tag_classes:
        price_tag = bs_object.find(name="div", class_=possible_price_tag_class)
        if price_tag is not None:
            price = price_tag.text.strip()
            return price
    return "Not Found"


def get_description(bs_object: BeautifulSoup) -> str:
    dirt_description = bs_object.find(name="div", class_="xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a").text
    description = dirt_description.replace("See less", "").replace("See translation", "") \
        .replace("[hidden information]", "").replace("See more", "").strip()
    return description


def get_all_image_urls(bs_object: BeautifulSoup) -> list:
    image_block_tag = bs_object.find(name="div", class_="x1a0syf3 x1ja2u2z")
    image_tags = image_block_tag.find_all(name="img")
    image_urls = [image_tag["src"] for image_tag in image_tags]
    return image_urls


def get_option_class(bs_object: BeautifulSoup) -> str:
    possible_option_class_variants = [
        "x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso "
        "x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h",

        "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty "
        "x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"
    ]
    for possible_option_class in possible_option_class_variants:
        check = bs_object.find(name="span", class_=possible_option_class)
        if check is not None:
            option_class = possible_option_class
            return option_class


def get_animal_friendly(bs_object: BeautifulSoup) -> str:
    text_content_of_bs_object = bs_object.text
    possible_animal_friendly_variants = ["Dog and cat friendly", "Cat friendly", "Dog friendly"]
    for possible_animal_friendly in possible_animal_friendly_variants:
        if possible_animal_friendly in text_content_of_bs_object:
            return possible_animal_friendly
    return "No friendly"


def get_date_of_publication(bs_object: BeautifulSoup, option_class: str) -> str:
    all_spans = bs_object.find_all(name="span", class_=option_class)
    for span in all_spans:
        if 'Listed' in span.text:
            date_of_publication = span.text
            return date_of_publication
    return "No information"


def get_rating(bs_object: BeautifulSoup) -> int:
    all_aria_label_divs = bs_object.find_all(name="div", attrs={"aria-label": True})
    for aria_label_div in all_aria_label_divs:
        if "rating" in aria_label_div["aria-label"]:
            rating = aria_label_div["aria-label"].split(" ")[0]
            return rating
    return 0


def get_chat_to_author_url(bs_object: BeautifulSoup) -> str:
    author_id = get_author_id(bs_object=bs_object)
    chat_to_author_url = f"https://www.facebook.com/messages/t/{author_id}/"
    return chat_to_author_url


def get_author_id(bs_object: BeautifulSoup) -> str:
    bs_object_string = str(bs_object)
    user_id_string_start_index = bs_object_string.find('"user_id":')
    bs_object_string_from_user_id = bs_object_string[user_id_string_start_index:]
    user_id_string_final_index = bs_object_string_from_user_id.find(',')
    user_id_string = bs_object_string_from_user_id[:user_id_string_final_index]
    author_id = user_id_string.replace('"', "").replace(":", "").replace("user_id", "")
    return author_id


def get_author_date_of_registration(bs_object: BeautifulSoup) -> str:
    str_bs_object = str(bs_object)
    start_index = str_bs_object.find("Joined Facebook in")
    str_bs_object_from_correct_start = str_bs_object[start_index:]
    end_index = str_bs_object_from_correct_start.find("</span>")
    possible_author_date_of_registration = str_bs_object_from_correct_start[:end_index]
    if "Joined Facebook in" in possible_author_date_of_registration:
        author_date_of_registration = possible_author_date_of_registration.replace("<!-- -->", "")
        return author_date_of_registration
    author_date_of_registration = "No information"
    return author_date_of_registration


if __name__ == "__main__":
    run()
