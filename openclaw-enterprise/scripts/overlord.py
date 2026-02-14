#!/usr/bin/env python3
"""
OVERLORD Engine - Сверх-Интеллект и Самообучение
================================================
Блоки 6-10: Шаги 41-80

Блок 6: Сверх-Интеллект и Самообучение (41-48)
- A/B Test Engine
- Neural Payment Prediction
- Psychological Profile Deepening
- Autonomous Script Evolution
- Deep Memory Retrieval
- Competitor Emulation
- Semantic Drift Detection
- Reinforcement Learning Loop
"""

import json
import random
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import os


# ============================================================================
# БЛОК 6: СВЕРХ-ИНТЕЛЛЕКТ И САМООБУЧЕНИЕ
# ============================================================================

@dataclass
class ABTest:
    """A/B тест."""
    test_id: str
    name: str
    variant_a: Dict  # Тактика A
    variant_b: Dict  # Тактика B
    target_audience: List[str]  # ID пользователей
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    winner: Optional[str] = None
    metrics_a: Dict = field(default_factory=lambda: {'conversions': 0, 'revenue': 0, 'engagement': 0})
    metrics_b: Dict = field(default_factory=lambda: {'conversions': 0, 'revenue': 0, 'engagement': 0})


class ABTestEngine:
    """
    A/B Test Engine - Система одновременного тестирования тактик.
    """
    
    def __init__(self):
        self.tests: Dict[str, ABTest] = {}
        self.user_assignments: Dict[str, str] = {}  # user_id -> test_id + variant
    
    def create_test(self, test_id: str, name: str, variant_a: Dict, variant_b: Dict,
                  target_audience: List[str]) -> str:
        """Создать A/B тест."""
        test = ABTest(
            test_id=test_id,
            name=name,
            variant_a=variant_a,
            variant_b=variant_b,
            target_audience=target_audience
        )
        self.tests[test_id] = test
        
        # Назначаем пользователей
        for i, user_id in enumerate(target_audience):
            variant = 'a' if i % 2 == 0 else 'b'
            self.user_assignments[user_id] = f"{test_id}:{variant}"
        
        return test_id
    
    def get_variant(self, user_id: str) -> Optional[Tuple[str, Dict]]:
        """Получить вариант для пользователя."""
        assignment = self.user_assignments.get(user_id)
        if not assignment:
            return None
        
        test_id, variant = assignment.split(':')
        test = self.tests.get(test_id)
        
        if not test or test.winner:
            return None
        
        if variant == 'a':
            return (variant, test.variant_a)
        return (variant, test.variant_b)
    
    def record_conversion(self, user_id: str, amount: float, engagement: float):
        """Записать конверсию."""
        assignment = self.user_assignments.get(user_id)
        if not assignment:
            return
        
        test_id, variant = assignment.split(':')
        test = self.tests.get(test_id)
        
        if not test:
            return
        
        if variant == 'a':
            test.metrics_a['conversions'] += 1
            test.metrics_a['revenue'] += amount
            test.metrics_a['engagement'] += engagement
        else:
            test.metrics_b['conversions'] += 1
            test.metrics_b['revenue'] += amount
            test.metrics_b['engagement'] += engagement
    
    def evaluate_winner(self, test_id: str) -> Optional[str]:
        """Определить победителя."""
        test = self.tests.get(test_id)
        if not test:
            return None
        
        # Простая логика: победитель по revenue
        if test.metrics_a['revenue'] > test.metrics_b['revenue']:
            test.winner = 'a'
        elif test.metrics_b['revenue'] > test.metrics_a['revenue']:
            test.winner = 'b'
        
        return test.winner
    
    def get_best_tactic(self, test_id: str) -> Optional[Dict]:
        """Получить лучшую тактику."""
        test = self.tests.get(test_id)
        if not test:
            return None
        
        winner = test.winner or self.evaluate_winner(test_id)
        
        if winner == 'a':
            return test.variant_a
        elif winner == 'b':
            return test.variant_b
        
        return None


