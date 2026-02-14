#!/bin/bash
#
# Диагностика и исправление Claude Code в VS Code
# Запусти: ./fix-claude-vscode.sh
#

echo "🔧 Диагностика Claude Code в VS Code..."
echo ""

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# 1. Проверка VS Code
echo "1️⃣  Проверка VS Code..."
if command -v code &> /dev/null; then
    VSCODE_VERSION=$(code --version | head -1)
    echo "   ✅ VS Code найден: $VSCODE_VERSION"
else
    echo "   ${RED}❌ VS Code не найден в PATH${NC}"
    ERRORS=$((ERRORS+1))
fi

# 2. Проверка расширения Claude Code
echo ""
echo "2️⃣  Проверка расширения Claude Code..."

EXTENSION_DIR=""
if [ -d "$HOME/.vscode/extensions" ]; then
    EXTENSION_DIR=$(find "$HOME/.vscode/extensions" -name "anthropic.claude-code-*" -type d | head -1)
fi

if [ -n "$EXTENSION_DIR" ]; then
    echo "   ✅ Расширение найдено:"
    echo "      $EXTENSION_DIR"
    
    # Проверка версии
    VERSION=$(basename "$EXTENSION_DIR" | sed 's/anthropic.claude-code-//')
    echo "      Версия: $VERSION"
else
    echo "   ${RED}❌ Расширение Claude Code не установлено!${NC}"
    echo "      Установи из VS Code Marketplace"
    ERRORS=$((ERRORS+1))
fi

# 3. Проверка CLI бинарника
echo ""
echo "3️⃣  Проверка CLI бинарника..."

CLI_BINARY=""
if [ -n "$EXTENSION_DIR" ]; then
    CLI_BINARY=$(find "$EXTENSION_DIR" -name "claude" -type f | head -1)
fi

if [ -n "$CLI_BINARY" ]; then
    echo "   ✅ CLI бинарник найден:"
    echo "      $CLI_BINARY"
    
    # Проверяем версию
    CLI_VERSION=$($CLI_BINARY --version 2>/dev/null)
    if [ -n "$CLI_VERSION" ]; then
        echo "      Версия CLI: $CLI_VERSION"
    fi
else
    echo "   ${RED}❌ CLI бинарник не найден!${NC}"
    ERRORS=$((ERRORS+1))
fi

# 4. Проверка PATH
echo ""
echo "4️⃣  Проверка PATH..."

if command -v claude &> /dev/null; then
    CLAUDE_PATH=$(which claude)
    echo "   ✅ Claude найден в PATH:"
    echo "      $CLAUDE_PATH"
    
    CLAUDE_VERSION=$(claude --version 2>/dev/null)
    echo "      Версия: $CLAUDE_VERSION"
else
    echo "   ${YELLOW}⚠️  Claude не найден в PATH${NC}"
    echo "      Исправляю..."
    
    # Создаем symlink
    if [ -n "$CLI_BINARY" ]; then
        mkdir -p "$HOME/.local/bin"
        ln -sf "$CLI_BINARY" "$HOME/.local/bin/claude"
        
        if [ -f "$HOME/.local/bin/claude" ]; then
            echo "   ✅ Создана ссылка: ~/.local/bin/claude"
            
            # Добавляем в PATH
            if ! grep -q "$HOME/.local/bin" "$HOME/.zshrc" 2>/dev/null && \
               ! grep -q "$HOME/.local/bin" "$HOME/.bashrc" 2>/dev/null; then
                echo "" >> "$HOME/.zshrc"
                echo "# Claude Code CLI" >> "$HOME/.zshrc"
                echo 'export PATH="\$HOME/.local/bin:\$PATH"' >> "$HOME/.zshrc"
                echo "   ✅ PATH добавлен в ~/.zshrc"
            fi
        fi
    fi
fi

# 5. Проверка настроек VS Code
echo ""
echo "5️⃣  Проверка настроек VS Code..."

if [ -f ".claude/settings.json" ]; then
    echo "   ✅ Найдены настройки проекта: .claude/settings.json"
    
    # Проверка manual mode
    if grep -q '"initialPermissionMode": "manual"' .claude/settings.json; then
        echo "   ✅ Режим manual approval включен"
    else
        echo "   ${YELLOW}⚠️  Режим manual approval не найден${NC}"
    fi
else
    echo "   ${YELLOW}⚠️  Настройки проекта не найдены${NC}"
    echo "      Создай: .claude/settings.json"
fi

# 6. Проверка .gitignore
echo ""
echo "6️⃣  Проверка .gitignore..."

if [ -f ".gitignore" ]; then
    if grep -q ".env" .gitignore; then
        echo "   ✅ .env в .gitignore"
    else
        echo "   ${YELLOW}⚠️  .env не в .gitignore${NC}"
    fi
else
    echo "   ${YELLOW}⚠️  Файл .gitignore не найден${NC}"
fi

# 7. Пробный запуск
echo ""
echo "7️⃣  Пробный запуск Claude..."

export PATH="$HOME/.local/bin:$PATH"

if command -v claude &> /dev/null; then
    echo "   ✅ Claude работает!"
    claude --version
else
    echo "   ${RED}❌ Claude не запускается${NC}"
    ERRORS=$((ERRORS+1))
fi

# Итог
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "${GREEN}✅ Все проверки пройдены!${NC}"
    echo ""
    echo "📋 Что делать дальше:"
    echo "   1. Перезагрузи VS Code (Cmd+Shift+P → Reload Window)"
    echo "   2. Открой Claude Code (Cmd+Shift+P → Claude Code: Open)"
    echo "   3. Или нажми Cmd+Shift+J (если настроено)"
    echo ""
    echo "⚡ Быстрые команды:"
    echo "   Cmd+Shift+P → Claude Code: Open"
    echo "   / - открыть меню команд"
    echo ""
else
    echo "${RED}❌ Обнаружены проблемы ($ERRORS)${NC}"
    echo ""
    echo "📋 Что делать:"
    echo "   1. Перезагрузи VS Code"
    echo "   2. Проверь, что расширение установлено"
    echo "   3. Перезапусти терминал для обновления PATH"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Полезные команды:"
echo "   claude --version     # Проверить версию"
echo "   claude --help        # Справка"
echo "   which claude         # Где находится CLI"
echo ""
