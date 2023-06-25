from src.parser.crawller.film import CrawllerFilms
from src.parser.crawller.actor import CrawllerActors
from src.db.DBHelper import DBHelper


class ControllerParser:
    def __init__(self):
        self.db = DBHelper("Data_of_films_and_actors.db")
        self.crawller_films = CrawllerFilms()
        self.crawller_actors = CrawllerActors()
        self.films = []
        self.actors = []

    def download_top_films(self):
        self.crawller_films.start_crawling(self.films)

    def download_actors(self):
        ids = self.db.fetch_films_id()

        actor = self.crawller_actors.start_crawling(ids, self.actors)

        self.actors = actor

    def create_database(self) -> None:
        """Создает таблицы в локальной базе данных"""
        self.db.create_tables()

    def save_films(self):
        for film in self.films:
            self.db.save_film_to_db(film)

    def save_actors(self):
        for actor in self.actors:
            self.db.save_actor_to_db(actor)

    def redownload_actors(self, actor_name: str):
        actor = self.crawller_actors.start_search(actor_name)
        self.actors.append(actor)
        self.save_actors()


    def __del__(self):
        self.db.close()
        print("Соединение с базой данных закрыто.")

if __name__ == "__main__":
    controller_p = ControllerParser()
    controller_p.create_database()

    controller_p.download_top_films()
    controller_p.save_films()

    controller_p.download_actors()
    controller_p.save_actors()
    # controller_p.redownload_actors("Фрэнк Дарабонт")