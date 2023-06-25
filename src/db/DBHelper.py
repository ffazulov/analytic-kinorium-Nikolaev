import sqlite3
class DBHelper:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        placeholders = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({placeholders})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_data(self, table_name, values, columns, ignore=False):
        placeholders = ", ".join("?" * len(values))
        if ignore:
            ignore = 'OR IGNORE'
        else:
            ignore = ''
        query = f"INSERT {ignore} INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_data(self, select: str, table_name, conditions=None, joins=None):
        query = f"SELECT {select} FROM {table_name}"
        if joins:
            query += joins
        if conditions:
            query += f" WHERE {conditions}"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def delete_data(self, table_name, conditions=None):
        query = f"DELETE FROM {table_name}"
        if conditions:
            query += f" WHERE {conditions}"
        self.cursor.execute(query)
        self.conn.commit()

    def fetch_films_id(self):
        '''
        Функция достает из базы данных список id фильмов, которые уже есть в базе
        :return: list of id
        '''
        query = "SELECT site_id FROM about_films"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        lst = [i[0] for i in rows]
        return lst

    def create_tables(self):
        self.create_table("actors", ["first_name TEXT",
                                     "last_name TEXT",
                                     "name_original TEXT",
                                     "birthday INTEGER",
                                     "height FLOAT",
                                     "citizenship TEXT",
                                     "site_id INTEGER PRIMARY KEY",
                                     "time_download TEXT",
                                     "place_birth TEXT",
                                     "genre TEXT"])

        self.create_table("genre", ["id INTEGER PRIMARY KEY AUTOINCREMENT",
                                    "name_genre TEXT",
                                    "percent REAL",
                                    "actor_id INTEGER",
                                    "FOREIGN KEY (actor_id)  REFERENCES actors (id)"])

        self.create_table("role", ["id INTEGER PRIMARY KEY AUTOINCREMENT",
                                   "name_role TEXT UNIQUE"])

        self.create_table("about_films", ["name_film TEXT",
                                          "country TEXT",
                                          "budget INTEGER",
                                          "duration integer",
                                          "site_id INTEGER PRIMARY KEY",
                                          "time_download TEXT"])

        self.create_table("films", ["site_id PRIMARY KEY",
                                    "name_film TEXT"])

        self.create_table("removed", ["actor_site_id INTEGER",
                                      "film_site_id INTEGER",
                                      "role_id INTEGER",
                                      "FOREIGN KEY (actor_site_id)  REFERENCES actors (site_id)",
                                      "FOREIGN KEY (film_site_id)  REFERENCES films (site_id)",
                                      "FOREIGN KEY (role_id)  REFERENCES role (id)"])

    def check_actor(self, actor):
        first_name = actor.split()[0]
        second_name = actor.split()[1]

        condition = f"WHERE actors.first_name = {first_name} and actors.second_name = {second_name}"
        request = f"SELECT EXISTS(SELECT * FROM removed {condition})"

        res = self.cursor.fetchall(request)

        if res:
            return True
        else:
            return False

    def fetch_roles_actor(self, actor, condition_user, depth):
        mass = self.basic(actor, condition_user, depth)
        result_relations = self.convert_relations(mass)
        # print(result_relations)
        res = self.unique_el_in_list(result_relations)
        # print(res)
        res = self.convert_mass_relations(res)
        # print(res)

        return res

    def fetch_all_roles(self):
        roles = self.fetch_data("name_role", "role")
        roles = [i[0] for i in roles]
        return roles

    def convert_mass_relations(self, mass):
        res_dir = {}
        for row in mass:
            actor = row[0]
            film = row[1]
            role = row[2]

            if (actor, role) in res_dir:
                res_dir[(actor, role)].append(film)
            else:
                res_dir[(actor, role)] = [film]
        return res_dir


    def basic(self, actor, condition_user, depth=1):
        """
        Функция достает из базы те записи актера, которые подходят к актеру
        :param actor: str
        :return: list: вида ["Бред", "Питт", "Актер", "Бойцовский клуб"]
        """
        first_name = actor.split()[0]
        last_name = actor.split()[1]

        result_rows = []

        condition = f"actors.first_name='{first_name}' and actors.last_name='{last_name}'"
        join = " JOIN removed ON actors.site_id=removed.actor_site_id JOIN role ON role.id=removed.role_id JOIN films ON films.site_id=removed.film_site_id"
        rows = self.fetch_data("DISTINCT actors.first_name, actors.last_name, role.name_role, films.name_film", "actors", condition, join)
        rows = self.unique_el_in_list(rows)

        for row in rows:
            result_rows.append(row)

            name_film = row[-1]
            lst_another_actors = self.fetch_another_actor(name_film, condition_user)
            lst_another_actors = self.unique_el_in_list(lst_another_actors)
            result_rows = self.merge_lists(result_rows, lst_another_actors)

            if depth > 1:
                for el in lst_another_actors:
                    all_actors = self.basic(el[0]+" "+el[1], condition_user, depth-1)
                    all_actors = self.unique_el_in_list(all_actors)
                    result_rows = self.merge_lists(result_rows, all_actors)

        result_rows = self.unique_el_in_list(result_rows)
        return result_rows

    def unique_el_in_list(self, lst):
        res = []
        for el in lst:
            if el not in res:
                res.append(el)
        return res

    def merge_lists(self, array_one, array_two):
        for row in array_two:
            if row not in array_one:
                array_one.append(row)
        return array_one

    def convert_relations(self, mass_relations: list):
        """
        Функция обрабатывает каждую строку, а так же сливает вместе имя и фамилию
        :param mass_relations:
        :return:
        """
        result_rows = []
        for row in mass_relations:
            name_actor = row[0]+" "+row[1]
            name_film = row[-1]
            role = row[2]
            row_relation = [name_actor, name_film, role]
            result_rows.append(row_relation)
        return result_rows

    def fetch_another_actor(self, name_film: str, condition=None):
        """
        Функция достает список актеров, которые подходят под условие, что они снимались в заданном фильме,
         создана для использования после функции fetch_roles_actor
        :return list: вида ["Бред", "Питт", "Актер", "Бойцовский клуб"]
        """
        name_film = name_film.replace("'", "''")

        condition_basic = f"films.name_film = '{name_film}' "
        if condition:
            condition_basic += condition

        join = " JOIN removed ON actors.site_id=removed.actor_site_id JOIN role ON role.id=removed.role_id JOIN films ON films.site_id=removed.film_site_id"
        rows = self.fetch_data("DISTINCT actors.first_name, actors.last_name, role.name_role, films.name_film", "actors", condition_basic, join)
        return rows

    def save_film_to_db(self, film):
        self.insert_data('about_films', film.return_info(), ["name_film", "country", "budget", "duration", "site_id", "time_download"], ignore=True)

    def save_genre_to_db(self, actor):
        for genre, percent in actor.genres_percent.dir_relation_genre.items():
            self.insert_data('genre', [actor.genres_percent.actor_id, genre, percent],
                                      ["actor_id", "name_genre", "percent"])

    def save_actor_to_db(self, actor):
        """
        Запускает процесс сохранения actors в БД
        :return: None
        """
        self.insert_data('actors', actor.return_info_tbl_actors(), ["first_name",
                        "last_name",
                        "name_original",
                        "birthday",
                        "height",
                        "citizenship",
                        "site_id",
                        "time_download",
                        "place_birth",
                        "genre"], ignore=True)

        for role, films_ids in actor.films_dir.items():
            role_id = self.save_role_select_role_id(role)
            for film_site_id in films_ids:
                self.insert_data("removed", [actor.site_id, film_site_id[0], role_id],
                                 ["actor_site_id", "film_site_id", "role_id"])
                self.insert_data("films", [film_site_id[0], film_site_id[1]],
                                 ["site_id", "name_film"], ignore=True)

        self.save_genre_to_db(actor)

    def save_role_select_role_id(self, role):
        self.insert_data("role", [role], ["name_role"], ignore=True)
        id = self.fetch_data("*", "role", conditions=f"role.name_role = \'{role}\'")[0][0]
        return id

    def close(self):
        self.conn.close()