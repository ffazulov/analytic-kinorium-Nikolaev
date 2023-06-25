from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Crawller:
    def add_useragent(self):
        """
        Добавляет user-agent к драйверу
        :return: None
        """
        self.options.add_argument(f"user-agent={self.useragent.random}")

    def waiting_for_element(self, seconds: int, tag: By, value_tag: str):
        """
        Функция выполняет процесс ожидания элемента по заданным параметрам
        :param seconds: Сколько секунд ожидать
        :param tag: По какому тегу ожидать элемент(By.ID)
        :param value_tag: Значение тега
        :return: None
        """
        element = WebDriverWait(self.driver, seconds).until(EC.presence_of_element_located((tag, value_tag)))