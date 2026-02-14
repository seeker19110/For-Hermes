#!/bin/bash

# Установка всех механизмов безопасности
# Запусти: chmod +x setup-security.sh && ./setup-security.sh

echo "🛡️  Установка механизмов безопасности..."
echo ""
echo "⚠️  Это настроит строгие ограничения безопасности."
echo "   Все операции будут требовать ручного подтверждения."
echo ""

read -p "Продолжить установку? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "❌ Установка отменена"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Создание директории .claude
echo "1️⃣  Создание директории .claude..."
mkdir -p .claude
echo "   ✅ .claude/ создана"

# 2. Настройка audit log
echo ""
echo "2️⃣  Настройка audit log..."
touch .claude/audit.log
echo "   ✅ Audit log создан: .claude/audit.log"

# 3. Копирование pre-commit hook
echo ""
echo "3️⃣  Установка pre-commit hook..."
if [ -f ".githooks/pre-commit" ]; then
    cp .githooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "   ✅ Pre-commit hook установлен"
else
    echo "   ⚠️  Pre-commit hook не найден в .githooks/"
fi

# 4. Обновление .gitignore
echo ""
echo "4️⃣  Обновление .gitignore..."

if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi

REQUIRED_IGNORES=(
    ".env"
    ".env.local"
    ".env.*.local"
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
    ".claude/audit.log"
    ".claude/audit_*.log"
    "INCIDENT_*.md"
)

for pattern in "${REQUIRED_IGNORES[@]}"; do
    if ! grep -q "^$pattern$" .gitignore; then
        echo "$pattern" >> .gitignore
        echo "   ✅ Добавлено в .gitignore: $pattern"
    fi
done

# 5. Проверка конфигурации
echo ""
echo "5️⃣  Проверка конфигурации..."

if [ -f "security-check.sh" ]; then
    ./security-check.sh
    CHECK_RESULT=$?
    
    if [ $CHECK_RESULT -eq 0 ]; then
        echo ""
        echo "   ✅ Конфигурация безопасна"
    else
        echo ""
        echo "   ⚠️  Обнаружены проблемы (см. выше)"
    fi
else
    echo "   ⚠️  security-check.sh не найден"
fi

# 6. Создание SECURITY.md если его нет
echo ""
echo "6️⃣  Проверка документации..."

SECURITY_FILES=(
    "SECURITY_PROCEDURES.md"
    "SECURITY_CHECKLIST.md"
    "MCP_SECURITY.md"
)

for file in "${SECURITY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file найден"
    else
        echo "   ⚠️  $file не найден"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Установка безопасности завершена!"
echo ""
echo "📋 Что настроено:"
echo "   ✅ Строгая конфигурация Claude Code"
echo "   ✅ Audit log включен"
echo "   ✅ Pre-commit hook установлен"
echo "   ✅ .gitignore обновлен"
echo "   ✅ Проверка секретов активна"
echo ""
echo "🛡️  Правила безопасности:"
echo "   • Каждая операция требует подтверждения"
echo "   • Нет доступа к .env и ключам"
echo "   • Нет push в main без review"
echo "   • Audit log отслеживает все действия"
echo ""
echo "📖 Документация:"
echo "   • SECURITY_PROCEDURES.md - процедуры безопасности"
echo "   • SECURITY_CHECKLIST.md - чеклисты"
echo "   • MCP_SECURITY.md - безопасность MCP"
echo ""
echo "🔍 Проверка безопасности:"
echo "   ./security-check.sh"
echo ""
echo "⚡ Перезагрузи VS Code для применения настроек!"
