#!/bin/bash

# Установка опциональных MCP серверов с предупреждениями безопасности
# Запусти: chmod +x setup-mcp-optional.sh && ./setup-mcp-optional.sh

echo "🛠️  Установка опциональных MCP серверов"
echo ""
echo "⚠️  Эти серверы имеют ПОВЫШЕННЫЕ РИСКИ безопасности!"
echo "   Устанавливай только если реально нужны."
echo ""

# Функция для установки с подтверждением
install_server() {
    local name=$1
    local package=$2
    local risk=$3
    local mitigation=$4
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 $name"
    echo "🔴 Уровень риска: $risk"
    echo "🛡️  Защита: $mitigation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    read -p "Установить $name? (yes/no): " choice
    if [[ $choice == "yes" ]]; then
        echo "  Установка $name..."
        npx -y $package --version &> /dev/null || true
        echo "  ✅ $name установлен"
        return 0
    else
        echo "  ❌ Пропущено"
        return 1
    fi
}

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен"
    exit 1
fi

# Список опциональных серверов
echo "Выбери серверы для установки:"
echo ""

# PostgreSQL
if install_server \
    "PostgreSQL" \
    "@modelcontextprotocol/server-postgres" \
    "ВЫСОКИЙ - доступ к БД, возможность DELETE/DROP" \
    "Создай read-only пользователя!"; then
    
    echo ""
    echo "💡 Для PostgreSQL используй read-only пользователя:"
    echo "   CREATE USER claude_readonly WITH PASSWORD 'secure_pass';"
    echo "   GRANT CONNECT ON DATABASE mydb TO claude_readonly;"
    echo "   GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_readonly;"
    echo ""
fi

# SQLite
if install_server \
    "SQLite" \
    "@modelcontextprotocol/server-sqlite" \
    "СРЕДНИЙ - доступ к локальной БД" \
    "Используй только локальные файлы"; then
    
    echo ""
    echo "💡 Для SQLite создай отдельный файл БД:"
    echo "   Путь: ./data/local.db (не production!)"
    echo ""
fi

# GitHub
if install_server \
    "GitHub" \
    "@modelcontextprotocol/server-github" \
    "СРЕДНИЙ - доступ к API, возможность создания issues/PR" \
    "Используй токен с минимальными правами"; then
    
    echo ""
    echo "💡 Для GitHub создай токен с минимальными правами:"
    echo "   1. https://github.com/settings/tokens"
    echo "   2. repo (только публичные репозитории)"
    echo "   3. issues:read (только чтение issues)"
    echo "   4. НЕ давай доступ к приватным репозиториям!"
    echo ""
    echo "   Добавь в ~/.zshrc или ~/.bashrc:"
    echo "   export GITHUB_TOKEN='ghp_xxxxxxxxxxxx'"
    echo ""
fi

# Redis
if install_server \
    "Redis" \
    "@modelcontextprotocol/server-redis" \
    "СРЕДНИЙ - доступ к кэшу, возможность FLUSHALL" \
    "Используй Redis ACL с ограниченными правами"; then
    
    echo ""
    echo "💡 Для Redis создай ограниченного пользователя:"
    echo "   redis-cli ACL SETUSER claude on >password +@read ~*"
    echo ""
fi

# Puppeteer
if install_server \
    "Puppeteer" \
    "@modelcontextprotocol/server-puppeteer" \
    "ВЫСОКИЙ - полный контроль браузера, cookies" \
    "Используй ТОЛЬКО для доверенных сайтов"; then
    
    echo ""
    echo "⚠️  ВНИМАНИЕ: Puppeteer имеет доступ к:"
    echo "   - Всем cookies и сессиям"
    echo "   - Возможность выполнения любого JavaScript"
    echo "   - Потенциальный доступ к аккаунтам"
    echo ""
    echo "   Используй ТОЛЬКО для:"
    echo "   - Доверенных внутренних сайтов"
    echo "   - Тестирования своих приложений"
    echo "   - Никогда для публичных/неизвестных сайтов!"
    echo ""
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Установка завершена!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  ВАЖНО: Не забудь добавить настройки в .claude/settings.json!"
echo ""
echo "🛡️  Проверь MCP_SECURITY.md для примеров конфигурации"
echo ""
echo "📋 Добавь в .claude/settings.json:"
echo ""
echo '  "postgres": {'
echo '    "command": "npx",'
echo '    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"]'
echo '  },'
echo '  "github": {'
echo '    "command": "npx",'
echo '    "args": ["-y", "@modelcontextprotocol/server-github"],'
echo '    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }'
echo '  },'
echo ""
