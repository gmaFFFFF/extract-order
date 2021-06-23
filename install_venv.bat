@echo off

rem Переменная installOnly == "true" говорит, что необходимо только установить виртуальную среду
set installOnly=%1
rem Переменная pipenvParam задает параметры запуска pipenv
set pipenvParam=%2
rem Доверенные источники пакетов Python
set trustedHostParam=--trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
rem Если возникнут проблемы с SSL сертификатами, то необходимо закоментировать следующую строку
set trustedHostParam=
rem Сохранить текущую кодировку консоли в переменной %ccp%
rem Источник https://www.dostips.com/forum/viewtopic.php?p=56647&sid=859d35fc5f1ead4cdd2370b10120f562#p56647
For /F "Tokens=*" %%A In ('ChCp') Do For %%B In (%%A) Do Set "ccp=%%~nB"

:install

rem Обновляем pip
py -m pip install %trustedHostParam% --upgrade pip

rem Установка pipx для управления cli приложениями python
py -m pip install %trustedHostParam%  --user pipx
IF ERRORLEVEL 1  (
    rem Сообщение об ошибке и возврат из процедуры
    chcp 65001 > nul && echo Ошибка Errorlevel: %ERRORLEVEL%
    chcp 65001 > nul && echo Возможно необходимо переустановить Python
    exit /B %ERRORLEVEL%
)

rem Добавление пути к pipx в переменную среды windows Path
py -m pipx ensurepath

rem Обновить переменную среды path
call RefreshEnv.cmd

rem Установка менеджера пакетов и вирутальных сред pipenv
pipx install --pip-args="%trustedHostParam%" pipenv

rem Проверка доступности pipenv. Если команда не найдена, то ERRORLEVEL == 1
where pipenv > nul
IF ERRORLEVEL 1  (
    rem Сообщение об ошибке и возврат из процедуры
    chcp 65001 > nul && echo Ошибка Errorlevel: %ERRORLEVEL%
    exit /B %ERRORLEVEL%
)

rem Обновляем pip  в виртуальной среде pipenv. Нужно для обновления приложения в той же venv
pipenv run py -m pip install %trustedHostParam% --upgrade pip

rem Установка зависимостей приложения
pipenv install %pipenvParam%

rem Обновить переменную среды path
call RefreshEnv.cmd

rem Если требуется только настройки виртуальной среды окружения, то завершить исполнение
if "%installOnly%"=="true" goto :EOF

:firstStart
rem Переключение на кодировку utf-8
chcp 65001  > nul
rem Вывод пустых строк
@echo.
@echo.
chcp 65001 > nul && echo Для заказа выписок запустите start_order.bat
chcp 65001 > nul && echo Для скачивания выписок из Outlook запустите start_download.bat




