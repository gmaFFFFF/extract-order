"""
Абстракиция пользовательких шагов для заказа выписок о зем. уч. на сайте Росреестра
"""

import typing
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from core.order_file import Order
from .elements import BaseElem, Button, ComboBox, Label, List, Input, SLEEP_TIME
from .locators import *


@dataclass()
class PageEgrn1:
    driver: RemoteWebDriver

    def is_cur_page(self):
        try:
            _ = self.header
        except NoSuchElementException:
            return False
        except:
            return False
        else:
            return True

    @classmethod
    def get_pages_classes(cls) -> typing.OrderedDict[int, typing.Any]:
        return OrderedDict([(1, PageEgrn1_step1),
                            (2, PageEgrn1_step2),
                            (3, PageEgrn1_step3),
                            (4, PageEgrn1_step4),
                            (5, PageEgrn1_step5),
                            ])

    def get_currnt_page(self):
        pages = [c(self.driver) for c in self.__class__.get_pages_classes().values()]
        page = p[0] if (p := [page for page in pages if page.is_cur_page()]) else None
        return page

    def refresh(self):
        self.driver.refresh()
        sleep(SLEEP_TIME)


@dataclass()
class PageEgrn1_outOfSync(PageEgrn1):
    header = Label(LocatorEgrn1_outOfSync.header_label)
    header.wait_time = 1
    button_resync = Button(LocatorEgrn1_outOfSync.resync_button)

    def resync(self):
        self.button_resync.click()
        sleep(SLEEP_TIME)


def resync_if_necessary(page: PageEgrn1):
    sync_panel: PageEgrn1_outOfSync = PageEgrn1_outOfSync(page.driver)
    if sync_panel.is_cur_page():
        sync_panel.resync()


@dataclass()
class PageEgrn1_step1(PageEgrn1):
    header = Label(LocatorEgrn1_step1.header_label)
    type_obj = ComboBox(LocatorEgrn1_step1.type_obj_input, LocatorEgrn1_step1.combobox_list_pattern)
    cn = Input(LocatorEgrn1_step1.cn_input)
    area = Input(LocatorEgrn1_step1.area_input)
    area_unit = ComboBox(LocatorEgrn1_step1.area_unit_input, LocatorEgrn1_step1.combobox_list_pattern)
    region = ComboBox(LocatorEgrn1_step1.region_input, LocatorEgrn1_step1.combobox_list_pattern)
    district = ComboBox(LocatorEgrn1_step1.district_input, LocatorEgrn1_step1.combobox_list_pattern)
    button_next = Button(LocatorEgrn1_step1.next_button)

    def type_order_parcel(self, order: Order):
        while (self.type_obj != 'Земельный участок' or
               self.cn != order.cn or
               self.area != str(order.area) or
               self.area_unit != 'Квадратный метр' or
               self.region != order.region or
               (self.district != order.district and order.district is not None)):
            resync_if_necessary(self)
            self.type_obj = 'Земельный участок'
            self.cn = order.cn
            self.area = order.area
            # Если при вводе сведений об очередном земельном участке не меняется регион и район его нахождения,
            # то перед нажатием кнопки "Перейти к сведениям о заявителе", курсор ввода находится внутри поля "Площадь".
            # Когда программа нажимет кнопку сайт Росреестра иногда сбрасывает площадь на пустое значение и не переходит
            # на следующую страницу. Программа этого не понимает и прекращает выполнение.
            # Поэтому перед нажатием кнопки лучше перейти на следующее поле.
            # TODO: Переделать в специализированную версию класса input
            b = BaseElem(LocatorEgrn1_step1.area_input)
            b.__get__(self, b.__class__).send_keys(Keys.TAB)

            self.area_unit = 'Квадратный метр'
            self.region = order.region
            self.district = order.district

    def next_step(self):
        resync_if_necessary(self)
        self.button_next.click()
        sleep(SLEEP_TIME)


@dataclass()
class PageEgrn1_step2(PageEgrn1):
    header = Label(LocatorEgrn1_step2.header_label)
    person_sur_name = Input(LocatorEgrn1_step2.person_sur_name)
    button_next = Button(LocatorEgrn1_step2.next_button)

    def next_step(self):
        resync_if_necessary(self)
        self.button_next.click()
        sleep(SLEEP_TIME)

    def get_person_sur_name(self):
        resync_if_necessary(self)
        return self.person_sur_name


@dataclass()
class PageEgrn1_step3(PageEgrn1):
    header = Label(LocatorEgrn1_step3.header_label)
    button_next = Button(LocatorEgrn1_step3.next_button)

    def next_step(self):
        resync_if_necessary(self)
        self.button_next.click()
        sleep(SLEEP_TIME)


@dataclass()
class PageEgrn1_step4(PageEgrn1):
    header = Label(LocatorEgrn1_step4.header_label)
    button_next = Button(LocatorEgrn1_step4.next_button)
    cert_user = List(LocatorEgrn1_step4.cert_user_pattern)
    button_sign = Button(LocatorEgrn1_step4.sign_button)

    def sign(self, user: str):
        resync_if_necessary(self)
        self.button_next.click()
        sleep(SLEEP_TIME)
        self.cert_user = user
        self.button_sign.click()
        sleep(SLEEP_TIME)


@dataclass()
class PageEgrn1_step5(PageEgrn1):
    header = Label(LocatorEgrn1_step5.header_label)
    order_num = Label(LocatorEgrn1_step5.order_num_text)
    order_code = Label(LocatorEgrn1_step5.order_code_text)
    order_date = date.today()
    button_repeat = Button(LocatorEgrn1_step5.repeat_button)

    def get_order_details(self) -> dict:
        return {"order_num": self.order_num,
                "order_code": self.order_code,
                "order_date": self.order_date}

    def repeat_order(self):
        resync_if_necessary(self)
        self.button_repeat.click()
        sleep(SLEEP_TIME)
