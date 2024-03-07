import asyncio
import re
import sys
import unicodedata
from pathlib import Path

import httpx
import win32com.client
from httpx import Timeout, ReadTimeout, HTTPStatusError
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type

# Решение проблемы с вылетом с ошибкой Asyncio Event Loop is Closed
# https://github.com/encode/httpx/issues/914#issuecomment-622586610
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def slugify(value, allow_unicode=True):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def get_result_num_and_ref(mail_body: str) -> dict[str, str]:
    num_pattern_str = r"(?<=по запросу № ).+(?=\.)"
    ref_pattern_str = r'(?<=перейдите HYPERLINK ").+(?=")'

    # создаем аналог статического переменной для хранения скомпированного регулярного выражения
    if not hasattr(get_result_num_and_ref, "num_pattern"):
        get_result_num_and_ref.num_pattern = re.compile(num_pattern_str)
        get_result_num_and_ref.ref_pattern = re.compile(ref_pattern_str)

    # Чтобы не писать много букв создаем псевдонимы
    num_pattern = get_result_num_and_ref.num_pattern
    ref_pattern = get_result_num_and_ref.ref_pattern

    num = num_pattern.search(mail_body).group(0)
    ref = ref_pattern.search(mail_body).group(0)

    return {num: ref}


def find_new_rosreestr_result_mail(filter_subj: str = 'Уведомление о завершении обработки запроса',
                                   filter_sender='noreply-site@rosreestr.ru') -> list:
    outlook = win32com.client.Dispatch("Outlook.Application")
    explorer = outlook.ActiveExplorer()
    folder = explorer.CurrentFolder
    items = folder.Items
    filter_str = "[Unread]=true" \
                 f" AND [SenderEmailAddress]='{filter_sender}'" \
                 f" AND [Subject]='{filter_subj}'"
    filter_items = items.Restrict(filter_str)
    mails = [i for i in filter_items if i.Class == 43]
    return mails


async def download(client: httpx.AsyncClient, extract: tuple, file_path: Path):
    max_attempt = 21
    num, url = extract

    print(f"Запрашивается выписка № {num}")
    try:
        with file_path.open('wb') as file:
            async for attempt in AsyncRetrying(stop=stop_after_attempt(max_attempt)
                    , wait=wait_exponential(multiplier=1, max=180)
                    , retry=retry_if_exception_type((ReadTimeout, HTTPStatusError))
                    , reraise=True
                    , before_sleep=lambda state: print(
                        f"Попытка № {state.attempt_number} скачать выписку № {num} не удалась. "
                        f"Следующая через {state.idle_for:0.0f} сек")):
                with attempt:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_bytes():
                            file.write(chunk)

                        if response.is_error:
                            file.truncate(0)
                            response.raise_for_status()
                        print(f"Выписка № {num} получена. Результат записан в файл {file_path}")

    except ReadTimeout as e:
        print(f"\nВыписку № {num} скачать не удалось, так как ожидание ответа "
              f"от сервера Росреестра превысило разумное время ({client.timeout.read} сек.). \n"
              f"Повторите попытку позже.")
        file_path.unlink(True)
        return num, False
    except Exception as e:
        print(f"Ошибка при скачивании выписки № {num}. Попробуйте в другой раз.")
        file_path.unlink(True)
        return num, False
    else:
        return num, True


async def downloads_all(extract: dict[str, str], target_folder: Path = Path('.')):
    async with httpx.AsyncClient(timeout=Timeout(60), verify=False) as client:
        targets = {num: target_folder / f"{slugify(num)}.zip" for num in extract.keys()}
        aws = (download(client, (num, url), targets[num]) for num, url in extract.items())
        L = await asyncio.gather(*aws)
        return L


def run_download(target_dir: Path = Path("./download")):
    p = Path(target_dir)
    p.mkdir(exist_ok=True)

    mails = find_new_rosreestr_result_mail()
    extracts = {k: v for mail in mails
                for k, v in get_result_num_and_ref(mail.Body).items()}

    result = asyncio.run(downloads_all(extracts, target_dir))
    success = [num for num, status in result if status is True]
    unread_mails = [mail for mail in mails
                    for num, _ in get_result_num_and_ref(mail.Body).items()
                    if num in success]
    for m in unread_mails:
        m.Unread = False
