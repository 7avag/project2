# project2

Учебный проект на Python + Aiogram. Бот хранит заметки каждого пользователя в JSON, выдаёт шутки (русские и английские), поддерживает переключение языка и даёт админу возможность рассылать сообщения и смотреть статистику. Авторы: Шорохов Владимир 472680 Шаповалова Виктория 468062



## Структура проекта


config/              # Настройки (чтение .env)
filters/             # Фильтры (проверка админа)
keyboards/           # Клавиатуры
  ├─ builders.py     # Формирует ReplyKeyboard (кнопки меню)
  └─ inline.py       # Формирует InlineKeyboard (действия с заметками)
locales/             # JSON-файлы с переводами (ru.json, en.json)
middlewares/         # Антиспам
routers/             # Обработчики команд и колбэков
  └─ commands.py     # Логика взаимодействия с ботом
services/            # Внешние сервисы
  └─ api_client.py   # Запрос шуток через HTTP + кэширование
states/              # 
  └─ notes_state.py  # Описаны состояния для создания/удаления заметок
storage/             # Хранилище заметок
  └─ storage.json    # 
utils/               # Утилиты
  ├─ formatters.py   # Форматирование текста заметки (дата/время)
  └─ logger.py       # Логгер (запись в файл)
bot.py               # Точка входа: создаёт Bot, Dispatcher, регистрирует роутеры
.env.example         # Шаблон переменных окружения (токен, админы и т.д.)
requirements.txt     # Зависимости (aiogram, aiohttp, aiocache...)
README.md            # Этот файл: краткое описание и возможности


## Что делает каждый файл

**config/settings.py**

* Читает `.env` (используется python-dotenv).
* Содержит поля: `BOT_TOKEN`, `ADMINS` (список user\_id), `API_TIMEOUT`, `CACHE_TTL`.
* Изменить здесь можно: путь к файлу хранения заметок, параметры таймаута и кэша, перечень админов.

**filters/admin\_filter.py**

* Класс `IsAdminFilter`: проверяет, что пользователь есть в `ADMINS`. Применяется к командам `/broadcast` и `/stats`.

**keyboards/builders.py**

* Функция `main_menu(lang)`: создаёт ReplyKeyboardMarkup с кнопками меню на русском или английском ("Мои заметки", "Шутка", "Язык", "Помощь").

**keyboards/inline.py**

* Функция `note_actions_keyboard(lang)`: создаёт InlineKeyboardMarkup с кнопками "Добавить заметку", "Удалить заметку", "Отмена" (или англ. "Add note", "Delete note", "Cancel").

**locales/ru.json** и **locales/en.json**

* Хранят все сообщения и фразы (приветствие, справка, подсказки для заметок, ошибки, тексты рассылки).

**middlewares/throttling.py**

* Простейший шаблон для ограничения частоты команд (антиспам). В текущей версии пропускает все запросы.

**routers/commands.py**

* Основная логика бота:

  * `/start`: установка `lang="ru"`, отправка приветствия и клавиатуры.
  * `/help`: показывает справку из `locales` (зависит от `lang`).
  * `/joke`: если `lang=="en"` или нажата кнопка "🤣 Joke", берёт шутку из внешнего API (`api_client`) и кэширует; иначе случайная русская.
  * `/language`: переключает между "ru" и "en", сохраняет в FSM, обновляет клавиатуру.
  * `/notes`: показывает список заметок текущего пользователя (по `user_id` в JSON), выводит Inline-клавиатуру для действий.
  * Колбэки `add_note`, `delete_note`, `cancel`: переходят в состояния FSM, запрашивают ввод текста или ID, сохраняют/удаляют заметки.
  * `/broadcast <text>`: админская команда, обходит всех `user_id` из `storage.json`, шлёт сообщение, считает `sent`/`failed`.
  * `/stats`: админская команда, возвращает `len(db["users"])`.

**services/api\_client.py**

* Класс `APIClient` с методом `get_random_joke`: делает асинхронный HTTP-запрос к `Chuck Norris API`, кэширует результат (`aiocache`).

**states/notes\_state.py**

* Определены два состояния : `WAITING_FOR_NOTE_TEXT` и `WAITING_FOR_DELETE_ID`.

**storage/storage.json**

* Главное хранилище заметок, формат:

  json
  { "users": { "<user_id>": [ { "id": 1, "text": "...", "timestamp": "..." }, ... ] } }
  

**utils/formatters.py**

* Функция `format_note`: форматирует запись заметки для вывода (ID, текст, дата/время).

**utils/logger.py**

* Настройка логгирования через стандартный `logging`. По умолчанию пишет в файл `bot.log` и/или в консоль.

**bot.py**

* Точка входа:

  1. Загружает `.env`, создаёт `Bot(token)`, `Dispatcher` с `MemoryStorage`.
  2. Регистрирует `ThrottlingMiddleware`, `IsAdminFilter`, подключает роутер `commands`.
  3. Запускает `dp.start_polling(bot)`.

**requirements.txt**

* Список зависимостей:

  aiogram
  aiohttp
  aiocache
  python-dotenv


**.env.example**

* Шаблон для переменных окружения, чтобы не слить токен.


### Как запустить

1. **Клонировать/распаковать** проект.
2. Создать виртуальное окружение:

   
   python -m venv venv
   source venv/bin/activate  # или .\venv\Scripts\activate для Windows
   
3. Установить зависимости:

   
   pip install -r requirements.txt
   
4. Скопировать `.env.example` → `.env` и заполнить:

   
   BOT_TOKEN=<ваш_токен>
   ADMINS=<ваши_ID>
   API_TIMEOUT=10
   CACHE_TTL=60
   
   BOT_TOKEN нужно брать у @BotFather
   Чтобы узнать ID своего аккаунта Телеграм, воспользуйтесь ботом @userinfobot
   
5. Убедиться, что `storage/storage.json` существует и внутри:

   json
   { "users": {} }
   
6. Запустить бота:

   
   python bot.py
   
7. В Telegram нажать «Start» (или `/start`), проверить команды.
