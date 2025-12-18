@echo off
REM Скрипт для запуска приложения на Windows

echo === Запуск системы управления тренажерным залом ===

REM Проверка виртуального окружения
if not exist "venv" (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активация виртуального окружения
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Проверка зависимостей
if not exist "venv\Scripts\uvicorn.exe" (
    echo Установка зависимостей...
    pip install --upgrade pip
    pip install -r requirements.txt
)

REM Проверка файла .env
if not exist ".env" (
    echo Файл .env не найден. Создание из примера...
    if exist "env.example" (
        copy env.example .env
        echo ВАЖНО: Отредактируйте файл .env перед запуском!
    ) else (
        echo Ошибка: файл env.example не найден!
        pause
        exit /b 1
    )
)

REM Запуск приложения
echo Запуск приложения...
echo Приложение будет доступно по адресу: http://localhost:8000
echo Документация API: http://localhost:8000/api/docs
echo.

uvicorn scr.main:app --host 0.0.0.0 --port 8000 --reload

pause

