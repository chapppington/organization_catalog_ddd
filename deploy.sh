#!/bin/bash

set -e

BRANCH=${1:-master}
APP_DIR=${VPS_APP_DIR:-$(pwd)}

echo "🚀 Starting deployment of branch: $BRANCH"

cd "$APP_DIR" || exit 1

echo "📥 Fetching latest code..."
git fetch origin
git reset --hard "origin/$BRANCH"
git clean -fd

[ ! -f .env ] && { echo "❌ .env file not found!"; exit 1; }

echo "🛑 Stopping containers..."
make all-down || true

echo "🔨 Building and starting containers..."
make all

DB_USER=$(grep "^POSTGRES_USER=" .env | cut -d'=' -f2 | xargs || echo "postgres")

echo "⏳ Waiting for PostgreSQL..."
for i in {1..30}; do
    docker exec postgres pg_isready -U "$DB_USER" >/dev/null 2>&1 && break
    [ $i -eq 30 ] && { echo "❌ PostgreSQL failed to start"; exit 1; }
    sleep 2
done
echo "✅ PostgreSQL is ready!"

echo "📊 Running migrations..."
make migrate || true

echo "🧹 Cleaning up..."
docker image prune -f >/dev/null 2>&1

echo "✅ Deployment completed!"
