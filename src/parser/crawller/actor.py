from src.parser.crawller.base import Crawller
from fake_useragent import UserAgent
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from src.parser.parser.actor import ParserActors
import time
from selenium.webdriver.common.by import By
import traceback


class CrawllerActors(Crawller):
    def __init__(self):
        self.useragent = UserAgent()
        self.options = webdriver.ChromeOptions()
        self.service = Service(r"/Chromedriver/chromedriver.exe")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.parser = ParserActors()

    def start_crawling(self, ids_from_db, result_actors: list):
        try:
            i=0
            for id in ids_from_db:
                i+=1
                self.get_page_actor(id)

                self.waiting_for_element(15, By.CLASS_NAME, "cast-page__item")
                time.sleep(8)

                dir_actors = self.parser.select_ids_actor_in_film(self.driver.page_source)

                result_actors = self.crawling_on_one_person(dir_actors, result_actors)
        except Exception:
            print(traceback.format_exc())
        finally:
            print("Работа Краулера актеров окончена корректно.")
            return result_actors

    def crawling_on_one_person(self, dir_actors: dir, result_actors: list):
        """
                Функция запускает цикл сбора информации об актерах, которые были переданы своими айдишниками
                :param dir_actors:
                :return:
                """
        for role, ids_actors in dir_actors.items():
            for id in ids_actors:
                self.add_useragent()
                self.driver.get(f"https://ru.kinorium.com/name/{id}/")

                self.waiting_for_element(15, By.CLASS_NAME, "person_info")
                time.sleep(7)

                actor = self.parser.select_info_about_actor(id, self.driver.page_source)

                result_actors.append(actor)

                # break
            # break
        return result_actors

    def get_page_actor(self, id: str) -> None:
        """
        Функция переходит в раздел страницы актеров
        :param: id: Id фильма, с которого требуется собрать информацию о актерах
        :return: None
        """
        self.driver.get(f"https://ru.kinorium.com/{id}/cast/")

    def start_search(self, actor: str):
        try:
            self.get_search_page_actor(actor)

            # self.waiting_for_element(15, By.CLASS_NAME, "list search-page__person-list")
            time.sleep(5)

            id_actor = self.parser.select_actor_search_page(self.driver.page_source)

            if id_actor:
                return self.crawling_person(id_actor)
            else:
                print("Введите повторно актера, заданного актера не получается найти на сайте")
        except Exception:
            print(traceback.format_exc())
        finally:
            print("Работа ReКраулера актеров окончена корректно.")

    def crawling_person(self, id_actor: str):
        self.driver.get(f"https://ru.kinorium.com/name/{id_actor}/")

        # self.waiting_for_element(15, By.CLASS_NAME, "person_info")
        time.sleep(7)

        actor = self.parser.select_info_about_actor(id_actor, self.driver.page_source)

        return actor

    def get_search_page_actor(self, actor: str):
        self.driver.get(f"https://ru.kinorium.com/search/?q={actor}")

    def __del__(self):
        self.driver.close()
        self.driver.quit()

        print("Работа Краулера актеров окончена.")