from src.parser.crawller.base import Crawller
from fake_useragent import UserAgent
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from src.parser.parser.film import ParserFilms
import time
from selenium.webdriver.common.by import By
import traceback


class CrawllerFilms(Crawller):
    def __init__(self):
        self.useragent = UserAgent()
        self.options = webdriver.ChromeOptions()
        self.service = Service(r"/Chromedriver/chromedriver.exe")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        self.parser = ParserFilms()

    def start_crawling(self, result_films):
        """
        Запускается процесс краулинга фильмов:
        проходит по топ-фильмам на странице и собирает информацию о фильмах
        :return:None
        """
        try:
            page = 1
            while True:
                self.add_useragent()
                self.driver.get(f"https://ru.kinorium.com/R2D2/?order=rating&page={page}")

                self.waiting_for_element(10, By.CLASS_NAME, "filmList__item-content")
                time.sleep(7)

                source_page = self.driver.page_source
                ids = self.parser.select_id_top_films(source_page)
                self.forward_to_films(ids, result_films)

                page += 1
                if page == 8:
                    break
        except Exception:
            print(traceback.format_exc())
        finally:
            print("Работа Краулера фильмов окончена корректна.")

    def forward_to_films(self, ids: list, result_films: list):
        """
        Переходит к каждому фильму,
        которые передались параментором ids и вызывает функцию select_info_of_film() у объекта Парсера,
        которая возвращает обьект Film и добавляет объект в список фильмов,
        :param ids: list
        :return: None
        """
        for id in ids:
            self.driver.get(f"https://ru.kinorium.com/{id}/")

            self.waiting_for_element(10, By.CLASS_NAME, "film-page__infowrap")
            time.sleep(7)

            source_page = self.driver.page_source
            film = self.parser.select_info_of_film(source_page, id)
            result_films.append(film)
            break

    def __del__(self):
        self.driver.close()
        self.driver.quit()

        print("Работа Краулера фильмов окончена.")