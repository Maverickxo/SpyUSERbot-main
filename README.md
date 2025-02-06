
Программа для мониторинга и маршрутизации сообщений в Telegram.

### Требования:
- Установленная библиотека Pyrogram.
- API ID и API Hash от Telegram.

### Описание:
- Основная задача программы — пересылка сообщений из чатов-источников в целевые чаты 
  согласно настройкам из файла конфигурации (config.json).
- Логирует информацию о сообщениях, отправителях и чатах в консоль и файл.
- Работает с текстовыми сообщениями и медиа (фото, видео, документы).

### Особенности:
- Универсальное логирование всех сообщений, даже при отсутствии конфигурации.
- Поддержка любых типов сообщений (текст, фото, видео, документы).
- Гибкая настройка правил через конфигурационный файл.
---

### Функциональность:
1. **Загрузка конфигурации:**
   - Файл config.json содержит маршруты и правила пересылки:
     - Ключевые слова (keywords).
     - Минимальная длина сообщения (min_length).
   - Если файл отсутствует, сообщения логируются в консоль без пересылки.

2. **Пересылка сообщений:**
   - Сообщения пересылаются из чатов-источников в целевые чаты.
   - К каждому пересылаемому сообщению добавляется информация:
     - Имя отправителя, ID, username.
     - Название и ID чата-источника.
   - Перед пересылкой сообщения проверяются по заданным правилам маршрутизации.

3. **Логирование:**
   - Все сообщения (текстовые и медиа) логируются в:
     - Консоль (для отладки).
     - Файл message_logs.txt (для сохранения истории).

4. **Команда /reload_config:**
   - Позволяет администратору обновить маршруты и правила пересылки без перезапуска программы.
   - Текущая конфигурация отправляется администратору в ответном сообщении и выводится в консоль.

---

### Описание правил маршрутизации:

1. **Если keywords пустое и min_length равен 0:**
   - Пересылаются все сообщения.

2. **Если keywords указан, а min_length равен 0:**
   - Пересылаются только сообщения, содержащие ключевые слова.

3. **Если min_length указан, а keywords пустое:**
   - Пересылаются все сообщения, длина которых превышает заданное количество символов.

4. **Если указаны оба правила (keywords и min_length):**
   - Пересылаются только сообщения, которые одновременно:
     - Содержат хотя бы одно ключевое слово.
     - Длиннее или равны указанному количеству символов.

---

### Пример структуры файла config.json:
json
{
  "routes": [
    {
      "from_id": -1001234567890,
      "from_name": "Источник",
      "to_id": -1009876543210,
      "to_name": "Получатель",
      "rules": {
        "keywords": ["важно", "срочно"],
        "min_length": 10
      }
    }
  ]
}
