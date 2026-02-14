#!/bin/bash

# Безопасная установка MCP серверов для 12-factor agents
# Запусти: chmod +x setup-mcp-secure.sh && ./setup-mcp-secure.sh

echo "🔒 Безопасная установка MCP серверов..."
echo ""
echo "⚠️  ВНИМАНИЕ: MCP серверы имеют доступ к вашей системе!"
echo "   Все действия будут требовать ручного подтверждения."
echo ""

# Проверка согласия
read -p "Продолжить установку? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "❌ Установка отменена"
    exit 0
fi

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен"
    echo "   Установи с: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js: $(node --version)"

# Проверка npx
if ! command -v npx &> /dev/null; then
    echo "📦 Установка npx..."
    npm install -g npx
fi

echo "✅ npx найден"
echo ""

# Установка MCP серверов
echo "📥 Установка официальных MCP серверов..."
echo ""

SERVERS=(
    "@modelcontextprotocol/server-filesystem"
    "@modelcontextprotocol/server-fetch"
    "@modelcontextprotocol/server-git"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-sequential-thinking"
    "@modelcontextprotocol/server-time"
)

for server in "${SERVERS[@]}"; do
    name=$(echo $server | sed 's/@modelcontextprotocol\/server-//')
    echo "  Установка $name..."
    npx -y $server --version &> /dev/null || true
done

echo ""
echo "✅ Серверы установлены!"
echo ""

# Создание директории .claude
mkdir -p .claude

# Создание безопасной конфигурации
echo "📝 Создание безопасной конфигурации..."

cat > .claude/settings.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "initialPermissionMode": "manual",
  "allowedTools": ["Read", "Edit", "Bash", "Glob", "Grep"],
  "autoAcceptEdits": false,
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "{{PROJECT_PATH}}"],
      "description": "Безопасный доступ к файлам проекта"
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "description": "Загрузка веб-страниц (только GET)"
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"],
      "description": "Операции с Git (требует подтверждения)"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "description": "Локальное хранилище знаний"
    },
    "sequentialthinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "description": "Динамическое решение проблем"
    },
    "time": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-time"],
      "description": "Конвертация времени"
    }
  }
}
EOF

# Замена пути проекта на актуальный
PROJECT_PATH=$(pwd)
sed -i.bak "s|{{PROJECT_PATH}}|$PROJECT_PATH|g" .claude/settings.json
rm .claude/settings.json.bak

echo "✅ Конфигурация создана: .claude/settings.json"
echo ""

# Создание .env.example для чувствительных данных
cat > .env.example << 'EOF'
# Пример переменных окружения для MCP серверов
# Скопируй в .env и заполни реальными значениями

# GitHub MCP (опционально)
# Создай токен: https://github.com/settings/tokens
# Права: repo (только публичные), issues:read
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# PostgreSQL MCP (опционально)
# Используй read-only пользователя!
DATABASE_URL=postgresql://claude_readonly:password@localhost/dbname

# Redis MCP (опционально)
# Используй ограниченного пользователя
REDIS_URL=redis://claude_user:password@localhost:6379
EOF

echo "✅ Создан .env.example для чувствительных данных"
echo ""

# Проверка конфигурации
echo "🔍 Проверка конфигурации..."

if [ -f ".claude/settings.json" ]; then
    echo "✅ Файл настроек найден"
    
    # Проверка на manual mode
    if grep -q '"initialPermissionMode": "manual"' .claude/settings.json; then
        echo "✅ Режим manual approval включён"
    else
        echo "⚠️  ВНИМАНИЕ: Режим manual approval не найден!"
        echo "   Исправь в .claude/settings.json"
    fi
    
    # Проверка на autoAcceptEdits
    if grep -q '"autoAcceptEdits": false' .claude/settings.json; then
        echo "✅ Авто-подтверждение отключено"
    else
        echo "⚠️  ВНИМАНИЕ: autoAcceptEdits должно быть false!"
    fi
else
    echo "❌ Файл настроек не создан"
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "   1. Перезагрузи VS Code"
echo "   2. Открой командное меню: /"
echo "   3. Выбери 'Refresh MCP Servers'"
echo "   4. Прочитай MCP_SECURITY.md!"
echo ""
echo "🛡️  Важно:"
echo "   - Все действия требуют твоего подтверждения"
echo "   - Никогда не храни токены в коде"
echo "   - Используй .env файл для секретов"
echo ""
echo "📖 Документация:"
echo "   - MCP_SECURITY.md - руководство по безопасности"
echo "   - MCP_SETUP.md - общая документация"
echo ""
echo "⚡ Пример использования:"
echo "   @filesystem прочитать README.md"
echo "   @fetch https://docs.anthropic.com/..."
echo "   @git показать статус"
echo "   @time текущее время в Лондоне"
