## Перейти в директорию с проектом, выполнить
python3 -m venv .venv

. .venv/bin/activate

## Установить все пакеты из requirements.txt

pip install -r requirements.txt

## Задать переменные окружения (аналогично .env-example)

cp .env-example .env

## Запуск скрипта

python3 main.py
