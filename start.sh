#!/bin/bash
# Скрипт для запуска приложения

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Запуск системы управления тренажерным залом ===${NC}"

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

# Активация виртуального окружения
echo -e "${GREEN}Активация виртуального окружения...${NC}"
source venv/bin/activate

# Проверка зависимостей
if [ ! -f "venv/bin/uvicorn" ]; then
    echo -e "${YELLOW}Установка зависимостей...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Проверка файла .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Файл .env не найден. Создание из примера...${NC}"
    if [ -f "env.example" ]; then
        cp env.example .env
        echo -e "${RED}⚠️  ВАЖНО: Отредактируйте файл .env перед запуском в production!${NC}"
    else
        echo -e "${RED}Ошибка: файл env.example не найден!${NC}"
        exit 1
    fi
fi

# Проверка подключения к базе данных
echo -e "${GREEN}Проверка подключения к базе данных...${NC}"
python -c "from scr.db.database import engine; engine.connect(); print('✅ База данных подключена')" 2>/dev/null || {
    echo -e "${RED}Ошибка подключения к базе данных!${NC}"
    echo -e "${YELLOW}Убедитесь, что:${NC}"
    echo "  1. PostgreSQL запущен"
    echo "  2. База данных создана"
    echo "  3. DATABASE_URL в .env настроен правильно"
    exit 1
}

# Запуск приложения
echo -e "${GREEN}Запуск приложения...${NC}"
echo -e "${YELLOW}Приложение будет доступно по адресу: http://0.0.0.0:8000${NC}"
echo -e "${YELLOW}Документация API: http://0.0.0.0:8000/api/docs${NC}"
echo ""

uvicorn scr.main:app --host 0.0.0.0 --port 8000 --reload

