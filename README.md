# Меню ресторана

Домашнее задание 1. "Написать проект на FastAPI с использованием PostgreSQL в качестве БД.
В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции.
Для проверки задания, к презентаций будет приложена Postman коллекция с тестами.
Задание выполнено, если все тесты проходят успешно.
Даны 3 сущности: Меню, Подменю, Блюдо."

## Начало работы

### Предварительные условия

Что нужно установить на ваш компьютер для использования проекта:
Python 3.10, PostgreSQL

### Установка

Пошаговый процесс установки и запуска проекта:

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/databorodata/restmenu.git

2. Перейдите в директорию проекта:

   ```bash
   cd /project/path

3. Создайте и активируйте виртуальное окружение:

   ```bash
   python3 -m venv venv

   source venv/bin/activate

4. Установите зависимости из файла requirements.txt:

   ```bash
   pip install -r requirements.txt

5. Создайте файл .env на основе .env_template и заполните необходимые переменные окружения (POSTGRES_HOST, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER).


6. Запустите проект с помощью скрипта start.sh:

   ```bash
   ./start.sh

## Развёртывание в Docker

### Запуск приложения в Docker

1. Перейдите в директорию проекта:

   ```bash
   cd /project/path

2. Чтобы запустить приложение, используйте следующую команду в вашем терминале

   ```bash
   docker-compose up -d

### Запуск тестов в Docker

1. Перейдите в директорию проекта:

   ```bash
   cd /project/path

2. Чтобы запустить тест для приложения, используйте следующую команду в вашем терминале

   ```bash
   docker-compose -f docker-compose-tests.yml up
   ```

### Доступ к google sheet открыт для редактирования по ссылке:

https://docs.google.com/spreadsheets/d/1aSWKJa9XeNGBfrtz2vdyuVKSW-y7XpkaZzkeIZpuG_8/edit#gid=1285963425

### Задание "Добавить эндпоинт (GET) для вывода всех меню со всеми связанными подменю и со всеми связанными блюдами". Реализовано здесь:

https://github.com/databorodata/restmenu/blob/celery_rabbit/app/routers/router_full_menu.py#L23

## Задания со звёздочкой

### * Реализовать вывод количества подменю и блюд для Меню через один (сложный) ORM запрос.

Реализован во всех файлах в папке app/repositories. Например здесь:

https://github.com/databorodata/restmenu/blob/celery_rabbit/app/repositories/menu_repository.py#L50

### ** Реализовать тестовый сценарий «Проверка кол-ва блюд и подменю в меню» из Postman с помощью pytest

Реализован здесь:

https://github.com/databorodata/restmenu/blob/celery_rabbit/tests/test_count_submenu_dish.py#L10

### * Описать ручки API в соответствий c OpenAPI

Реализован во всех файлах в папке app/router . Например здесь:

https://github.com/databorodata/restmenu/blob/celery_rabbit/app/routers/router_menu.py#L18

### ** Реализовать в тестах аналог Django reverse() для FastAPI

Реализован во всех тестах ( папка tests). Функция reverse здесь:

https://github.com/databorodata/restmenu/blob/celery_rabbit/tests/utils.py#L6

### * Обновление меню из google sheets раз в 15 сек.

Реализация механизма обновления происходит в папке backgorund. Иницализация celery  здесь:

https://github.com/databorodata/restmenu/blob/celery_rabbit/background/celery_app.py#L18
