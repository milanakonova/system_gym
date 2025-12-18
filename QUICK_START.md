# Быстрый старт

## Минимальные шаги для запуска

### 1. Установка зависимостей

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установка пакетов
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Установите PostgreSQL, затем создайте БД:
sudo -u postgres psql
CREATE DATABASE gym_sistem;
CREATE USER gym_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE gym_sistem TO gym_user;
\q
```

### 3. Настройка переменных окружения

```bash
cp env.example .env
nano .env  # Отредактируйте DATABASE_URL и SECRET_KEY
```

### 4. Инициализация базы данных

```bash
python init_database.py
```

### 5. Запуск

```bash
# Linux/Mac
./start.sh

# Windows
start.bat

# Или напрямую
uvicorn scr.main:app --reload
```

### 6. Проверка

Откройте в браузере:
- http://localhost:8000/api/docs - Swagger документация
- http://localhost:8000/health - Проверка здоровья

**Вход**: admin@gym.com / admin123

---

## Docker (самый быстрый способ)

```bash
# 1. Настройте .env
cp env.example .env
nano .env

# 2. Запустите
docker-compose up -d

# 3. Инициализируйте БД
docker-compose exec app python init_database.py

# Готово! Приложение на http://localhost:8000
```

---

## Production развертывание

См. подробную инструкцию в [DEPLOYMENT.md](DEPLOYMENT.md)

