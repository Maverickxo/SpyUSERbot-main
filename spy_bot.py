from pyrogram import Client, filters
from config import *
from load_conf_json import load_config
from log_utils import log_console, log_message

# Инициализация клиента и маршрутов
ROUTES = load_config()
app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)


# Команда для обновления конфигурации
@app.on_message(filters.command("reload_config") & filters.user(ADMIN))  # Укажите ваш ID админа
def reload_config(message):
    """
    Обновляет маршруты из config.json и отправляет их администратору.

    - Загружает конфигурацию.
    - Отправляет информацию о маршрутах и правилах администратору.
    - Сообщает об ошибке, если конфигурация недоступна.
    """
    global ROUTES
    ROUTES = load_config()
    if ROUTES:
        # Формируем сообщение для админа
        response = "Конфигурация успешно обновлена!\n\nТекущие маршруты и правила:\n"
        for source_id, route in ROUTES.items():
            response += f"- Из '{route['from_name']}' (ID: {source_id}) в '{route['to_name']}' (ID: {route['to_id']})\n"
            rules = route.get("rules", {})
            if rules:
                response += "  Правила:\n"
                if "keywords" in rules:
                    response += f"    - Ключевые слова: {', '.join(rules['keywords']) or 'Не указаны'}\n"
                if "min_length" in rules:
                    response += f"    - Минимальная длина сообщения: {rules['min_length']}\n"
            else:
                response += "  Правила: отсутствуют\n"

        message.reply(response)
        print("Конфигурация успешно обновлена. Текущие маршруты и правила:")
        print(response)
    else:
        response = "Конфигурация не обновлена. Проверьте файл config.json."
        message.reply(response)
        print(response)


@app.on_message(filters.chat(list(ROUTES.keys())))
def copy_message(message):
    """
    Пересылает сообщения из чатов-источников в целевые чаты согласно конфигурации.

    - Логирует сообщения в консоль и файл.
    - Проверяет правила маршрутизации (`keywords`, `min_length`).
    - Добавляет информацию об отправителе и чате-источнике.
    """

    route_info = ROUTES[message.chat.id]
    target_chat_id = route_info["to_id"]
    source_chat_name = route_info["from_name"]
    target_chat_name = route_info["to_name"]

    # Логируем сообщение в консоль
    log_console(message)

    # Получение информации о пользователе
    user_info = ""
    if message.from_user:
        user_info = f"\nОтправитель:\nИмя: {message.from_user.first_name or 'Нет'}\n"
        user_info += f"ID: {message.from_user.id}\n"
        if message.from_user.username:
            user_info += f"Username: @{message.from_user.username}\n"

    # Логируем сообщение
    log_message(source_chat_name, message.chat.id, target_chat_name, target_chat_id, message.text or "[Медиа]")

    # Проверка правил маршрутизации
    rules = route_info.get("rules", {})
    keywords = rules.get("keywords", [])  # Получаем ключевые слова, если указаны
    min_length = rules.get("min_length", 0)  # Длина сообщения, если указана

    # Если `keywords` не указаны или пустые, собираем все сообщения
    if keywords and message.text:
        if not any(keyword in message.text for keyword in keywords):
            return

    # Если `min_length` не указана, обрабатываем все сообщения
    if min_length > 0 and message.text:
        if len(message.text) < min_length:
            return

    # Пересылка сообщений с добавлением информации о пользователе
    if message.text:
        modified_text = f"Сообщение:\n{message.text}\n\n---\nЧат: {source_chat_name}{user_info}"
        app.send_message(chat_id=target_chat_id, text=modified_text)
    elif message.photo:
        caption = f"Сообщение:\n{message.caption or ''}\n\n---\nЧат: {source_chat_name}\n{user_info}"
        app.send_photo(chat_id=target_chat_id, photo=message.photo.file_id, caption=caption)
    elif message.video:
        caption = f"Сообщение:\n{message.caption or ''}\n\n---\nЧат: {source_chat_name}\n{user_info}"
        app.send_video(chat_id=target_chat_id, video=message.video.file_id, caption=caption)
    elif message.document:
        caption = f"Сообщение:\n{message.caption or ''}\n\n---\nЧат: {source_chat_name}\n{user_info}"
        app.send_document(chat_id=target_chat_id, document=message.document.file_id, caption=caption)
    else:
        print(f"Неподдерживаемый тип сообщения из {source_chat_name} ({message.chat.id})")


# Универсальный обработчик для логирования всех сообщений
@app.on_message()
def universal_logger(message):
    """
    Универсальный обработчик для логирования всех сообщений.

    - Логирует каждое полученное сообщение в консоль.
    - Работает независимо от конфигурации маршрутов.
    """

    log_console(message)  # Логируем все сообщения, не завися от конфигурации


# Запуск бота
if __name__ == "__main__":
    if not ROUTES:
        print("Файл конфигурации отсутствует. Сообщения будут выведены в консоль.")
    else:
        print("Бот запущен с маршрутами:")
        for source_id, route in ROUTES.items():
            print(f"- Из '{route['from_name']}' ({source_id}) в '{route['to_name']}' ({route['to_id']})")
    app.run()
