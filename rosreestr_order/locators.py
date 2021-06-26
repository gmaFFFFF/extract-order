"""
Основные поисковые индексы - локаторы (xpath или css selector) элементов html страницы при заказе выписок из ЕГРН на зу
"""

from selenium.webdriver.common.by import By


class LocatorEgrn1_step1:
    _input_xpath_1 = "(// div[contains(text(), 'Площадь:')] /../../../../../../../../../../..// input)"
    _input_xpath_2 = "//div[contains(text(),'Регион:')]/../../../../../../../../../../.."
    _menu_xpath = "//td[contains(@class,'gwt-MenuItem')]/span[contains(text(),'{0}')]"

    header_label = (By.XPATH, "//div[@innertext='1. Детали запроса (шаг 1 из 4)']")
    combobox_list_pattern = (By.XPATH, _menu_xpath)
    type_obj_input = (By.XPATH, "//div[contains(text(),'Тип объекта:')]/../../../../../../../../../../..//input")
    cn_input = (By.XPATH, "//div[contains(text(),'Кадастровый номер:')]/../../../../../../../../../../..//input")
    area_input = (By.XPATH, f"{_input_xpath_1}[1]")
    area_unit_input = (By.XPATH, f"{_input_xpath_1}[2]")

    region_input = (By.XPATH, f"{_input_xpath_2}//input")
    district_input = (By.XPATH, f"({_input_xpath_2}/following-sibling::node()//input)[1]")
    next_button = (By.XPATH, "//span[contains(text(),'Перейти к сведениям о заявителе')]/../..")


class LocatorEgrn1_step2:
    header_label = (By.XPATH, "//div[@innertext='2. Сведения о заявителе или его представителе (шаг 2 из 4)']")
    person_sur_name = (By.XPATH, "//div[contains(text(),'Фамилия:')]/../../../../../../../../../../..//input")
    next_button = (By.XPATH, "//span[contains(text(),'Перейти к прилагаемым к запросу документам')]/../..")


class LocatorEgrn1_step3:
    header_label = (By.XPATH, "//div[@innertext='3. Прилагаемые документы (шаг 3 из 4)']")
    next_button = (By.XPATH, "//span[contains(text(),'Перейти к проверке данных')]/../..")


class LocatorEgrn1_step4:
    _cert_list_xpath = "//div[contains(@class,'CertificateListDialog')]"

    header_label = (By.XPATH, "//div[@innertext='4. Проверка введённых данных (шаг 4 из 4)']")
    next_button = (By.XPATH, "//span[contains(text(),'Подписать и отправить запрос')]/../..")
    cert_user_pattern = (By.XPATH,
                         f"{_cert_list_xpath}//td[contains(@class,'subject')]" "[contains(text(),'{0}')]")
    sign_button = (By.XPATH, f"{_cert_list_xpath}//button[contains(text(),'Подписать')]")


# TODO: Закончить
class LocatorEgrn1_step5:
    header_label = (By.XPATH, "//div[contains(text(),'Ваш запрос зарегистрирован. Номер запроса: ')]")
    order_num_text = (By.XPATH, "//div[contains(text(),'Номер запроса: ')]/b")
    order_code_text = (By.XPATH, "//div//following-sibling::text()[contains(.,'код')]/following-sibling::b")
    repeat_button = (By.XPATH, "//span[contains(text(),'Сформировать еще один запрос')]/../..")


# TODO: Нужно тестировать рассинхрон
class LocatorEgrn1_outOfSync:
    test_script = """
    return (document.evaluate("count(//*[text()='Out of sync'])", document, null, XPathResult.ANY_TYPE, null)
    .numberValue>0)"""
    header_label = (By.XPATH, "//*[text()='Out of sync']")
    resync_button = (By.PARTIAL_LINK_TEXT, "click here")
