import os
from typing import Dict

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from webdriver_manager.opera import OperaDriverManager

from rosreestr_order.page import PageEgrn1_step1, PageEgrn1_step2, PageEgrn1_step3, PageEgrn1_step4, \
    PageEgrn1_step5
from .order_file import OrderFileXlsx


class Customer:
    """
    Конечный автомат заказывающий выписки, о зем. уч. на сайте Росреестра

    Важно:
    Нормальная работа только с Opera браузер
    # Росреестр не поддерживает Firefox или наоброт
    # С Chrome и IE тоже какие-то проблемы

    """

    url: str = "https://rosreestr.gov.ru/wps/portal/p/cc_present/EGRN_1"
    browsers_driver: Dict[str, RemoteWebDriver] = {"Firefox": webdriver.Firefox,
                                                   "Chrome": webdriver.Chrome,
                                                   "Opera": webdriver.Opera,
                                                   "Ie": webdriver.Ie}
    drivers_name: Dict[str, str] = {"Firefox": "geckodriver",
                                    "Chrome": "chromedriver",
                                    "Opera": "operadriver",
                                    "Ie": "IEDriverServer"}

    # Профиль текущего пользователя используется чтобы использовать расширения для авто заполнения форм
    profile: Dict[str, str] = {"Opera": f"C:/Users/{os.getlogin()}/AppData/Roaming/Opera Software/Opera Stable"}

    def __init__(self, browser: str = "Opera"):
        if browser == "Firefox":
            raise ValueError("Сайт Росреестра не совместим с Firefox")
        # TODO: Доработать использование профайла
        if browser == "Opera":
            options = webdriver.ChromeOptions()
            options.add_argument(f'user-data-dir={self.profile["Opera"]}')
            # TODO: Сделать автоматический выбор версии драйвера в зависимости от версии Opera браузер
            executable_path = OperaDriverManager("v.90.0.4430.85", cache_valid_range=365).install()
        else:
            options = None
            # TODO: Перейти на webdriver_manager по всем поддерживаемым браузерам
            executable_path = f'./driver/{self.drivers_name[browser]}'

        self.driver = self.browsers_driver[browser](executable_path=executable_path, options=options)
        self.driver.implicitly_wait(15)  # секунды
        self.driver.get("https://rosreestr.gov.ru/wps/portal/p/cc_present/EGRN_1")
        self.order_file = OrderFileXlsx()
        self.orders = self.order_file.get_orders()

    def run_order(self):
        if not self.orders:
            return

        page_1: PageEgrn1_step1 = PageEgrn1_step1(self.driver)
        page_2: PageEgrn1_step2 = PageEgrn1_step2(self.driver)
        page_3: PageEgrn1_step3 = PageEgrn1_step3(self.driver)
        page_4: PageEgrn1_step4 = PageEgrn1_step4(self.driver)
        page_5: PageEgrn1_step5 = PageEgrn1_step5(self.driver)

        for i, order in enumerate(self.orders):
            print(f"В очереди: {len(self.orders) - i} объект(а,ов)")
            print(f"\tОжидаемое время на обработку: {round((len(self.orders) - i) * 3 / 60, 2)} часов")
            print(f"Попытка заказать выписку на {order.cn}...")
            if i != 0:
                page_5.repeat_order()
            page_1.type_order(order)
            if i == 0:
                input("Заполните первую страницу и нажмите Enter...")
                page_1.type_order(order)
            page_1.next_step()
            if i == 0:
                input("Заполните вторую страницу и нажмите Enter...")
            person_sur_name = page_2.get_person_sur_name()
            page_2.next_step()
            if i == 0:
                input("Заполните третью страницу и нажмите Enter...")
            page_3.next_step()
            page_4.sign(person_sur_name)
            order.__dict__.update(page_5.get_order_details())
            self.order_file.write_order(order)
            print(f"\tУспешно!")
