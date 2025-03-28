# API для информации о Tron адресах

Микросервис, предоставляющий информацию о адресах в блокчейне Tron, включая баланс TRX, bandwidth и energy. Сервис логирует все запросы адресов в базу данных и предоставляет эндпоинты для получения истории запросов с пагинацией.

В реальном кейсе я бы использовал gRPC, а также alembic для миграций.

## Требования

- Python 3.12+
- Docker и Docker Compose (опционально)

## Установка

### Использование Docker (Рекомендуется)

1. Клонируйте репозиторий:

   ```
   git clone https://github.com/hoopengo/tron-fastapi.git
   cd tron-fastapi
   ```

2. Запустите приложение и базу данных с Docker Compose:

   ```
   docker compose -f docker/compose.yml up db -d --build
   # подождать 5 секунд
   docker compose -f docker/compose.yml up app -d --build
   ```

3. Остановить контейнер:

   ```
   docker compose -f docker/compose.yml down -v
   ```

4. Доступ к API по адресу http://localhost:8000

### Локальная разработка

1. Клонируйте репозиторий:

   ```
   git clone https://github.com/hoopengo/tron-fastapi.git
   cd tron-fastapi
   ```

2. Создайте виртуальное окружение и установите зависимости:

   ```
   uv venv --python 3.12
   uv sync
   ```

3. Создайте файл `.env` на основе примера:

   ```
   cp .env.example .env
   ```

4. Добавьте env на датабазу:

   ```
   export DATABASE_URL="sqlite:///./db.sqlite3"
   ```

5. Запустите приложение:

   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. Доступ к API по адресу http://localhost:8000

## Эндпоинты API

### `POST /addresses/`

Получение информации о Tron адресе, включая баланс TRX, bandwidth и energy.

**Тело запроса:**

```json
{
  "address": "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8"
}
```

**Ответ:**

```json
{
  "address": "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8",
  "balance_trx": 15.456907,
  "bandwidth": 600,
  "energy": 0
}
```

### `GET /addresses/`

Получение списка недавних запросов адресов из базы данных с пагинацией.

**Параметры запроса:**

- `page`: Номер страницы (по умолчанию: 1)
- `page_size`: Количество элементов на странице (по умолчанию: 10, макс: 100)

**Ответ:**

```json
{
  "total": 1,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "address": "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8",
      "balance_trx": 15.456907,
      "bandwidth": 600,
      "energy": 0,
      "id": 1,
      "created_at": "2025-03-28T02:42:33.582576Z"
    }
    // другие запросы
  ]
}
```

## Тестирование

Запуск тестов с pytest:

```
export DATABASE_URL=sqlite:///./test.db
pytest
```
