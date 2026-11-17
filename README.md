# report-service

Учебный HTTP-сервис отчётов (практическая работа № 5, вариант 7).

Маршруты: `GET /health`, `GET /report`, `GET /records`, `POST /records` (JSON `{"name": "...", "value": 1}`).
Данные хранятся в `data.json` в каталоге `DATA_DIR` (в контейнере `/data`, именованный том `report-data`).

## Конфигурация

Порт читается из переменной окружения `PORT` (по умолчанию 8080). Параметры развёртывания — в `env.example`:

    Copy-Item env.example .env      # PowerShell; Linux: cp env.example .env

## Тесты

    python -m unittest discover -s tests -v

## Запуск

    docker compose up -d --build

## Документы

- `docs/passport.md` — паспорт приложения и платформы
- `docs/runbook.md` — порядок развёртывания, отката и действий при отказе
- `docs/checklist.md` — чек-лист приёмки
- `CHANGELOG.md` — история версий
