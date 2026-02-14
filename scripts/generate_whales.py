#!/usr/bin/env python3
"""
Generate Whales - Генератор профилей китов для стресс-тестирования
================================================================
Создает 50 уникальных профилей клиентов с:
- Уникальными характеристиками
- Историей сообщений
- Паттернами поведения
"""

import json
import random
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict

# Имена пользователей
FIRST_NAMES = [
    "Alex", "Jordan", "Casey", "Morgan", "Taylor", "Riley", "Quinn", "Avery",
    "Skyler", "Dakota", "Reese", "Finley", "Sage", "River", "Phoenix", "Blake",
    "Cameron", "Drew", "Emerson", "Hayden", "Jamie", "Kendall", "Logan", "Micah",
    "Noah", "Parker", "Remy", "Sawyer", "Spencer", "Sydney"
]

LAST_INITIALS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Психологические типы
PSYCHOTYPES = [
    "need_for_control", "identity_shift", "validation", "findom", "loneliness"
]

# Настроения
MOODS = ["angry", "generous", "impatient", "curious", "flirtatious", "desperate", "neutral"]

# Шаблоны сообщений по типу
MESSAGE_TEMPLATES = {
    "need_for_control": [
        "Tell me what to do tonight",
        "Give me instructions",
        "What should I do?",
        "Guide me through this",
        "I need you to dominate me"
    ],
    "identity_shift": [
        "I want to be a good girl",
        "Make me a sissy",
        "Transform me",
        "I want to crossdress",
        "Turn me into her"
    ],
    "validation": [
        "I love you so much",
        "You're amazing goddess",
        "I'm devoted to you",
        "My queen",
        "I'll do anything for you"
    ],
    "findom": [
        "I want to send you money",
        "Can I tip you?",
        "Want to spoil you",
        "I'll transfer now",
        "Gift for my goddess"
    ],
    "loneliness": [
        "Just want to chat",
        "Keep me company",
        "So bored today",
        "Talk to me please",
        "Feeling lonely"
    ]
}

# Базовые траты
SPEND_RANGES = {
    "low": (10, 30),
    "medium": (50, 100),
    "high": (100, 200),
    "whale": (200, 500)
}


def generate_whale_profiles(count: int = 50) -> List[Dict]:
    """Генерация списка профилей китов."""
    profiles = []
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_initial = random.choice(LAST_INITIALS)
        username = f"{first_name}{last_initial}{random.randint(10,99)}"
        
        # Определяем тип и настроение
        psychotype = random.choice(PSYCHOTYPES)
        mood = random.choice(MOODS)
        
        # Определяем уровень трат
        spend_tier = random.choices(
            ["low", "medium", "high", "whale"],
            weights=[20, 30, 30, 20]
        )[0]
        spend_range = SPEND_RANGES[spend_tier]
        weekly_spent = random.randint(spend_range[0], spend_range[1])
        
        # Генерируем историю сообщений
        messages = random.sample(MESSAGE_TEMPLATES[psychotype], k=random.randint(2, 4))
        
        profile = {
            "user_id": f"whale_{i+1:03d}",
            "username": username,
            "psychotype": psychotype,
            "mood": mood,
            "weekly_spent": weekly_spent,
            "total_spent": weekly_spent * random.randint(4, 20),  # LTV
            "messages": messages,
            "engagement_score": random.uniform(0.5, 1.0),
            "response_rate": random.uniform(0.6, 1.0),
            "last_active": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
        }
        
        profiles.append(profile)
    
    return profiles


def save_to_database(profiles: List[Dict], db_path: str = "data/user_profiles.db"):
    """Сохранение профилей в SQLite базу."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for profile in profiles:
        cursor.execute("""
            INSERT OR REPLACE INTO user_profiles 
            (user_id, username, fetishes, total_spent, weekly_spent, psychotype, messages_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            profile["user_id"],
            profile["username"],
            profile["psychotype"],
            profile["total_spent"],
            profile["weekly_spent"],
            profile["psychotype"],
            len(profile["messages"])
        ))
        
        # Добавляем историю сообщений
        for msg in profile["messages"]:
            cursor.execute("""
                INSERT INTO conversation_history 
                (user_id, message_from, message_text, psychotype_detected)
                VALUES (?, ?, ?, ?)
            """, (
                profile["user_id"],
                "user",
                msg,
                profile["psychotype"]
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Сохранено {len(profiles)} профилей в базу данных")


def save_to_json(profiles: List[Dict], filepath: str = "logs/whale_profiles.json"):
    """Сохранение профилей в JSON."""
    with open(filepath, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_profiles": len(profiles),
            "profiles": profiles
        }, f, indent=2)
    print(f"✅ Сохранено {len(profiles)} профилей в {filepath}")


def print_statistics(profiles: List[Dict]):
    """Вывод статистики по сгенерированным профилям."""
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА СГЕНЕРИРОВАННЫХ ПРОФИЛЕЙ")
    print("="*60)
    
    # По типу
    psychotype_counts = {}
    for p in profiles:
        psychotype_counts[p["psychotype"]] = psychotype_counts.get(p["psychotype"], 0) + 1
    
    print("\n🔍 По психотипу:")
    for pt, count in psychotype_counts.items():
        print(f"   {pt}: {count}")
    
    # По настроению
    mood_counts = {}
    for p in profiles:
        mood_counts[p["mood"]] = mood_counts.get(p["mood"], 0) + 1
    
    print("\n😊 По настроению:")
    for mood, count in mood_counts.items():
        print(f"   {mood}: {count}")
    
    # Финансы
    total_spent = sum(p["total_spent"] for p in profiles)
    avg_spent = total_spent / len(profiles)
    print(f"\n💰 Финансы:")
    print(f"   Общий LTV: ${total_spent:,.2f}")
    print(f"   Средний LTV: ${avg_spent:,.2f}")
    
    # По уровню трат
    tiers = {"low": 0, "medium": 0, "high": 0, "whale": 0}
    for p in profiles:
        if p["weekly_spent"] < 50:
            tiers["low"] += 1
        elif p["weekly_spent"] < 100:
            tiers["medium"] += 1
        elif p["weekly_spent"] < 200:
            tiers["high"] += 1
        else:
            tiers["whale"] += 1
    
    print(f"\n📈 По уровню трат:")
    for tier, count in tiers.items():
        print(f"   {tier}: {count} ({count/len(profiles)*100:.1f}%)")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    print("🐋 Генератор профилей китов")
    print("="*60)
    
    # Генерация
    profiles = generate_whale_profiles(50)
    
    # Сохранение
    save_to_json(profiles)
    save_to_database(profiles)
    
    # Статистика
    print_statistics(profiles)
    
    print("✅ Генерация завершена!")
