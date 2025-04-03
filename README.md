# Приложение Виртуальный Офис (Онлайн Офис)
Приложение Виртуальный Офис представляет собой сочетание Agile досок и чатов для организации работы команд.  
[Описание концепции](https://docs.google.com/document/d/18LW9NSkqJL2wgNNiybbIwfivqAUDlHoJxPBWO1Tdr9Y/edit?usp=sharing)

## Требования к системе:
1) Установленный [Docker](https://www.docker.com/)
2) Желательно установленный [Make](https://www.gnu.org/software/make/). Для пользователей Windows [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm)

## Текущий состав сборки:
1) PostgreSQL версии 16
2) Backend сервер на базе Python 3.12 с использованием FastApi и SQLAlchemy   
3) Redis последняя стабильная версия опубликованная в Docker Hub
4) RabbitMQ 4 Management последняя версия опубликованная в Docker Hub
5) В отдельном репозитории ведется разработка прототипа frontend приложения [ссылка](https://github.com/DenisMaslennikov/virtual-office-portotype)

## В API backend на данный момент реализовано:
1) [Структура БД](https://dbdiagram.io/d/online_office-674309ede9daa85aca83d70e)
2) Возможность регистрации пользователей и аутентификации
3) Механизм получения/обновления JWT токена
4) Тестовый websocket чат с возможностью отправки сообщения и рассылки всем подписанным на канал клиентам. [Проект протокола websocket](https://docs.google.com/document/d/138YtcPSjwvNBRKij6UjerFuiyjv6x1ZWpNOoYhxnI8s/edit?usp=sharing)

## Запуск dev сервера:
1) Клонируйте репозиторий `git clone https://github.com/DenisMaslennikov/office-online.git`
2) Откройте директорию проекта
3) Создайте `.env` файл в директории config используя в качестве шаблона .env.template из той же директории
4) Если в системе установлен make используйте команду `make start` если make не установлен используйте команду `docker compose up --build`
5) Документация в формате Swagger будет доступна по адресу http://127.0.0.1:8000/docs#


