# 🔐 Настройка Окружения

## Быстрый Старт

### 1. Получите Токен Telegram
```
1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте: /newbot
4. Следуйте инструкциям
5. Получите токен: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 2. Узнайте Свой ID
```
1. Найдите @userinfobot в Telegram
2. Отправьте любое сообщение
3. Получите ID: 123456789
```

### 3. Создайте .env
```bash
cd openclaw-enterprise
cp .env.example .env
nano .env  # или используйте редактор
```

### 4. Заполните Переменные
```env
# Telegram (обязательно)
TELEGRAM_TOKEN=your_new_bot_token_here
TELEGRAM_ADMIN_ID=your_user_id_here

# LoyalFans (если нужно)
LOYALFANS_USERNAME=your_username
LOYALFANS_PASSWORD=your_password

# Остальные по необходимости...
```

### 5. Проверьте Безопасность
```bash
# Из корня проекта
./scripts/check-secrets.sh
```

Должно показать: ✅ Проверка пройдена!

---

## ⚠️ Важные Правила

### ❌ НИКОГДА не коммитьте:
- `.env` файлы
- Реальные токены и пароли
- API ключи
- Приватные ключи

### ✅ Всегда проверяйте перед коммитом:
```bash
./scripts/check-secrets.sh
git status
git diff --cached
```

### 🔄 Если нужно добавить новую переменную:
1. Добавьте в `.env` (реальное значение)
2. Добавьте в `.env.example` (пример с placeholder)
3. Обновите документацию
4. Коммитьте только `.env.example`!

---

## 🛠️ Для Разработчиков

### Проверка перед коммитом (pre-commit hook)
```bash
# Установите hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./scripts/check-secrets.sh || exit 1
EOF
chmod +x .git/hooks/pre-commit
```

### Тестовые значения
Для разработки используйте тестовые данные:
```env
TELEGRAM_TOKEN=test_token_12345
TELEGRAM_ADMIN_ID=123456789
LOYALFANS_USERNAME=test_user
LOYALFANS_PASSWORD=test_pass
```

---

## 🆘 Проблемы?

### Ошибка: "TELEGRAM_TOKEN не найден"
```bash
# Проверьте что файл существует
ls -la openclaw-enterprise/.env

# Проверьте содержимое
cat openclaw-enterprise/.env | grep TELEGRAM
```

### Ошибка: "Permission denied" для скрипта
```bash
chmod +x scripts/check-secrets.sh
```

---

**Последнее обновление**: 2024-02-14
**Статус**: Актуально после инцидента с утечкой токена