class NeuralPaymentPredictor:
    """
    Neural Payment Prediction - Прогноз платежей.
    """
    
    def __init__(self):
        self.user_features: Dict[str, Dict] = {}
        self.weights = {
            'recency': 0.3,
            'engagement': 0.25,
            'spending_history': 0.25,
            'psychotype_match': 0.2
        }
    
    def update_user(self, user_id: str, features: Dict):
        """Обновить данные пользователя."""
        if user_id not in self.user_features:
            self.user_features[user_id] = {
                'messages_count': 0,
                'total_spent': 0,
                'last_activity': None,
                'avg_response_time': 0,
                'psychotype_scores': {}
            }
        
        self.user_features[user_id].update(features)
    
    def predict_payment_probability(self, user_id: str, hours: int = 2) -> float:
        """
        Предсказать вероятность платежа.
        
        Returns:
            Вероятность (0-1)
        """
        if user_id not in self.user_features:
            return 0.3  # Базовая вероятность
        
        features = self.user_features[user_id]
        
        # 1. Recency score (недавняя активность)
        if features.get('last_activity'):
            last = datetime.fromisoformat(features['last_activity'])
            hours_since = (datetime.now() - last).total_seconds() / 3600
            recency = max(0, 1 - hours_since / 168)  # 1 неделя = 0
        else:
            recency = 0
        
        # 2. Engagement score
        engagement = min(1, features.get('messages_count', 0) / 50)
        
        # 3. Spending history
        spending = min(1, features.get('total_spent', 0) / 1000)
        
        # 4. Psychotype match (упрощено)
        psychotype_score = features.get('psychotype_match', 0.5)
        
        # Вычисляем взвешенную сумму
        probability = (
            recency * self.weights['recency'] +
            engagement * self.weights['engagement'] +
            spending * self.weights['spending_history'] +
            psychotype_score * self.weights['psychotype_match']
        )
        
        return min(1.0, probability)
    
    def get_payment_window(self, user_id: str) -> str:
        """Определить окно платежа."""
        prob = self.predict_payment_probability(user_id)
        
        if prob > 0.7:
            return "immediate"  # В ближайшие часы
        elif prob > 0.4:
            return "24h"  # В течение 24 часов
        elif prob > 0.2:
            return "week"  # В течение недели
        else:
            return "low"  # Низкая вероятность


