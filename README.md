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


### Задание "Реализовать вывод количества подменю и блюд для Меню через один (сложный) ORM запрос."


Запрос реализовал в отдельном эндпоинте:

https://github.com/databorodata/restmenu/blob/pytest_docker/app/routers/complex.py#L16


Так же внедрил запрос для работы эндопоинтов сущности Меню

https://github.com/databorodata/restmenu/blob/pytest_docker/app/routers/router_menu.py#L30
