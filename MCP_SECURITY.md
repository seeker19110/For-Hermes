# MCP Серверы - Безопасность и Установка

## ⚠️ ВАЖНО: Безопасность MCP Серверов

**Каждый MCP сервер - это потенциальная угроза безопасности!** Серверы имеют доступ к:
- Файловой системе
- Сети
- API
- Базам данных

## 🔒 Принципы Безопасности

### 1. **Режим Manual Approval (Обязательно)**
```json
{
  "initialPermissionMode": "manual",
  "autoAcceptEdits": false
}
```
**Каждое действие требует вашего подтверждения!**

### 2. **Принцип Минимальных Привилегий**
- Устанавливайте только необходимые серверы
- Ограничивайте доступ только нужными директориями
- Используйте read-only где возможно

### 3. **Изоляция Данных**
- Никогда не храните токены в коде
- Используйте переменные окружения
- Разделяйте production и dev окружения

## 📦 Установленные Серверы

### 🟢 Безопасные (Рекомендованы)

#### 1. **Filesystem** - Доступ к файлам
```
@filesystem прочитать README.md
@filesystem найти все *.md файлы
```
**Безопасность:** ✅ Только папка проекта, запись требует подтверждения

#### 2. **Fetch** - Загрузка веб-страниц
```
@fetch https://docs.anthropic.com/claude/docs/tool-use
```
**Безопасность:** ✅ Только GET-запросы, не отправляет данные

#### 3. **Git** - Операции с Git
```
@git показать статус
@git создать коммит "Обновление документации"
```
**Безопасность:** ✅ Требует подтверждения для изменений

#### 4. **Time** - Работа со временем
```
@time текущее время в Токио
```
**Безопасность:** ✅ Только чтение, stateless

#### 5. **Sequential Thinking** - Цепочки мыслей
```
@sequentialthinking проанализируй сложную проблему шаг за шагом
```
**Безопасность:** ✅ Не сохраняет данные

#### 6. **Memory** - Локальная память
```
@memory сохрани заметку о проекте
@memory вспомни все заметки про Claude
```
**Безопасность:** ✅ Данные только локально в `~/.mcp/memory`

## 🟡 Опциональные Серверы (Устанавливать при необходимости)

### PostgreSQL - База данных ⚠️ Требует осторожности
```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"],
    "description": "Доступ к PostgreSQL (только чтение рекомендуется)"
  }
}
```
**Риски:**
- Доступ к данным
- Возможность DELETE/DROP
- **Решение:** Создай read-only пользователя

```sql
-- Создать read-only пользователя
CREATE USER claude_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO claude_readonly;
GRANT USAGE ON SCHEMA public TO claude_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_readonly;
```

### SQLite - Локальная БД
```json
{
  "sqlite": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-sqlite", "/path/to/local.db"],
    "description": "Локальная SQLite база данных"
  }
}
```
**Безопасность:** ✅ Лучше PostgreSQL - только локальный файл

### GitHub - API GitHub ⚠️ Требует токена
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
    }
  }
}
```
**Риски:**
- Доступ к приватным репозиториям
- Возможность создания issues/PR
- **Решение:** Используйте токен с минимальными правами

**Создание безопасного токена:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Выберите права:
   - ✅ `repo` (только для публичных репозиториев)
   - ❌ Не давайте доступ к приватным репозиториям без необходимости
   - ✅ `issues:read` вместо `issues:write` если только читаете

### Puppeteer - Браузер ⚠️ Высокий риск
```json
{
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
    "description": "Автоматизация браузера"
  }
}
```
**Риски:**
- Выполнение JavaScript на страницах
- Доступ к cookies/sessions
- Потенциальный доступ к аккаунтам
- **Решение:** Используйте только для доверенных сайтов

### Redis - Кэш ⚠️ Средний риск
```json
{
  "redis": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-redis", "redis://localhost:6379"]
  }
}
```
**Риски:**
- Доступ к кэшированным данным
- Возможность FLUSHALL (удаление всего)
- **Решение:** Используйте Redis ACL

```bash
# Создать пользователя с ограниченными правами
redis-cli ACL SETUSER claude_user on >password +@read ~*
```

## 🔴 Архивированные Серверы (Не рекомендуются)

Эти серверы больше не поддерживаются официально. Используйте на свой страх и риск:
- AWS KB Retrieval
- Brave Search (заменён официальным)
- EverArt
- GitLab
- Google Drive
- Google Maps
- Sentry
- Slack (теперь поддерживается Zencoder)

## 🛡️ Чеклист Безопасности

Перед установкой MCP сервера проверьте:

- [ ] Сервер из официального репозитория или доверенного источника?
- [ ] Только необходимые права доступа?
- [ ] Чувствительные данные в переменных окружения?
- [ ] Режим manual approval включён?
- [ ] Ограничен доступ к файловой системе?
- [ ] Read-only доступ где возможно?
- [ ] Логирование действий сервера?

## 🚨 Примеры Опасных Команд

**Никогда не запускайте без проверки:**
```
@filesystem удалить всё в папке /
@postgres выполни DROP DATABASE production
@github создай 1000 issues
@redis выполни FLUSHALL
```

**Всегда проверяйте перед подтверждением!**

## 🔐 Рекомендуемая Конфигурация

Для безопасной работы используйте только:
```json
{
  "filesystem": { "только папка проекта" },
  "fetch": { "только GET запросы" },
  "git": { "без автопуша" },
  "time": { "read-only" },
  "sequentialthinking": { "stateless" }
}
```

Другие серверы добавляйте только когда реально нужны!

## 📞 Что делать при подозрении?

1. **Немедленно отключите сервер**
   - Удалите из `.claude/settings.json`
   - Перезагрузите VS Code

2. **Проверьте логи**
   ```bash
   cat ~/.claude/logs/mcp-servers.log
   ```

3. **Проверьте изменения**
   ```bash
   git status
   git diff
   ```

4. **Отзовите токены**
   - GitHub: Settings → Developer settings → Tokens
   - PostgreSQL: Отзовите права пользователя

5. **Сообщите о проблеме**
   - MCP Security: https://github.com/modelcontextprotocol/security

## 📚 Полезные Ссылки

- [Официальные MCP серверы](https://github.com/modelcontextprotocol/servers)
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/concepts/security)
- [Claude Code Security](https://docs.anthropic.com/claude-code/security)

---

**Помните:** Безопасность - ваша ответственность. MCP серверы - это мощные инструменты, но с большой силой приходит большая ответственность! 🔒