class PsychologicalProfiler:
    """
    Psychological Profile Deepening - Детальные профили клиентов.
    """
    
    def __init__(self, db_path: str = "data/user_profiles.db"):
        self.db_path = db_path
        self._ensure_table()
    
    def _ensure_table(self):
        """Создать таблицу если нужно."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whale_obsessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                obsessions TEXT,  -- JSON массив
                triggers TEXT,    -- JSON массив
                pet_name TEXT,
                city TEXT,
                job TEXT,
                interests TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def save_obsessions(self, user_id: str, obsessions: List[str], triggers: List[str],
                       personal_facts: Dict):
        """Сохранить данные об "пунктиках" клиента."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO whale_obsessions 
            (user_id, obsessions, triggers, pet_name, city, job, interests, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            user_id,
            json.dumps(obsessions),
            json.dumps(triggers),
            personal_facts.get('pet_name'),
            personal_facts.get('city'),
            personal_facts.get('job'),
            json.dumps(personal_facts.get('interests', []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_obsessions(self, user_id: str) -> Optional[Dict]:
        """Получить данные о клиенте."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT obsessions, triggers, pet_name, city, job, interests
            FROM whale_obsessions WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'obsessions': json.loads(row[0]) if row[0] else [],
            'triggers': json.loads(row[1]) if row[1] else [],
            'pet_name': row[2],
            'city': row[3],
            'job': row[4],
            'interests': json.loads(row[5]) if row[5] else []
        }
    
    def generate_obsession_insight(self, user_id: str) -> str:
        """Сгенерировать insight на основе пунктиков."""
        data = self.get_obsessions(user_id)
        
        if not data:
            return ""
        
        insights = []
        
        if data.get('pet_name'):
            insights.append(f"помню, ты рассказывал про своего питомца {data['pet_name']}")
        
        if data.get('city'):
            insights.append(f"как там в {data['city']}?")
        
        if data.get('obsessions'):
            top_obsession = random.choice(data['obsessions'])
            insights.append(f"знаю, тебе нравится {top_obsession}")
        
        if insights:
            return ", ".join(insights) + " 💕"
        
        return ""


class AutonomousScriptEvolution:
    """
    Autonomous Script Evolution - Авто-эволюция скриптов.
    """
    
    def __init__(self):
        self.script_performance: Dict[str, Dict] = defaultdict(lambda: {
            'uses': 0,
            'conversions': 0,
            'failed_responses': 0,
            'avg_engagement': 0
        })
        self.evolution_log: List[Dict] = []
    
    def record_usage(self, script_id: str, converted: bool, engagement: float,
                    user_response: str = None):
        """Записать использование скрипта."""
        stats = self.script_performance[script_id]
        stats['uses'] += 1
        
        if converted:
            stats['conversions'] += 1
        
        # Анализ реакции пользователя
        if user_response:
            negative_words = ['неинтересно', 'скучно', 'надоело', 'отстань', 'не хочу']
            if any(word in user_response.lower() for word in negative_words):
                stats['failed_responses'] += 1
        
        # Обновляем среднее вовлечение
        stats['avg_engagement'] = (
            (stats['avg_engagement'] * (stats['uses'] - 1) + engagement) / stats['uses']
        )
    
    def should_evolve(self, script_id: str) -> bool:
        """Определить, нужно ли менять скрипт."""
        stats = self.script_performance[script_id]
        
        if stats['uses'] < 10:
            return False
        
        # Меняем если низкая конверсия или много негативных реакций
        conversion_rate = stats['conversions'] / stats['uses']
        failure_rate = stats['failed_responses'] / stats['uses']
        
        return conversion_rate < 0.1 or failure_rate > 0.3
    
    def suggest_evolution(self, script_id: str) -> str:
        """Предложить эволюцию скрипта."""
        stats = self.script_performance[script_id]
        
        suggestions = []
        
        if stats['failed_responses'] / max(1, stats['uses']) > 0.3:
            suggestions.append("Слишком много негативных реакций - смягчи тон")
        
        if stats['conversions'] / max(1, stats['uses']) < 0.1:
            suggestions.append("Низкая конверсия - добавь больше персонализации")
        
        if stats['avg_engagement'] < 0.3:
            suggestions.append("Низкое вовлечение - сделай вопросы более интересными")
        
        if not suggestions:
            suggestions.append("Скрипт работает хорошо, но можно улучшить")
        
        return "; ".join(suggestions)


class DeepMemoryRetrieval:
    """
    Deep Memory Retrieval - Поиск по истории за 6+ месяцев.
    """
    
    def __init__(self, db_path: str = "data/user_profiles.db"):
        self.db_path = db_path
    
    def search_memory(self, user_id: str, query: str, months: int = 6) -> List[str]:
        """
        Поиск по памяти.
        
        Args:
            user_id: ID пользователя
            query: Поисковый запрос
            months: Глубина поиска в месяцах
            
        Returns:
            Список найденных фактов
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=months*30)).isoformat()
        
        # Ищем в истории разговоров
        cursor.execute("""
            SELECT message_text, response_text 
            FROM conversation_history 
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        """, (user_id, since))
        
        results = []
        for row in cursor.fetchall():
            if query.lower() in row[0].lower() or query.lower() in (row[1] or "").lower():
                results.append(row[0])
        
        conn.close()
        
        return results[:5]  # Максимум 5 результатов
    
    def get_memories_for_context(self, user_id: str, limit: int = 3) -> List[str]:
        """Получить воспоминания для контекста."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Последние сообщения пользователя
        cursor.execute("""
            SELECT message_text FROM conversation_history
            WHERE user_id = ? AND message_from = 'user'
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit))
        
        memories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return memories
    
    def extract_fact_from_message(self, message: str) -> Optional[Dict]:
        """Извлечь факт из сообщения."""
        facts = {}
        
        # Простые паттерны для извлечения
        patterns = {
            'pet': r'питомец.*?называется?\s+(\w+)',
            'city': r'живу.*?в\s+(\w+)',
            'job': r'работаю.*?как\s+(.+)',
            'age': r'(\d+)\s*лет'
        }
        
        import re
        for fact_type, pattern in patterns.items():
            match = re.search(pattern, message.lower())
            if match:
                facts[fact_type] = match.group(1)
        
        return facts if facts else None


