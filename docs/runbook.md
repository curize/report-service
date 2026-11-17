# Runbook развёртывания v1.0.1 (вариант 7)

Команды даны для Windows PowerShell, выполняются из корня репозитория.

## Предусловия
- Docker запущен: `docker version`, `docker compose version`.
- Порт 8207 свободен: `netstat -ano | findstr :8207` ничего не выводит.
- Порт 8080 занят (демонстрация варианта): в отдельном окне `python -m http.server 8080`.
- В репозитории есть метки v1.0.0 и v1.0.1: `git tag`.

## A. Начальное состояние (v1.0.0, порт 8090)
1. `git checkout v1.0.0`
2. `docker compose up -d --build`
3. `python scripts/acceptance.py http://localhost:8090 --log deployment-log.txt`
Контрольная точка: все проверки PASS, `docker compose ps` показывает app в состоянии running.

## B. Резервная копия данных
1. `mkdir backup`
2. `docker compose cp app:/data/data.json backup/data.json`
3. `python scripts/verify_backup.py backup/data.json restored`
Контрольная точка: `RESULT: OK, checksums match`, файл есть в каталоге restored.

## C. Развёртывание v1.0.1 (замена с изменением порта)
1. `docker compose down` (без ключа -v: том с данными сохраняется)
2. `git checkout release`
3. `Copy-Item env.example .env`
4. `docker compose up -d --build`
5. Подождать 15 секунд и выполнить `docker compose ps`: статус healthy.
6. `python scripts/acceptance.py http://localhost:8207 --closed-port 8090 --log deployment-log.txt`
7. Открыть http://localhost:8207/records: старые записи на месте.
Контрольные точки: шаг 5 — healthy; шаг 6 — ALL CHECKS PASSED; шаг 7 — число записей не меньше, чем до замены.

## Критерий остановки
Любая ошибка команды, статус unhealthy, строка FAIL в приёмочных проверках или потеря записей: остановиться и выполнить откат (раздел D).

## D. Откат на v1.0.0 (возврат старого сопоставления портов 8090 -> 8080)
1. `docker compose down` (без -v)
2. `git checkout v1.0.0`
3. `docker compose up -d --build`
4. `python scripts/acceptance.py http://localhost:8090 --closed-port 8207 --log deployment-log.txt`
5. Проверить http://localhost:8090/records: данные сохранены.
После проверки отката вернуться к v1.0.1: `git checkout release`, повторить раздел C.

## E. Наблюдение
- Статус: `docker compose ps`; здоровье: `docker inspect --format "{{.State.Health.Status}}" report-service-app-1`
- Журнал: `docker compose logs --tail 20`
- Ресурсы: `docker stats --no-stream`

## F. Отказ: порт занят другим процессом
1. `docker compose down`
2. В отдельном окне PowerShell: `python -m http.server 8207`
3. `docker compose up -d`: ожидается ошибка вида «port is already allocated / ports are not available».
4. Обнаружение: текст ошибки, `docker compose ps` (контейнера нет), `netstat -ano | findstr :8207` (порт слушает чужой процесс).
5. Устранение: остановить тестовый процесс (Ctrl+C в окне), затем `docker compose up -d`.
6. Проверка: `docker compose ps` показывает healthy, `python scripts/acceptance.py http://localhost:8207 --log deployment-log.txt` — ALL CHECKS PASSED.
Критерий восстановления: конфликт обнаружен и устранён, сервис healthy, данные на месте.
