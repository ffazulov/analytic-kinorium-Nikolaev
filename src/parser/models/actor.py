import unicodedata
import re

class Actor:
    def __init__(self, name: str, name_original: str, birthday: str, height: float,
                 citizenship: str, films_dir: dir, site_id: int, time_download: str, place_birth: str, genre: str, genre_object: object):
        self.first_name = str(self.select_first_name(name)[0])
        self.last_name = str(self.select_first_name(name)[1])
        self.name_original = name_original
        self.birthday = self.convert_birthday(birthday)
        self.height = self.convert_height(height)
        self.citizenship = self.delete_word(citizenship, "гражданство")
        self.films_dir = self.convert_dir_films(films_dir)
        self.site_id = int(site_id)
        self.time_download = time_download
        self.place_birth = self.delete_word(place_birth, "место рождения")
        self.genre = self.delete_word(genre, "жанры")
        self.genres_percent = genre_object

    def convert_dir_films(self, dir_films):
        dir_res = {}
        for role, films_ids in dir_films.items():
            dir_res[self.convert_role(role)] = films_ids
        return dir_res

    def convert_birthday(self, birthday: str):
        """
        Так как может поступать строка вида "3 апреля 1924 — 1 июля 2004",
        функция иключает вариант событий, когда человек умирает и возраст актера продалжает расти
        :param birthday: строка
        :return: строка вида "1924"
        """
        if birthday is not None:
            birthday = unicodedata.normalize("NFKD", birthday)
            birthday = (' ').join(birthday.split())
            date = re.findall(r'\b\d{4}\b', birthday)
            if date:
                return int(date[0])
        return None

    def select_first_name(self, name):
        """
        Функция достает имя и фамилию из передананой строки
        :param name: "Брэд Пит"
        :return: ["Брэд", "Пит"]
        """
        return name.split()

    def convert_height(self, height):
        pattern = r"\d+\.\d+"
        if height is None:
            return None
        result = re.search(pattern, height)
        if result:
            return float(result.group())
        else:
            return None

    def delete_word(self, row, word):
        if row is None:
            return None
        res = row.replace(word, "")
        res = str(res)
        res = res.strip()
        return res

    def convert_role(self, role):
        if "Акт" in role:
            return "Актер"
        elif "Режис" in role:
            return "Режиссер"
        elif "Сцен" in role:
            return "Сценарист"
        return role

    def return_info_tbl_actors(self):
        return [self.first_name, self.last_name, self.name_original, self.birthday, self.height, self.citizenship, self.site_id, self.time_download, self.place_birth, self.genre]

    def __str__(self):
        return f"Имя: {self.first_name}, Фамилия: {self.last_name}, Рост: {self.height}, Гражданство: {self.citizenship}, Фильмs: {self.films_dir}"