class CompetitorEmulation:
    """
    Competitor Emulation - Эмуляция конкурентов для ревности.
    """
    
    JEALOUSY_TRIGGERS = [
        "Кстати, другой подписчик тоже интересовался этим...",
        "Недавно один очень настойчивый фанат писал мне про это...",
        "Знаешь, меня тут спрашивали про подобное...",
        "Недавно мне написали, что готовы на многое ради моего внимания...",
    ]
    
    @classmethod
    def generate_jealousy_message(cls, context: str = None) -> str:
        """Сгенерировать сообщение-триггер ревности."""
        base = random.choice(cls.JEALOUSY_TRIGGERS)
        
        if context:
            return f"{base} Но мне больше нравится общаться с тобой 💕"
        
        return base
    
    @classmethod
    def create_urgency(cls, user_spending_level: str) -> str:
        """Создать ощущение срочности."""
        messages = {
            'low': "Я тут подумала... может, порадуешь меня чем-то? 😘",
            'medium': "Знаешь, мне нужен кто-то, кто меня поддержит... 💭",
            'high': "Ты же мой самый главный, да? 🥺"
        }
        
        return messages.get(user_spending_level, messages['medium'])


class SemanticDriftDetector:
    """
    Semantic Drift Detection - Определение скуки/раздражения.
    """
    
    BOREDOM_PATTERNS = [
        'да', 'ладно', 'окей', 'ну', 'ладно', 'не знаю', 'что-то такое'
    ]
    
    ANGER_PATTERNS = [
        'злой', 'надоел', 'отстань', 'надоело', 'раздражает', 'бесит'
    ]
    
    @classmethod
    def detect_drift(cls, messages: List[str]) -> Optional[str]:
        """
        Определить семантический дрейф.
        
        Returns:
            'boredom', 'anger', 'excitement' или None
        """
        if not messages:
            return None
        
        recent_messages = messages[-3:]
        
        # Проверяем на скуку
        boredom_count = sum(
            1 for msg in recent_messages 
            if any(p in msg.lower() for p in cls.BOREDOM_PATTERNS)
        )
        
        if boredom_count >= 2:
            return 'boredom'
        
        # Проверяем на злость
        anger_count = sum(
            1 for msg in recent_messages 
            if any(p in msg.lower() for p in cls.ANGER_PATTERNS)
        )
        
        if anger_count >= 1:
            return 'anger'
        
        return None
    
    @classmethod
    def get_adaptive_response(cls, drift_type: str, username: str) -> str:
        """Получить адаптивный ответ на дрейф."""
        
        boredom_responses = [
            "Ой, тебе скучно? Расскажи что-нибудь интересное о себе! 💕",
            "Давай поиграем во что-нибудь? 😘",
            "Расскажи, чем ты занимаешься? Мне так интересно всё про тебя! ✨"
        ]
        
        anger_responses = [
            "Успокойся, зайка... 😘 Расскажи, что случилось?",
            "Я не хотела тебя расстроить... Прости меня 💋",
            "Давай поговорим спокойно? Я всегда выслушаю тебя 💕"
        ]
        
        if drift_type == 'boredom':
            return random.choice(boredom_responses)
        elif drift_type == 'anger':
            return random.choice(anger_responses)
        
        return ""


class ReinforcementLearningLoop:
    """
    Reinforcement Learning Loop - Система самопоощрения.
    """
    
    REWARD_THRESHOLDS = {
        100: "bronze",
        500: "silver", 
        1000: "gold",
        5000: "platinum",
        10000: "diamond"
    }
    
    def __init__(self):
        self.total_rewards: float = 0
        self.reward_history: List[Dict] = []
        self.current_rank: str = "bronze"
    
    def process_reward(self, amount: float, source: str = "payment") -> Dict:
        """
        Обработать награду.
        
        Returns:
            Информация о награде
        """
        self.total_rewards += amount
        
        # Определяем ранг
        new_rank = self.current_rank
        for threshold, rank in sorted(self.REWARD_THRESHOLDS.items()):
            if amount >= threshold:
                new_rank = rank
        
        rank_up = self._get_rank_value(new_rank) > self._get_rank_value(self.current_rank)
        self.current_rank = new_rank
        
        reward_info = {
            'amount': amount,
            'source': source,
            'total_rewards': self.total_rewards,
            'rank': new_rank,
            'rank_up': rank_up
        }
        
        self.reward_history.append({
            **reward_info,
            'timestamp': datetime.now().isoformat()
        })
        
        return reward_info
    
    def _get_rank_value(self, rank: str) -> int:
        """Получить числовое значение ранга."""
        ranks = ['bronze', 'silver', 'gold', 'platinum', 'diamond']
        return ranks.index(rank) if rank in ranks else 0
    
    def get_status(self) -> Dict:
        """Получить статус системы."""
        return {
            'total_rewards': self.total_rewards,
            'current_rank': self.current_rank,
            'total_transactions': len(self.reward_history),
            'next_rank_threshold': self._get_next_threshold()
        }
    
    def _get_next_threshold(self) -> Optional[int]:
        """Получить порог следующего ранга."""
        current_value = self._get_rank_value(self.current_rank)
        
        for threshold, rank in self.REWARD_THRESHOLDS.items():
            if self._get_rank_value(rank) > current_value:
                return threshold
        
        return None


