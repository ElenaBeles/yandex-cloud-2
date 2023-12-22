# Приложение командной строки "Фотоархив"

Порядок сборки приложения:
1. Установить зависимости через requirements.txt
2. Запустить:
    *python cloudphoto.py ###* - Windows
    *.\cloudphoto.py ###* - для Linux
В данном случае *###* - необходимая команда с параметрами 

Функции приложения:

- Инициализация программы **
- Отправка фотографий в облачное хранилище
- Загрузка фотографий из облачного хранилища
- Просмотр списка альбомов и фотографий в альбоме
- Удаление альбомов и фотографий
- Генерация и публикация веб-страниц фотоархива (Пример работы: https://cloudphoto-2.website.yandexcloud.net/index.html)

## Состав git-а

- cloudphoto.py - точка выполнения команд
- functions.py - функции по работе с Yandex cloud
- templates - каталог с файлами(index.html, error.html, album-page.html) для генерации сайта
- requirements.txt - файл с данными об используемых версиях библиотек

> Программа cloudphoto запускается в Unix подобных операционных системах, включая подсистему WSL2 в Windows;

> Конфигурационный файл программы cloudphoto находится в домашнем каталоге пользователя по пути .config/cloudphoto/cloudphotorc;

> При завершении с ошибками программа завершается с кодом возврата (exit status) равным 1;

> При завершении без ошибок программа завершается с кодом возврата (exit status) равным 1;
