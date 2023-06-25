class GenresActor:
    def __init__(self, actor_id: int, dir_relation_genre: dir):
        self.actor_id = actor_id
        self.dir_relation_genre = self.convert_percent_dir(dir_relation_genre)

    def convert_percent_dir(self, dir_relation_genre: dir):
        for genre, percent in dir_relation_genre.items():
            dir_relation_genre[genre] = self.convert_percent(percent)
        return dir_relation_genre

    def convert_percent(self, percent: str):
        if percent is not None:
            percent = float(percent.replace("%", ""))
            percent = percent/100
            return percent
        else:
            return None