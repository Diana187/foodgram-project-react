# praktikum_new_diplom

### IP для просмотра проекта
```
http://51.250.77.38/
```

## Описание
Сервис «Foodgram» – «Продуктовый помощник». С его помощью пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а также скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### ⚙️ Технологии:

- ![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) (3.7.13)
- ![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green) (3.2.16)
- ![image](https://img.shields.io/badge/django%20rest-ff1709?style=for-the-badge&logo=django&logoColor=white) (3.12.4)
- ![image] (https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
- ![image] (https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)
- ![image] (https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
- ![image] (https://img.shields.io/badge/gunicorn-blue?logo=gunicorn&logoColor=white)


## Установка
Клонируйте репозиторий на локальную машину:
```
git clone https://github.com/Diana187/foodgram-project-react.git
```
Для работы с проектом локально –– установите вирутальное окружение и восстановите зависимости:
```
python -m venv venv
pip install -r requirements.txt
```

## Подготовка удаленного сервера для развертывания приложения
Для работы с проектом на удаленном сервере установите Docker и docker-compose.

Подготовьте сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/
```
Установите docker и docker-compose:
```
sudo apt install docker.io 
sudo apt install docker compose
```
Соберите контейнер и выполните миграции:
```
sudo docker compose up -d --build
sudo docker compose exec backend python manage.py migrate
```
Создайте суперюзера и соберите статику:
```
sudo docker compose exec backend python manage.py createsuperuser
sudo docker compose exec backend python manage.py collectstatic --no-input
```
Скопируйте предустановленные данные json:
```
sudo docker compose exec backend python manage.py loadmodels --path 'recipes/data/ingredients.json'
sudo docker compose exec backend python manage.py loadmodels --path 'recipes/data/tags.json'
```
Для использования панели администратора по адресу http://51.250.77.38/admin/ необходимо создать суперпользователя.
```
python manage.py createsuperuser.
```
К проекту по адресу http://51.250.77.38/redoc/ подключена документация API. В ней описаны шаблоны запросов к API и ответы. Для каждого запроса указаны уровни прав доступа - пользовательские роли, которым разрешён запрос.

## Развернутый проект можно посмотреть по ссылке:
http://51.250.77.38/recipes/
