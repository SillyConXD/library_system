# Library System

Веб-приложение для управления библиотекой на Django: регистрация пользователей, бронирование и выдача книг, отчёты для библиотекаря и администратора.

---

## 📦 Установка

### 1. Клонируйте репозиторий

```sh
git clone https://github.com/ВАШ_ЛОГИН/library_system.git
cd library_system/library
```

---

### 2. Создайте и настройте базу данных PostgreSQL

1. Установите PostgreSQL, если он ещё не установлен:  
   [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

2. Откройте pgAdmin или psql и создайте базу данных и пользователя:

```sql
CREATE DATABASE library_db;
CREATE USER postgres WITH PASSWORD '1234';
GRANT ALL PRIVILEGES ON DATABASE library_db TO postgres;
```

> **Примечание:**  
> Имя базы данных, пользователя и пароль должны совпадать с настройками в файле [`library/library/settings.py`](library/library/settings.py):
> ```
> DATABASES = {
>     'default': {
>         'ENGINE': 'django.db.backends.postgresql',
>         'NAME': 'library_db',
>         'USER': 'postgres',
>         'PASSWORD': '1234',
>         'HOST': 'localhost',
>         'PORT': '5432',
>     }
> }
> ```

---

### 3. Создайте и активируйте виртуальное окружение

**Windows:**
```sh
python -m venv ../myenv
..\myenv\Scripts\activate
```

**Linux/Mac:**
```sh
python3 -m venv ../myenv
source ../myenv/bin/activate
```

---

### 4. Установите зависимости

```sh
pip install -r requirements.txt
```
Если файла `requirements.txt` нет, создайте его командой:
```sh
pip freeze > requirements.txt
```

---

### 5. Примените миграции базы данных

```sh
python manage.py makemigrations
python manage.py migrate
```

---

### 6. Создайте суперпользователя (администратора)

```sh
python manage.py createsuperuser
```
Следуйте инструкциям в терминале.

---

## 🚀 Запуск

```sh
python manage.py runserver
```
Откройте браузер и перейдите по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 👤 Роли пользователей

- **Читатель** — регистрируется через сайт, может бронировать книги.
- **Библиотекарь/Админ** — создаётся через админ-панель, может выдавать книги, просматривать и изменять бронирования, формировать отчёты.

---

## 🛠️ Основные функции

- Регистрация и вход пользователей
- Просмотр каталога книг, поиск и фильтрация
- Бронирование книг читателями
- Выдача книг библиотекарем/админом
- Просмотр и отмена бронирований
- Отчёты по просроченным и популярным книгам
- Админ-панель Django для управления всеми сущностями

---

## 📝 Примечания

- Не забудьте добавить в `.gitignore` файлы виртуального окружения, базу данных и секретные ключи.
- Для загрузки обложек книг настройте директорию `/media/` и добавьте соответствующие настройки в `settings.py`.

---

## 📄 Лицензия

Проект создан в учебных целях.

---

**Если возникнут вопросы — пишите!**
