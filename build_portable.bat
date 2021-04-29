@echo off

rem Сохранить текущую кодировку консоли в переменной %ccp%
rem Источник https://www.dostips.com/forum/viewtopic.php?p=56647&sid=859d35fc5f1ead4cdd2370b10120f562#p56647
For /F "Tokens=*" %%A In ('ChCp') Do For %%B In (%%A) Do Set "ccp=%%~nB"

rem Переменная installOnly говорит, что необходимо только установить виртуальную среду,
rem используется в файле install_venv.bat
set installOnly=true

rem Установка пакетов времени разработки
set pipenvParam=--dev

call .\install_venv.bat %installOnly% %pipenvParam%

IF ERRORLEVEL 1  (
    chcp 65001 > nul && echo Не удалось настроить среду для сборки приложения...
    exit /B %ERRORLEVEL%
)

rem Сформировать дистрибутив, содержащий программу и всё необходимое для её запуска
pipenv run pyinstaller app.spec
IF ERRORLEVEL 1  (
    chcp 65001 > nul && echo Не удалось собрать дистрибутив...
    exit /B %ERRORLEVEL%
)

rem Открыть папку с укомплектованной программой
explorer .\dist

rem Переключение на кодировку utf-8
chcp 65001 > nul

echo Дистрибутив приложения собран. Папка, в которой он находится (dist\) откроется в проводнике
echo Можете переместить его на ЭВМ, у которой отсутствует Python

rem Возврат исходной кодировки
chcp %ccp% > nul

pause