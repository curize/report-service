# report-service

Учебный HTTP-сервис отчётов (практическая работа № 5, вариант 7).

Маршруты: `GET /health`, `GET /report`, `GET /records`, `POST /records` (JSON `{"name": "...", "value": 1}`).
Данные хранятся в `data.json` в каталоге `DATA_DIR` (в контейнере `/data`, именованный том).

## Тесты

    python -m unittest discover -s tests -v

## Запуск

    docker compose up -d --build
