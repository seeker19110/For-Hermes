# MCP Серверы для 12-Factor Agents

⚠️ **ВАЖНО: Прочитай [MCP_SECURITY.md](MCP_SECURITY.md) перед установкой!**

Этот проект использует Model Context Protocol (MCP) серверы для расширения возможностей Claude Code.

## Что такое MCP?

MCP (Model Context Protocol) позволяет Claude взаимодействовать с внешними инструментами:
- Файловая система
- GitHub
- Базы данных
- API
- И многое другое

## Установленные MCP Серверы

### 1. Filesystem (Файловая система)
**Назначение:** Позволяет Claude читать и записывать файлы проекта

**Использование:**
```
@filesystem прочитай файл README.md
@filesystem покажи содержимое папки content/
@filesystem создай новый файл
```

**Команды:**
- `read_file` - Чтение файла
- `write_file` - Запись файла
- `list_directory` - Список файлов
- `search_files` - Поиск в файлах

### 2. Fetch (Загрузка веб-страниц)
**Назначение:** Загружает веб-страницы для анализа

**Использование:**
```
@fetch https://docs.anthropic.com/claude/docs/tool-use
@fetch загрузи документацию по MCP с https://github.com/modelcontextprotocol/servers
```

### 3. Git (Операции с Git)
**Назначение:** Выполняет git-команды

**Использование:**
```
@git покажи текущий статус
@git какие файлы изменены?
@git создай коммит с сообщением "Обновил документацию"
```

**Команды:**
- `git_status` - Статус репозитория
- `git_log` - История коммитов
- `git_diff` - Изменения
- `git_commit` - Создание коммита

## Как добавить новый MCP сервер

### Пример: GitHub MCP Server

1. **Получи токен GitHub:**
   - Зайди в Settings → Developer settings → Personal access tokens
   - Создай токен с правами `repo`

2. **Добавь в `.claude/settings.json`:**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
```

3. **Используй:**
```
@github создай issue "Добавить примеры кода"
@github найди все открытые PR
@github поищи код с "Claude" в репозитории
```

### Пример: PostgreSQL MCP Server

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_URL": "postgresql://user:pass@localhost/dbname"
      }
    }
  }
}
```

**Использование:**
```
@postgres выполни запрос "SELECT * FROM agents WHERE status='active'"
@postgres покажи структуру таблицы deployments
```

## Полезные MCP серверы для проекта

### Для работы с документацией:
```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

### Для работы с SQLite:
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"]
    }
  }
}
```

### Для работы с Slack:
```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-...",
        "SLACK_TEAM_ID": "T..."
      }
    }
  }
}
```

## Примеры использования в проекте

### Анализ кода:
```
@filesystem найди все файлы с расширением .md в папке content/
@filesystem прочитай factor-01-natural-language-to-tool-calls.md
@git покажи какие изменения были в последнем коммите
```

### Исследование:
```
@fetch загрузи документацию Anthropic о tool use
@filesystem сравни factor-01.md и factor-02.md
```

### Автоматизация:
```
@git создай коммит всех изменений с сообщением "Добавлены примеры Claude"
@git запушь ветку claude/add-claude-documentation-ySPb6
```

## Устранение неполадок

### Сервер не запускается?
1. Проверь, что Node.js установлен: `node --version`
2. Установи npx: `npm install -g npx`
3. Перезагрузи VS Code

### Ошибка доступа к файлам?
- Убедись, что путь в `args` правильный
- Проверь права доступа к файлам

### MCP сервер не виден?
1. Открой командное меню: `/`
2. Выбери "Refresh MCP Servers"
3. Или перезагрузи VS Code

## Дополнительные ресурсы

- [Официальные MCP серверы](https://github.com/modelcontextprotocol/servers)
- [Документация MCP](https://modelcontextprotocol.io/)
- [Создание собственного MCP сервера](https://modelcontextprotocol.io/quickstart/server)

---

**Примечание:** MCP серверы работают только в режиме manual approval. Каждое действие требует твоего подтверждения для безопасности.

**🛡️ Безопасность:**
- [Руководство по безопасности](MCP_SECURITY.md) - обязательно к прочтению!
- [Опциональные серверы](setup-mcp-optional.sh) - устанавливай только нужные
- Все токены в `.env` файле (не в коде!)
