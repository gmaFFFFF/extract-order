from dataclasses import dataclass
from time import sleep
from typing import Tuple

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

WAIT_TIME = 20  # секунд
SLEEP_TIME = 2  # секунд


@dataclass()
class BaseElem:
    """
    Элемент на html странице
    """

    locator: Tuple[str, str]
    wait_time = WAIT_TIME

    def __get__(self, instance, owner):
        self.driver = instance.driver
        WebDriverWait(self.driver, self.wait_time).until(expected_conditions.presence_of_element_located(self.locator))
        elem = self.driver.find_element(*self.locator)
        return elem


class Label(BaseElem):
    """
    Метка на html странице
    """

    def __get__(self, instance, owner):
        elem = super().__get__(instance, owner)
        return elem.text if (elem.text is not None and elem.text != "") else elem.get_attribute("value")


class Input(Label):
    """
    Поле ввода на html странице
    """

    def __set__(self, instance, value):
        try:
            self.driver = instance.driver
            cur_val = self.__get__(instance, self.__class__)
            if (cur_val is None or cur_val == "") and (value is None or value == ""):
                return

            if str.strip(str.upper(cur_val)) == str.strip(str.upper(str(value))):
                return

            elem = self.driver.find_element(*self.locator)
            WebDriverWait(self.driver, self.wait_time).until(
                expected_conditions.visibility_of_element_located(self.locator))
            elem.click()
            sleep(SLEEP_TIME)
            elem.clear()
            sleep(SLEEP_TIME)
            # clear не всегда помогает, поэтому "костыль"
            elem.send_keys(Keys.END)
            sleep(SLEEP_TIME)
            elem.send_keys(Keys.CONTROL + Keys.SHIFT + Keys.HOME)
            sleep(SLEEP_TIME / 3)
            elem.send_keys(Keys.DELETE)
            if value is not None:
                elem.send_keys(str(value))

        except Exception as e:
            print(e)


@dataclass()
class ComboBox(Input):
    """
    Поле ввода с выпадающим списком на html странице
    """

    locator_menu: Tuple[str, str]

    def __set__(self, instance, value):
        try:
            self.driver = instance.driver
            elem = self.driver.find_element(*self.locator)
            cur_val = self.__get__(instance, self.__class__)
            super().__set__(instance, value)

            if (cur_val is None or cur_val == "") and (value is None or value == ""):
                return
            if str.strip(str.upper(cur_val)) == str.strip(str.upper(str(value))):
                return
            if value is None:  # После вызова метода суперкласса, т.к. нужно очистить предыдущее значение
                return
            sleep(SLEEP_TIME)
            try:
                locator_menu = (self.locator_menu[0], self.locator_menu[1].format(value))
                WebDriverWait(self.driver, self.wait_time).until(
                    expected_conditions.visibility_of_element_located(locator_menu))
                elem_menu = self.driver.find_element(*locator_menu)
                sleep(SLEEP_TIME)
                elem_menu.click()
            except:
                # elem.send_keys(Keys.DOWN)
                elem.send_keys(Keys.TAB)

        except Exception as e:
            print(e)


class List(BaseElem):
    """
    Выпадающий список на html странице
    """

    def __set__(self, instance, value):
        self.driver = instance.driver
        locator = (self.locator[0], self.locator[1].format(value))
        elem = self.driver.find_element(*locator)
        WebDriverWait(self.driver, self.wait_time).until(expected_conditions.element_to_be_clickable(locator))
        sleep(SLEEP_TIME)
        elem.click()


class Button(BaseElem):
    """
    Кнопка на html странице
    """

    def click(self):
        pass
