#!/bin/bash

# Скрипт для деплоя на VPS
# Использование: ./deploy.sh [branch]
# По умолчанию деплоится ветка master

set -e

BRANCH=${1:-master}
APP_DIR=${VPS_APP_DIR:-$(pwd)}

echo "🚀 Starting deployment of branch: $BRANCH"

# Переходим в директорию проекта
cd "$APP_DIR" || {
    echo "❌ Directory $APP_DIR not found!"
    exit 1
}

# Обновляем код из репозитория
# (При запуске через GitHub Actions код уже обновлен, но повторное обновление безопасно)
echo "📥 Fetching latest code..."
git fetch origin
git reset --hard "origin/$BRANCH"
git clean -fd

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create .env file before deployment."
    exit 1
fi

# Останавливаем старые контейнеры
echo "🛑 Stopping old containers..."
docker compose -f docker_compose/storages.yaml -f docker_compose/app.yaml --env-file .env down || true

# Собираем и запускаем контейнеры
echo "🔨 Building and starting containers..."
docker compose -f docker_compose/storages.yaml -f docker_compose/app.yaml --env-file .env up --build -d

# Читаем переменные окружения из .env заранее
DB_NAME=$(grep -E "^POSTGRES_DB=" .env 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "organization_catalog")
DB_USER=$(grep -E "^POSTGRES_USER=" .env 2>/dev/null | cut -d '=' -f2 | tr -d '"' | tr -d "'" || echo "postgres")

# Удаляем пробелы
DB_NAME=$(echo "$DB_NAME" | xargs)
DB_USER=$(echo "$DB_USER" | xargs)

# Ждем пока PostgreSQL будет готов
echo "⏳ Waiting for PostgreSQL to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker exec postgres pg_isready -U "$DB_USER" > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "   Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ PostgreSQL failed to become ready after $MAX_ATTEMPTS attempts"
    exit 1
fi

# Создаем базу данных, если её нет
echo "🔍 Checking if database '$DB_NAME' exists..."
if ! docker exec postgres psql -U "$DB_USER" -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "📦 Creating database '$DB_NAME'..."
    docker exec postgres psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || {
        echo "⚠️  Failed to create database, but continuing..."
    }
else
    echo "✅ Database '$DB_NAME' already exists"
fi

# Применяем миграции
echo "📊 Running database migrations..."
docker exec main-app alembic upgrade head || {
    echo "⚠️  Migration failed, but continuing..."
}

# Очищаем старые Docker образы
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

# Проверяем статус контейнеров
echo "✅ Checking container status..."
docker ps --filter "name=main-app" --format "table {{.Names}}\t{{.Status}}"

echo "🎉 Deployment completed successfully!"

