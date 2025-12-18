# Инструкция по развертыванию системы управления тренажерным залом

## Содержание
1. [Требования](#требования)
2. [Подготовка сервера](#подготовка-сервера)
3. [Установка зависимостей](#установка-зависимостей)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Настройка приложения](#настройка-приложения)
6. [Запуск приложения](#запуск-приложения)
7. [Настройка автозапуска (systemd)](#настройка-автозапуска-systemd)
8. [Развертывание с Docker](#развертывание-с-docker)
9. [Настройка Nginx (опционально)](#настройка-nginx-опционально)
10. [Проверка работоспособности](#проверка-работоспособности)
11. [Устранение неполадок](#устранение-неполадок)

---

## Требования

- **ОС**: Linux (Ubuntu 20.04+ / Debian 11+ / CentOS 8+)
- **Python**: 3.11 или выше
- **PostgreSQL**: 12 или выше
- **Память**: минимум 512 MB RAM
- **Диск**: минимум 1 GB свободного места

---

## Подготовка сервера

### 1. Обновление системы

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Установка Python и необходимых инструментов

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
sudo yum install -y python3 python3-pip git
```

### 3. Установка PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
```

### 4. Запуск PostgreSQL

```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# CentOS/RHEL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## Установка зависимостей

### 1. Клонирование или загрузка проекта

```bash
# Если проект в Git репозитории
git clone <repository_url> /opt/system_gym
cd /opt/system_gym

# Или загрузите проект вручную в /opt/system_gym
```

### 2. Создание виртуального окружения

```bash
cd /opt/system_gym
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка Python зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Настройка базы данных

### 1. Создание пользователя и базы данных PostgreSQL

```bash
sudo -u postgres psql
```

В консоли PostgreSQL выполните:

```sql
-- Создание пользователя (замените 'your_password' на надежный пароль)
CREATE USER gym_user WITH PASSWORD 'your_secure_password';

-- Создание базы данных
CREATE DATABASE gym_sistem OWNER gym_user;

-- Выдача прав
GRANT ALL PRIVILEGES ON DATABASE gym_sistem TO gym_user;

-- Выход
\q
```

### 2. Инициализация базы данных приложения

```bash
cd /opt/system_gym
source venv/bin/activate
python init_database.py
```

После успешной инициализации вы увидите:
- ✅ Инициализация успешно завершена!
- Данные для входа администратора:
  - Email: admin@gym.com
  - Password: admin123

**⚠️ ВАЖНО**: Измените пароль администратора после первого входа!

---

## Настройка приложения

### 1. Создание файла конфигурации .env

```bash
cd /opt/system_gym
cp env.example .env
nano .env
```

### 2. Настройка переменных окружения

Отредактируйте файл `.env` со следующими значениями:

```env
# База данных (используйте данные из шага выше)
DATABASE_URL=postgresql://gym_user:your_secure_password@localhost:5432/gym_sistem

# Генерация секретного ключа для JWT
# Выполните: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=ваш_сгенерированный_секретный_ключ

# CORS - укажите домены вашего фронтенда
CORS_ORIGINS=http://yourdomain.com,https://www.yourdomain.com

# Настройки сервера
HOST=0.0.0.0
PORT=8000
RELOAD=False
```

### 3. Установка прав доступа

```bash
chmod 600 .env  # Только владелец может читать/писать
```

---

## Запуск приложения

### Ручной запуск (для тестирования)

```bash
cd /opt/system_gym
source venv/bin/activate
uvicorn scr.main:app --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: `http://your_server_ip:8000`

### Запуск с несколькими воркерами (рекомендуется для production)

```bash
uvicorn scr.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Настройка автозапуска (systemd)

### 1. Создание пользователя для приложения (опционально, но рекомендуется)

```bash
sudo useradd -r -s /bin/false -d /opt/system_gym gym_app
sudo chown -R gym_app:gym_app /opt/system_gym
```

### 2. Настройка systemd сервиса

Отредактируйте файл `system_gym.service` и укажите правильные пути:

```bash
nano system_gym.service
```

Измените следующие строки при необходимости:
- `User=` - пользователь для запуска (gym_app или ваш пользователь)
- `Group=` - группа пользователя
- `WorkingDirectory=` - путь к проекту (/opt/system_gym)
- `ExecStart=` - путь к uvicorn

### 3. Установка и запуск сервиса

```bash
# Копирование файла сервиса
sudo cp system_gym.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable system_gym

# Запуск сервиса
sudo systemctl start system_gym

# Проверка статуса
sudo systemctl status system_gym
```

### 4. Просмотр логов

```bash
# Просмотр логов
sudo journalctl -u system_gym -f

# Последние 100 строк
sudo journalctl -u system_gym -n 100
```

---

## Развертывание с Docker

### 1. Установка Docker и Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Выход и повторный вход для применения изменений группы
exit
```

### 2. Настройка переменных окружения для Docker

Создайте файл `.env` в корне проекта:

```env
DB_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://yourdomain.com,https://www.yourdomain.com
```

### 3. Запуск с Docker Compose

```bash
cd /opt/system_gym

# Сборка и запуск контейнеров
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Остановка с удалением данных БД (осторожно!)
docker-compose down -v
```

### 4. Инициализация базы данных в Docker

```bash
# Выполнение команды инициализации внутри контейнера
docker-compose exec app python init_database.py
```

---

## Настройка Nginx (опционально)

### 1. Установка Nginx

```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

### 2. Создание конфигурации Nginx

Создайте файл `/etc/nginx/sites-available/system_gym`:

```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/system_gym/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Активация конфигурации

```bash
# Ubuntu/Debian
sudo ln -s /etc/nginx/sites-available/system_gym /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# CentOS/RHEL
sudo cp /etc/nginx/sites-available/system_gym /etc/nginx/conf.d/system_gym.conf
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Настройка SSL с Let's Encrypt (рекомендуется)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your_domain.com -d www.your_domain.com

# Автоматическое обновление
sudo systemctl enable certbot.timer
```

---

## Проверка работоспособности

### 1. Проверка API

```bash
# Проверка здоровья приложения
curl http://localhost:8000/health

# Должен вернуть: {"status":"ok"}
```

### 2. Проверка документации API

Откройте в браузере:
- Swagger UI: `http://your_server:8000/api/docs`
- ReDoc: `http://your_server:8000/api/redoc`

### 3. Проверка подключения к базе данных

```bash
cd /opt/system_gym
source venv/bin/activate
python -c "from scr.db.database import engine; engine.connect(); print('База данных подключена успешно')"
```

---

## Устранение неполадок

### Проблема: Приложение не запускается

**Решение:**
1. Проверьте логи: `sudo journalctl -u system_gym -n 50`
2. Убедитесь, что PostgreSQL запущен: `sudo systemctl status postgresql`
3. Проверьте файл `.env` и переменные окружения
4. Проверьте права доступа к файлам

### Проблема: Ошибка подключения к базе данных

**Решение:**
1. Проверьте, что PostgreSQL запущен: `sudo systemctl status postgresql`
2. Проверьте строку подключения в `.env`
3. Проверьте права пользователя БД:
   ```bash
   sudo -u postgres psql -c "\du"
   ```

### Проблема: Порт 8000 уже занят

**Решение:**
1. Найдите процесс: `sudo lsof -i :8000`
2. Измените порт в `.env` на другой (например, 8001)
3. Перезапустите сервис: `sudo systemctl restart system_gym`

### Проблема: CORS ошибки

**Решение:**
1. Убедитесь, что в `.env` указаны правильные домены в `CORS_ORIGINS`
2. Формат: `CORS_ORIGINS=http://domain1.com,https://domain2.com`
3. Перезапустите приложение

### Проблема: Статические файлы не загружаются

**Решение:**
1. Проверьте существование папок `static/` и `templates/`
2. Проверьте права доступа: `ls -la static/ templates/`
3. Если используете Nginx, проверьте конфигурацию

---

## Резервное копирование

### Резервное копирование базы данных

```bash
# Создание бэкапа
sudo -u postgres pg_dump gym_sistem > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
sudo -u postgres psql gym_sistem < backup_20240101_120000.sql
```

### Автоматическое резервное копирование (cron)

Создайте скрипт `/opt/system_gym/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
mkdir -p $BACKUP_DIR
sudo -u postgres pg_dump gym_sistem > $BACKUP_DIR/gym_backup_$(date +%Y%m%d_%H%M%S).sql
find $BACKUP_DIR -name "gym_backup_*.sql" -mtime +7 -delete
```

Сделайте исполняемым и добавьте в cron:

```bash
chmod +x /opt/system_gym/backup.sh
crontab -e
# Добавьте строку для ежедневного бэкапа в 2:00
0 2 * * * /opt/system_gym/backup.sh
```

---

## Обновление приложения

### 1. Остановка сервиса

```bash
sudo systemctl stop system_gym
```

### 2. Резервное копирование

```bash
# Бэкап БД
sudo -u postgres pg_dump gym_sistem > backup_before_update.sql

# Бэкап кода (если используете Git)
cd /opt/system_gym
git stash
```

### 3. Обновление кода

```bash
# Если используете Git
git pull origin main

# Или загрузите новую версию вручную
```

### 4. Обновление зависимостей

```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 5. Применение миграций (если есть)

```bash
python init_database.py
```

### 6. Запуск сервиса

```bash
sudo systemctl start system_gym
sudo systemctl status system_gym
```

---

## Безопасность

### Рекомендации по безопасности:

1. **Измените пароль администратора** после первого входа
2. **Используйте сильный SECRET_KEY** (сгенерируйте случайную строку)
3. **Ограничьте CORS_ORIGINS** только вашими доменами
4. **Настройте файрвол**:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
5. **Регулярно обновляйте систему** и зависимости
6. **Используйте HTTPS** в production (Let's Encrypt)
7. **Ограничьте доступ к PostgreSQL** только с localhost
8. **Используйте отдельного пользователя** для запуска приложения

---

## Контакты и поддержка

При возникновении проблем проверьте:
- Логи приложения: `sudo journalctl -u system_gym -f`
- Логи PostgreSQL: `sudo tail -f /var/log/postgresql/postgresql-*.log`
- Логи Nginx: `sudo tail -f /var/log/nginx/error.log`

---

**Успешного развертывания! 🚀**

