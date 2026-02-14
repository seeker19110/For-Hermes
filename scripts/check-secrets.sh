#!/bin/bash
# Secret Scanner for OpenClaw Enterprise
# Checks for potential secret leaks before commit

echo "🔍 Проверка на утечку секретов..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track if we found any issues
FOUND_ISSUES=0

# Check 1: .env files
echo -e "\n📁 Проверка .env файлов..."
if git ls-files | grep -E "\.env$" > /dev/null 2>&1; then
    echo -e "${RED}❌ НАЙДЕНЫ .env файлы в git:${NC}"
    git ls-files | grep -E "\.env$"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ .env файлы не найдены в git${NC}"
fi

# Check 2: Potential Telegram tokens
echo -e "\n🔑 Проверка Telegram токенов..."
if git grep -l "TELEGRAM_TOKEN=[0-9]" -- "*.env" "*.py" "*.yaml" "*.yml" 2>/dev/null; then
    echo -e "${RED}❌ Найдены реальные Telegram токены!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ Telegram токены не найдены${NC}"
fi

# Check 3: Private keys
echo -e "\n🔐 Проверка приватных ключей..."
if git ls-files | grep -E "\.(key|pem|p12|pfx)$" > /dev/null 2>&1; then
    echo -e "${RED}❌ Найдены ключевые файлы:${NC}"
    git ls-files | grep -E "\.(key|pem|p12|pfx)$"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ Ключевые файлы не найдены${NC}"
fi

# Check 4: AWS credentials
echo -e "\n☁️  Проверка AWS ключей..."
if git grep -E "(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16})" -- "*.env" "*.py" 2>/dev/null; then
    echo -e "${RED}❌ Найдены AWS Access Keys!${NC}"
    FOUND_ISSUES=1
else
    echo -e "${GREEN}✅ AWS ключи не найдены${NC}"
fi

# Check 5: Passwords in code
echo -e "\n🔒 Проверка паролей в коде..."
SUSPICIOUS=$(git grep -E "(password|passwd|pwd)\s*=\s*[\"'][^\"']+[\"']" -- "*.py" 2>/dev/null | grep -v "your_" | grep -v "example" | grep -v "test_" | head -5)
if [ ! -z "$SUSPICIOUS" ]; then
    echo -e "${YELLOW}⚠️  Подозрительные строки (возможно, ложные срабатывания):${NC}"
    echo "$SUSPICIOUS"
else
    echo -e "${GREEN}✅ Пароли в коде не найдены${NC}"
fi

# Check 6: .env.example exists
echo -e "\n📋 Проверка шаблона .env.example..."
if [ -f "openclaw-enterprise/.env.example" ]; then
    echo -e "${GREEN}✅ .env.example существует${NC}"
else
    echo -e "${RED}❌ .env.example отсутствует!${NC}"
    FOUND_ISSUES=1
fi

# Summary
echo -e "\n================================"
if [ $FOUND_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ Проверка пройдена! Секретов не найдено.${NC}"
    exit 0
else
    echo -e "${RED}❌ НАЙДЕНЫ ПРОБЛЕМЫ!${NC}"
    echo -e "${YELLOW}Исправьте их перед коммитом.${NC}"
    exit 1
fi
