@echo off
rem Github не поддерживает макрос include, поэтому необходимо собрать документ со включениями в единый документ
rem На компьтере должен быть установлен asciidoctorj и pandoc

set base_dir=.
set tgt_dir=..
set src=readme.adoc
set tgt=%tgt_dir%\readme.adoc
set docbook_file=%src%.xml

rem Конвертируем в формат docbook
asciidoctorj 	--base-dir %base_dir% --destination-dir %tgt_dir% ^
		--backend docbook --attribute imagesdir=doc\img ^
		--out-file %docbook_file% %src%

rem Коневертируем обратно в asciidoc, но уже единым файлом
pandoc 	--from=docbook --to=asciidoctor ^
	--standalone ^
	--output=%tgt% %tgt_dir%\%docbook_file%

rem Удаляем временные файлы
del %tgt_dir%\%docbook_file%