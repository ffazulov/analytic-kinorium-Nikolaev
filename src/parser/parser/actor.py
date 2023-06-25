from bs4 import BeautifulSoup
from datetime import datetime
import re
from src.parser.models.actor import Actor
from src.parser.models.genre import GenresActor

class ParserActors:
    def __init__(self):
        pass

    def select_ids_actor_in_film(self, html_page) -> dir:
        """
        Функция парсит страницу и возвращает словарь вида {"Режиссёры": ["5223(id actor)", "434342(id actor)"]}
        :return: dir
        """
        soup = BeautifulSoup(html_page, "lxml")

        dir_roles = self.select_roles(soup, "div", "cast-page__amplua-name amplua-name")

        for key, value in dir_roles.items():
            dir_roles[key] = self.select_site_id_actor(value)

        return dir_roles

    def select_roles(self, soup: BeautifulSoup, tag: str, value_class: str) -> dir:
        """
        Функция находит элементы с личностями и их роль в фильме, возвращает словать, ключом которого является их роль и значение это объект, состоящий из актеров
        Функция также подходит для собирания инормации о участии в фильмах для личностей, поэтому был вынесен параметр value_class
        :param soup: BeautifulSoup object
        :return: directory: {"Режиссёр": BeautifulSoup object}
        """
        lst_rows = soup.find_all("div", class_="ref-list clearfix")
        dir_actors = {}
        for row in lst_rows:
            role = row.find(tag, class_=value_class).text
            dir_actors[self.select_row(role, r'\b[А-ЯЁ][а-яё]+\b')] = row

        return dir_actors

    def select_row(self, name: str, pattern: str) -> str:
        """
        Функция достает строку по заданному паттерну для библиотеки re
        :param name: Строка с именем актера
        :param pattern: Строка паттерн для поиска содержимого строки
        :return: str or None
        """
        match = re.search(pattern, name)
        if match:
            return match.group()
        else:
            return None

    def select_site_id_actor(self, soup: BeautifulSoup) -> list:
        """
        Функция возвращает список айдишников актеров, которые учавствовали под переданной параметром ролью
        :param soup: BeautifulSoup object
        :return: list
        """
        names_actors = soup.find_all("a", attrs={"class": "cast-page__link-name link-info-persona-type-persona",
                                                 "data-type": "persona"})
        names_actors = [el["data-id"] for el in names_actors]

        return names_actors

    def select_info_about_actor(self, id_actor: int, html_page) -> Actor:
        """
        Функция собирает информацию о актере, и вызывает функцию, которая начинает сбор информации о фильмах, с которыми взаимодействовал данный актер
        :param: id_actor id актера на сайте(который был выдан сайтом)
        :return: Actor Object
        """
        soup = BeautifulSoup(html_page, "lxml")

        name = self.select_name_actor(soup)

        name_original = self.select_values_under_main_name(soup, "span", "person-page__name-orig")
        birthday = self.select_values_under_main_name(soup, "span", "person-page__birtday")

        box_info = self.select_box_info_actor(soup)
        height = self.select_info_from_boxinfo(box_info, "рост")
        citizenship = self.select_info_from_boxinfo(box_info, "гражданство")
        site_id = id_actor
        time_download = str(datetime.now().date())
        place_birth = self.select_info_from_boxinfo(box_info, "место рождения")
        genre = self.select_info_from_boxinfo(box_info, "жанры")

        dir_films = self.select_roles(soup, "span", "amplua-name__countAll")

        for role, block in dir_films.items():
            dir_films[role] = [(film["data-id"], self.convert_name(film.text)) for film in block.find_all("i", class_="movie-title__text filmList__item-title-link-popup link-info-movie-type-film")]

        genres_actors = self.select_info_about_genre(id_actor, html_page)

        return Actor(name, name_original, birthday, height, citizenship, dir_films, site_id, time_download, place_birth, genre, genres_actors)

    def convert_name(self, name: str):
        res_name = name.replace("\n", "")
        res_name = ' '.join(res_name.split())

        bad_words = ["Пост-продакшн", "Сериал", "Проект объявлен", "В производстве", "Топ-500"]

        for word in bad_words:
            if word in res_name:
                res_name = res_name.replace(word, "")
        return res_name

    def select_name_actor(self, soup: BeautifulSoup) -> str:
        """
        Функция выполняет поиск имени и фамилии персонажа, если ей передали html страницу с каким нибудь человеком
        :param soup: BeautifulSoup object (Желательно, предварительно обработанный функцией select_box_info_actor())
        :return: Возвращает строку вида "Брэд Пит"
        """
        name = soup.find("div", attrs={"class": "person-page__title-elements-wrap", "itemprop": "name"}).text
        return name

    def select_box_info_actor(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Функция возвращает блок с информацией о актере
        :param soup: BeautifulSoup object
        :return: block of actor
        """
        box_info = soup.find("tbody")

        box_info = [row.text for row in box_info.find_all("tr")]
        return box_info

    def select_info_from_boxinfo(self, soup: BeautifulSoup, value: str) -> str or None:
        """
        Функция достает из box info информацию о value, если такая есть, иначе возвращает None
        :param soup: BeautifulSoup object (Желательно, предварительно обработанный функцией select_box_info_actor())
        :return: str or None: Строка вида "1.7 м.", если такой информации нет, то None(value="рост")
        """
        for row in soup:
            if value in row:
                return row
        return None

    def select_values_under_main_name(self, soup: BeautifulSoup, tag: str, value_class: str) -> str or None:
        res = soup.find(tag, class_=value_class)
        if res is not None:
            return res.text
        return None

    def select_info_about_genre(self, id_actor: int, html_page):
        soup = BeautifulSoup(html_page, "lxml")

        genres_rows = soup.find_all("li", class_="user-statistic__chart-item person-page__stats-chart-item")

        dir_genre_actor = {}

        for genre_row in genres_rows:
            if genre_row is not None:
                name_genre = genre_row.text.split()[0]
                percent_genre = genre_row.text.split()[1]
            else:
                continue
            dir_genre_actor[name_genre] = percent_genre

        return GenresActor(id_actor, dir_genre_actor)

    def select_actor_search_page(self, html_page):

        soup = BeautifulSoup(html_page, "lxml")

        box_result_searching = soup.find("div", class_="list search-page__person-list")
        if box_result_searching:
            actor_case = box_result_searching.find_all("div", class_="item")
            if actor_case:
                return actor_case[0].find("div", class_="poster")["rel"]
        return None