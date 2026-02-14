# OpenClaw Enterprise 🤖🦞

Автономный AI-агент для монетизации аудитории на платформе LoyalFans.

## 🚀 Быстрый старт

### Требования
- Node.js 18+
- Python 3.10+ (для whisper-local)
- OpenRouter API ключ

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/your-org/openclaw-enterprise.git
cd openclaw-enterprise

# Копирование переменных окружения
cp .env.example .env

# Установка зависимостей
npm install

# Запуск
npm run start
```

### Настройка MCP серверов

1. **browseract-pro** — автоматизация LoyalFans
2. **whisper-local** — обработка аудио

См. [MCP_SETUP.md](./MCP_SETUP.md) для детальной инструкции.

## 📁 Структура проекта

```
openclaw-enterprise/
├── agents/           # AI-агенты для разных задач
├── workflows/       # YAML-определения рабочих процессов
├── mcp/             # MCP-конфигурации
├── scripts/         # Вспомогательные скрипты
├── docs/            # Документация
├── claw_config.yaml # Основная конфигурация
└── RULES.md         # Боевой скрипт продаж
```

## 🎮 Команды

| Команда          | Описание                                  |
| ---------------- | ----------------------------------------- |
| `START`          | Начать рабочий цикл агента                |
| `LEARN`          | Активировать обучение через whisper-local |
| `ENGAGE [user]`  | Начать диалог с подписчиком               |
| `CONTENT [type]` | Создать контент                           |

## 🔧 Конфигурация

Основной файл конфигурации: [`claw_config.yaml`](./claw_config.yaml)

### MCP интеграции

- **browseract-pro**: Автоматизация LoyalFans
  - Отправка/получение сообщений
  - Публикация контента
  - PPV создание
  - Аналитика

- **whisper-local**: Обработка аудио
  - Транскрибирование
  - Анализ тональности
  - Извлечение ключевых слов
  - Обучение паттернам

## 📋 Требования 12-Factor

Проект следует методологии 12-Factor App:

1. ✅ **Codebase** — один репозиторий
2. ✅ **Dependencies** — явные зависимости
3. ✅ **Config** — конфигурация в окружении
4. ✅ **Backing Services** — MCP как сервисы
5. ✅ **Build, release, run** — разделение стадий
6. ✅ **Processes** — stateless состояние
7. ✅ **Port binding** — порты для сервисов
8. ✅ **Concurrency** — горизонтальное масштабирование
9. ✅ **Disposability** — быстрый старт/останов
10. ✅ **Dev/prod parity** — контейнеризация
11. ✅ **Logs** — структурное логирование
12. ✅ **Admin processes** — миграции и т.д.

## 🛡️ Безопасность

- Шифрование AES-256-GCM
- Управление секретами через env
- Rate limiting
- Логирование действий

## 📄 Лицензия

MIT License

---

*OpenClaw Enterprise v1.0.0*