# ============================================================================
# OVERLORD ENGINE - ГЛАВНЫЙ КЛАСС
# ============================================================================

class OverlordEngine:
    """
    Overlord Engine - Главный класс сверх-интеллекта.
    """
    
    def __init__(self, db_path: str = "data/user_profiles.db"):
        self.db_path = db_path
        
        # Блок 6: Сверх-Интеллект
        self.ab_test_engine = ABTestEngine()
        self.payment_predictor = NeuralPaymentPredictor()
        self.psychological_profiler = PsychologicalProfiler(db_path)
        self.script_evolution = AutonomousScriptEvolution()
        self.deep_memory = DeepMemoryRetrieval(db_path)
        self.rl_loop = ReinforcementLearningLoop()
    
    # =========================================================================
    # Методы для интеграции
    # =========================================================================
    
    def process_message(self, user_id: str, message: str, 
                       psychotype: str) -> Dict:
        """
        Обработать сообщение с учетом сверх-интеллекта.
        """
        result = {
            'should_respond': True,
            'drift_detected': None,
            'memory_context': [],
            'payment_prediction': 0.5,
            'jealousy_trigger': False,
            'script_evolution': None
        }
        
        # 1. Semantic Drift Detection
        recent_messages = self.deep_memory.get_memories_for_context(user_id)
        drift = SemanticDriftDetector.detect_drift([message] + recent_messages)
        
        if drift:
            result['drift_detected'] = drift
        
        # 2. Deep Memory Retrieval
        memories = self.deep_memory.get_memories_for_context(user_id, limit=2)
        result['memory_context'] = memories
        
        # 3. Payment Prediction
        prob = self.payment_predictor.predict_payment_probability(user_id)
        result['payment_prediction'] = prob
        
        # 4. Competitor Emulation (редко)
        if random.random() < 0.05:  # 5% шанс
            result['jealousy_trigger'] = True
        
        # 5. Script Evolution Check
        if random.random() < 0.1:  # 10% шанс
            result['script_evolution'] = "Проверка эффективности скриптов..."
        
        return result
    
    def record_payment(self, user_id: str, amount: float):
        """Записать платеж для обучения."""
        # RL Loop
        reward = self.rl_loop.process_reward(amount)
        
        # A/B Test
        self.ab_test_engine.record_conversion(user_id, amount, engagement=0.8)
        
        # Update Payment Predictor
        self.payment_predictor.update_user(user_id, {
            'last_activity': datetime.now().isoformat(),
            'total_spent': self.payment_predictor.user_features.get(user_id, {}).get('total_spent', 0) + amount
        })
    
    def save_user_obsessions(self, user_id: str, obsessions: List[str],
                            triggers: List[str], personal_facts: Dict):
        """Сохранить пунктики пользователя."""
        self.psychological_profiler.save_obsessions(user_id, obsessions, triggers, personal_facts)
    
    def get_user_insight(self, user_id: str) -> str:
        """Получить персонализированный insight."""
        return self.psychological_profiler.generate_obsession_insight(user_id)
    
    def get_status(self) -> Dict:
        """Получить статус системы."""
        return {
            'rl_loop': self.rl_loop.get_status(),
            'active_tests': len(self.ab_test_engine.tests),
            'users_tracked': len(self.payment_predictor.user_features)
        }


# Singleton
_overlord_engine: Optional[OverlordEngine] = None


def get_overlord_engine(db_path: str = "data/user_profiles.db") -> OverlordEngine:
    """Получить экземпляр OverlordEngine."""
    global _overlord_engine
    if _overlord_engine is None:
        _overlord_engine = OverlordEngine(db_path)
    return _overlord_engine
