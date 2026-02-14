#!/bin/bash
#
# Скрипт проверки безопасности конфигурации Claude Code
# Запусти: ./security-check.sh
#

echo "🔒 Проверка безопасности конфигурации..."
echo ""

EXIT_CODE=0
ERRORS=()
WARNINGS=()

# Функция для добавления ошибки
add_error() {
    ERRORS+=("❌ $1")
    EXIT_CODE=1
}

# Функция для добавления предупреждения
add_warning() {
    WARNINGS+=("⚠️  $1")
}

# 1. Проверка файла настроек
echo "1️⃣  Проверка .claude/settings.json..."

if [ ! -f ".claude/settings.json" ]; then
    add_error "Файл .claude/settings.json не найден!"
else
    # Проверка manual mode
    if ! grep -q '"initialPermissionMode": "manual"' .claude/settings.json; then
        add_error "initialPermissionMode должен быть 'manual'!"
    else
        echo "   ✅ Режим manual approval включен"
    fi
    
    # Проверка autoAcceptEdits
    if ! grep -q '"autoAcceptEdits": false' .claude/settings.json; then
        add_error "autoAcceptEdits должен быть false!"
    else
        echo "   ✅ Авто-подтверждение отключено"
    fi
    
    # Проверка audit log
    if ! grep -q '"auditLog"' .claude/settings.json; then
        add_warning "Audit log не настроен"
    else
        echo "   ✅ Audit log включен"
    fi
    
    # Проверка ограничений путей
    if grep -q '"allowedDirectories"' .claude/settings.json; then
        echo "   ✅ Ограничение директорий настроено"
    else
        add_warning "Нет ограничений на директории"
    fi
fi

echo ""

# 2. Проверка .gitignore
echo "2️⃣  Проверка .gitignore..."

if [ ! -f ".gitignore" ]; then
    add_error "Файл .gitignore не найден!"
else
    REQUIRED_IGNORES=(".env" "*.key" "*.pem" ".claude/audit.log")
    
    for pattern in "${REQUIRED_IGNORES[@]}"; do
        if grep -q "^$pattern" .gitignore; then
            echo "   ✅ $pattern в .gitignore"
        else
            add_warning "$pattern не найден в .gitignore"
        fi
    done
fi

echo ""

# 3. Проверка секретов в репозитории
echo "3️⃣  Проверка на наличие секретов..."

SECRETS_FOUND=0

# Проверка .env
if [ -f ".env" ]; then
    if git ls-files | grep -q "^\.env$"; then
        add_error "Файл .env отслеживается git! Исправь немедленно!"
        SECRETS_FOUND=1
    else
        echo "   ✅ .env не отслеживается"
    fi
fi

# Проверка ключей
KEY_FILES=$(find . -name "*.key" -o -name "*.pem" 2>/dev/null | grep -v node_modules | head -5)
if [ -n "$KEY_FILES" ]; then
    add_warning "Найдены файлы ключей:"
    echo "$KEY_FILES" | while read file; do
        echo "      - $file"
    done
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo "   ✅ Секреты не найдены в git"
fi

echo ""

# 4. Проверка pre-commit hook
echo "4️⃣  Проверка pre-commit hook..."

if [ -f ".git/hooks/pre-commit" ]; then
    if [ -x ".git/hooks/pre-commit" ]; then
        echo "   ✅ Pre-commit hook установлен и активен"
    else
        add_warning "Pre-commit hook не исполняемый"
        echo "   Исправить: chmod +x .git/hooks/pre-commit"
    fi
else
    add_warning "Pre-commit hook не установлен"
    echo "   Установить:"
    echo "   cp .githooks/pre-commit .git/hooks/pre-commit"
    echo "   chmod +x .git/hooks/pre-commit"
fi

echo ""

# 5. Проверка audit log
echo "5️⃣  Проверка audit log..."

if [ -f ".claude/audit.log" ]; then
    LOG_SIZE=$(stat -f%z ".claude/audit.log" 2>/dev/null || stat -c%s ".claude/audit.log" 2>/dev/null)
    LOG_LINES=$(wc -l < ".claude/audit.log")
    
    echo "   ✅ Audit log существует"
    echo "   📊 Размер: $((LOG_SIZE / 1024)) KB"
    echo "   📊 Строк: $LOG_LINES"
    
    # Проверка подозрительных операций
    SUSPICIOUS=$(grep -cE "(rm|delete|force|reset)" .claude/audit.log 2>/dev/null || echo "0")
    if [ "$SUSPICIOUS" -gt 0 ]; then
        add_warning "Обнаружено $SUSPICIOUS подозрительных операций в audit log"
    fi
else
    add_warning "Audit log не найден"
fi

echo ""

# 6. Проверка прав доступа
echo "6️⃣  Проверка прав доступа..."

if [ -f ".claude/settings.json" ]; then
    PERMS=$(stat -f%Lp ".claude/settings.json" 2>/dev/null || stat -c%a ".claude/settings.json" 2>/dev/null)
    if [ "$PERMS" = "644" ] || [ "$PERMS" = "600" ]; then
        echo "   ✅ Права доступа к настройкам корректны"
    else
        add_warning "Права доступа к .claude/settings.json: $PERMS (рекомендуется 644)"
    fi
fi

echo ""

# 7. Проверка MCP серверов
echo "7️⃣  Проверка MCP серверов..."

if [ -f ".claude/settings.json" ]; then
    # Подсчет количества серверов
    SERVER_COUNT=$(grep -c '"command":' .claude/settings.json)
    echo "   📊 Настроено серверов: $SERVER_COUNT"
    
    # Проверка на опасные серверы
    DANGEROUS_SERVERS=("puppeteer" "postgres" "redis" "github")
    for server in "${DANGEROUS_SERVERS[@]}"; do
        if grep -q "server-$server" .claude/settings.json; then
            add_warning "Обнаружен потенциально опасный сервер: $server"
        fi
    done
    
    if [ ${#WARNINGS[@]} -eq 0 ] || [[ ! " ${WARNINGS[@]} " =~ "опасный сервер" ]]; then
        echo "   ✅ Опасных серверов не обнаружено"
    fi
fi

echo ""

# Вывод результатов
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "❌ ОШИБКИ:"
    for error in "${ERRORS[@]}"; do
        echo "   $error"
    done
    echo ""
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЯ:"
    for warning in "${WARNINGS[@]}"; do
        echo "   $warning"
    done
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Проверка безопасности пройдена!"
    echo ""
    echo "Конфигурация безопасна для использования."
    exit 0
else
    echo "❌ Обнаружены проблемы безопасности!"
    echo ""
    echo "Исправь ошибки перед работой с Claude Code."
    echo ""
    echo "Полезные команды:"
    echo "   ./security-check.sh     # Перепроверить"
    echo "   cat SECURITY_PROCEDURES.md  # Прочитать процедуры"
    exit 1
fi
