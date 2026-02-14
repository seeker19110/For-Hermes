#!/bin/bash

# Скрипт установки MCP серверов для 12-factor agents проекта
# Запусти: chmod +x setup-mcp.sh && ./setup-mcp.sh

echo "🚀 Установка MCP серверов для 12-factor agents..."
echo ""

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Установи его с https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js найден: $(node --version)"

# Проверка наличия npm/npx
if ! command -v npx &> /dev/null; then
    echo "📦 Установка npx..."
    npm install -g npx
fi

echo "✅ npx найден"

# Проверка наличия uv (для uvx)
if ! command -v uvx &> /dev/null; then
    echo "📦 Установка uv..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        # Linux
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uvx найден"
echo ""

# Установка MCP серверов
echo "📥 Установка MCP серверов..."

# Filesystem
echo "  - Filesystem MCP сервер..."
npx -y @modelcontextprotocol/server-filesystem --version &> /dev/null || true

# Fetch
echo "  - Fetch MCP сервер..."
uvx mcp-server-fetch --version &> /dev/null || true

# Git
echo "  - Git MCP сервер..."
uvx mcp-server-git --version &> /dev/null || true

echo ""
echo "✅ MCP серверы установлены!"
echo ""

# Создание директории .claude если её нет
mkdir -p .claude

# Проверка существования settings.json
if [ ! -f ".claude/settings.json" ]; then
    echo "📝 Создание .claude/settings.json..."
    cat > .claude/settings.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "initialPermissionMode": "manual",
  "allowedTools": ["Read", "Edit", "Bash", "Glob", "Grep"],
  "autoAcceptEdits": false,
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "$(pwd)"],
      "description": "Доступ к файлам проекта"
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "description": "Загрузка веб-страниц"
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"],
      "description": "Операции с Git"
    }
  }
}
EOF
    echo "✅ Файл настроек создан: .claude/settings.json"
else
    echo "⚠️  Файл .claude/settings.json уже существует"
    echo "   Проверь MCP_SETUP.md для ручной настройки"
fi

echo ""
echo "🎉 Готово! MCP серверы настроены."
echo ""
echo "📋 Что дальше:"
echo "   1. Перезагрузи VS Code"
echo "   2. Открой командное меню: /"
echo "   3. Выбери 'Refresh MCP Servers'"
echo "   4. Используй @filesystem, @fetch, @git в чате"
echo ""
echo "📖 Подробная документация: MCP_SETUP.md"
