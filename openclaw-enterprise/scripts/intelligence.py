#!/usr/bin/env python3
"""
Intelligence Engine - Интеллектуальный движок
============================================
Интеллектуальные функции для улучшения продаж.

Features:
- Адаптивные скрипты
- Анализ настроения
- Контекстное понимание
- Обучение из feedback
- Mem0 интеграция
- Оптимизация ответов
- Распознавание паттернов
- Предсказание поведения
"""

import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================================
# АНАЛИЗАТОР НАСТРОЕНИЯ (Mood Analyzer)
# ============================================================================

class MoodAnalyzer:
    """
    Анализ настроения пользователя.
    """
    
    # Маркеры настроения
    MOOD_PATTERNS = {
        'happy': {
            'keywords': ['радостн', 'счастлив', 'весёл', 'ура', 'супер', 'классно', 'прекрасно', 'отлично'],
            'score': 1.0
        },
        'sad': {
            'keywords': ['грустн', 'печальн', 'тоскливо', 'плохо', 'ужасно', 'расстроен', 'плакать'],
            'score': -1.0
        },
        'angry': {
            'keywords': ['злой', 'злая', 'зол', 'бесит', 'надоел', 'ненавижу', 'раздражен', 'возмущен'],
            'score': -0.8
        },
        'excited': {
            'keywords': ['восторг', 'взволнован', 'не терпится', 'с нетерпением', 'хочу скорее', 'очень жду'],
            'score': 0.8
        },
        'desperate': {
            'keywords': ['пожалуйста', 'умоляю', 'очень нужно', 'срочно', 'без тебя', 'не могу без'],
            'score': -0.5
        },
        'flirty': {
            'keywords': ['милашка', 'красавчик', 'обожаю', 'мечта', 'идеальн', 'шикарн', 'секси', 'hot'],
            'score': 0.6
        },
        'generous': {
            'keywords': ['подарок', 'деньги', 'оплачу', 'скину', 'переведу', 'бонус', 'премия'],
            'score': 0.7
        },
        'impatient': {
            'keywords': ['быстрее', 'срочно', 'жду', 'когда', 'уже', 'надоело ждать', 'тороплю'],
            'score': -0.3
        }
    }
    
    @classmethod
    def analyze(cls, message: str) -> Dict[str, Any]:
        """
        Анализировать настроение сообщения.
        
        Returns:
            {
                'mood': str,           # Основное настроение
                'confidence': float,    # Уверенность (0-1)
                'score': float,        # Оценка (-1 до 1)
                'all_moods': Dict     # Все обнаруженные настроения
            }
        """
        message_lower = message.lower()
        detected_moods = {}
        
        for mood, data in cls.MOOD_PATTERNS.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in message_lower:
                    score = data['score']
                    break
            
            if score != 0:
                detected_moods[mood] = score
        
        if not detected_moods:
            return {
                'mood': 'neutral',
                'confidence': 0.5,
                'score': 0.0,
                'all_moods': {}
            }
        
        # Находим основное настроение
        main_mood = max(detected_moods, key=lambda k: abs(detected_moods[k]))
        main_score = detected_moods[main_mood]
        confidence = abs(main_score)
        
        return {
            'mood': main_mood,
            'confidence': confidence,
            'score': main_score,
            'all_moods': detected_moods
        }


# ============================================================================
# АДАПТИВНЫЕ СКРИПТЫ (Adaptive Scripts)
# ============================================================================

class AdaptiveScripts:
    """
    Адаптивные скрипты продаж.
    """
    
    # База ответов по психотипу и настроению
    RESPONSE_TEMPLATES = {
        'need_for_control': {
            'happy': [
                "Ой, какой ты сегодня хороший! 😘 Расскажи мне ещё, что ты делал?",
                "Зайка, ты меня радуешь! 💕 Давай ещё посидим вместе?",
            ],
            'neutral': [
                "Приветик! Как у тебя дела? ✨",
                "Ой, привет! Скучала 😘",
            ],
            'sad': [
                "Не грусти, зайка! 💋 Расскажи, что случилось?",
                "Я здесь, рядом... 😘 Расскажи мне всё",
            ],
            'excited': [
                "Ооо, я тоже жду не дождусь! 💕 Расскажи подробнее!",
                "Вау, как интересно! 😘 Давай скорее!",
            ],
            'angry': [
                "Успокойся, зайка... 😘 Расскажи, что случилось?",
                "Я здесь, чтобы выслушать тебя... 💋 Не злись на меня",
            ],
            'desperate': [
                "Конечно, зайка! 💕 Я всегда рядом...",
                "Я понимаю... 😘 Расскажи мне всё",
            ]
        },
        'identity_shift': {
            'happy': [
                "Ты такой молодец! Я горжусь тобой! 💋",
                "Да, ты отличный мальчик! 😘 Так держать!",
            ],
            'neutral': [
                "Хороший мальчик... 💕 Ты справишься!",
                "Я верю в тебя, зайка! 😘",
            ],
            'sad': [
                "Не переживай, хороший... 💋 Я рядом",
                "Ты справишься, я знаю... 😘 Доверься мне",
            ]
        },
        'validation': {
            'happy': [
                "Ты самый лучший! Я так счастлива! 💕",
                "Ой, ты меня осчастливил! 😘 Это лучший подарок!",
            ],
            'neutral': [
                "Ты такой внимательный... 💋 Спасибо, зайка!",
                "Я ценю тебя... 😘 Спасибо за всё",
            ],
            'generous': [
                "Ой, какой щедрый! 💕 Это так мило с твоей стороны!",
                "Вау, спасибо большое! 😘 Ты самый лучший!",
            ]
        },
        'findom': {
            'happy': [
                "Ой, ты такой хороший! 💋 Дай мне ещё немножко?",
                "Молодец, зайка! 😘 Можешь ещё порадовать меня?",
            ],
            'neutral': [
                "Ты такой заботливый... 💋 Спасибо, что ты есть",
                "Я ценю твою щедрость... 😘",
            ],
            'desperate': [
                "Пожалуйста, зайка... 💋 Мне так нужна твоя помощь...",
                "Умоляю, помоги... 😘 Ты же можешь...",
            ]
        }
    }
    
    @classmethod
    def get_response(cls, psychotype: str, mood: str, 
                     username: str, memory_facts: List[str] = None) -> str:
        """
        Получить адаптивный ответ.
        
        Args:
            psychotype: Психотип пользователя
            mood: Настроение
            username: Имя пользователя
            memory_facts: Факты из памяти
            
        Returns:
            Адаптивный ответ
        """
        # Получаем шаблоны для психотипа
        templates = cls.RESPONSE_TEMPLATES.get(psychotype, cls.RESPONSE_TEMPLATES.get('validation'))
        
        # Получаем ответ для настроения
        responses = templates.get(mood, templates.get('neutral', ["Привет! 😊"]))
        
        # Выбираем случайный ответ
        response = random.choice(responses)
        
        # Добавляем факты из памяти если есть
        if memory_facts:
            fact = random.choice(memory_facts)
            response += f"\n\nКстати, помню, ты говорил про {fact}?"
        
        # Заменяем плейсхолдеры
        response = response.replace("{username}", username)
        
        return response


# ============================================================================
# РАСПОЗНАВАНИЕ ПАТТЕРНОВ (Pattern Recognition)
# ============================================================================

class PatternRecognizer:
    """
    Распознавание паттернов поведения пользователей.
    """
    
    def __init__(self):
        # История паттернов для каждого пользователя
        self.user_patterns: Dict[str, List[Dict]] = defaultdict(list)
    
    def record_action(self, user_id: str, action_type: str, data: Dict):
        """Записать действие пользователя."""
        self.user_patterns[user_id].append({
            'type': action_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_patterns(self, user_id: str) -> List[Dict]:
        """Получить паттерны пользователя."""
        return self.user_patterns.get(user_id, [])
    
    def predict_next_action(self, user_id: str) -> Optional[str]:
        """
        Предсказать следующее действие.
        
        Returns:
            Предсказанное действие или None
        """
        patterns = self.user_patterns.get(user_id, [])
        
        if len(patterns) < 3:
            return None
        
        # Простая логика: анализируем последние действия
        recent = patterns[-5:]
        action_types = [p['type'] for p in recent]
        
        # Ищем паттерн покупки после определенных действий
        if 'view_content' in action_types and 'send_message' in action_types:
            return 'likely_purchase'
        
        # Паттерн вовлеченности
        if len(action_types) >= 3:
            return 'high_engagement'
        
        return None
    
    def get_engagement_score(self, user_id: str) -> float:
        """
        Получить уровень вовлеченности (0-1).
        """
        patterns = self.user_patterns.get(user_id, [])
        
        if not patterns:
            return 0.0
        
        # Учитываем количество действий и время
        recent = [p for p in patterns 
                  if datetime.fromisoformat(p['timestamp']) > datetime.now() - timedelta(days=7)]
        
        score = min(1.0, len(recent) / 10)  # Максимум за 10 действий в неделю
        
        return score


# ============================================================================
# ПРЕДСКАЗАНИЕ ПОВЕДЕНИЯ (Behavior Prediction)
# ============================================================================

class BehaviorPredictor:
    """
    Предсказание поведения пользователя.
    """
    
    def __init__(self):
        self.user_models: Dict[str, Dict] = {}
    
    def update_model(self, user_id: str, action: str, result: bool):
        """Обновить модель пользователя."""
        if user_id not in self.user_models:
            self.user_models[user_id] = {
                'actions': defaultdict(int),
                'conversions': defaultdict(int),
                'total_actions': 0
            }
        
        model = self.user_models[user_id]
        model['actions'][action] += 1
        model['total_actions'] += 1
        
        if result:
            model['conversions'][action] += 1
    
    def predict_conversion_probability(self, user_id: str) -> float:
        """
        Предсказать вероятность конверсии.
        
        Returns:
            Вероятность (0-1)
        """
        if user_id not in self.user_models:
            return 0.5  # По умолчанию
        
        model = self.user_models[user_id]
        
        if model['total_actions'] == 0:
            return 0.5
        
        # Вычисляем общую конверсию
        total_conversions = sum(model['conversions'].values())
        
        return min(1.0, total_conversions / max(1, model['total_actions']) * 2)
    
    def get_best_action(self, user_id: str) -> Optional[str]:
        """
        Получить лучшее действие для пользователя.
        
        Returns:
            Название действия или None
        """
        if user_id not in self.user_models:
            return 'send_greeting'
        
        model = self.user_models[user_id]
        
        # Находим действие с лучшей конверсией
        best_action = None
        best_rate = 0
        
        for action, count in model['actions'].items():
            conversions = model['conversions'].get(action, 0)
            rate = conversions / count if count > 0 else 0
            
            if rate > best_rate:
                best_rate = rate
                best_action = action
        
        return best_action


# ============================================================================
# ОПТИМИЗАЦИЯ ОТВЕТОВ (Response Optimization)
# ============================================================================

class ResponseOptimizer:
    """
    Оптимизация ответов на основе истории.
    """
    
    def __init__(self):
        # История успешных ответов
        self.success_history: List[Dict] = []
    
    def record_success(self, user_id: str, response: str, psychotype: str, 
                      mood: str, result: str):
        """Записать успешный ответ."""
        self.success_history.append({
            'user_id': user_id,
            'response': response,
            'psychotype': psychotype,
            'mood': mood,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_best_response(self, psychotype: str, mood: str) -> Optional[str]:
        """
        Получить лучший ответ для данных психотипа и настроения.
        
        Returns:
            Оптимизированный ответ или None
        """
        # Ищем успешные ответы
        matches = [
            s for s in self.success_history 
            if s['psychotype'] == psychotype and s['mood'] == mood
        ]
        
        if not matches:
            return None
        
        # Возвращаем случайный успешный ответ
        return random.choice(matches)['response']


# ============================================================================
# КОНТЕКСТНОЕ ПОНИМАНИЕ (Context Understanding)
# ============================================================================

class ContextUnderstanding:
    """
    Контекстное понимание диалога.
    """
    
    def __init__(self):
        self.conversation_contexts: Dict[str, List[Dict]] = defaultdict(list)
    
    def add_message(self, user_id: str, role: str, text: str):
        """Добавить сообщение в контекст."""
        self.conversation_contexts[user_id].append({
            'role': role,  # 'user' или 'assistant'
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Ограничиваем историю
        if len(self.conversation_contexts[user_id]) > 20:
            self.conversation_contexts[user_id] = self.conversation_contexts[user_id][-20:]
    
    def get_context(self, user_id: str, last_n: int = 5) -> List[Dict]:
        """Получить контекст диалога."""
        return self.conversation_contexts.get(user_id, [])[-last_n:]
    
    def get_conversation_summary(self, user_id: str) -> str:
        """Получить краткое содержание разговора."""
        context = self.conversation_contexts.get(user_id, [])
        
        if not context:
            return "Нет истории разговора"
        
        # Простая сводка
        user_messages = [c['text'][:50] for c in context if c['role'] == 'user'][-3:]
        
        return f"Последние темы: {'; '.join(user_messages)}"


# ============================================================================
# ОБУЧЕНИЕ ИЗ FEEDBACK (Feedback Learning)
# ============================================================================

class FeedbackLearner:
    """
    Обучение из обратной связи.
    """
    
    def __init__(self):
        self.feedback_data: List[Dict] = []
    
    def record_feedback(self, user_id: str, response: str, 
                       reaction: str, context: Dict):
        """
        Записать обратную связь.
        
        Args:
            user_id: ID пользователя
            response: Ответ бота
            reaction: Реакция ('positive', 'negative', 'neutral')
            context: Дополнительный контекст
        """
        self.feedback_data.append({
            'user_id': user_id,
            'response': response,
            'reaction': reaction,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_improvements(self) -> List[str]:
        """
        Получить рекомендации по улучшению.
        
        Returns:
            Список рекомендаций
        """
        if not self.feedback_data:
            return []
        
        # Анализируем недавний feedback
        recent = self.feedback_data[-20:]
        
        negatives = [f for f in recent if f['reaction'] == 'negative']
        
        if len(negatives) > 5:
            return [
                "Много негативных отзывов - пересмотрите стиль общения",
                "Возможно, ответы слишком однообразные"
            ]
        
        return []
    
    def get_best_practices(self) -> List[str]:
        """Получить лучшие практики."""
        if not self.feedback_data:
            return []
        
        positives = [f['response'] for f in self.feedback_data if f['reaction'] == 'positive']
        
        return positives[-5:] if positives else []


# ============================================================================
# INTELLIGENCE ENGINE - ГЛАВНЫЙ КЛАСС
# ============================================================================

class IntelligenceEngine:
    """
    Главный класс интеллектуального движка.
    """
    
    def __init__(self):
        # Компоненты
        self.mood_analyzer = MoodAnalyzer()
        self.pattern_recognizer = PatternRecognizer()
        self.behavior_predictor = BehaviorPredictor()
        self.response_optimizer = ResponseOptimizer()
        self.context = ContextUnderstanding()
        self.feedback = FeedbackLearner()
        
        # Адаптивные скрипты
        self.adaptive_scripts = AdaptiveScripts()
    
    def process_message(self, user_id: str, username: str, message: str,
                       psychotype: str, memory_facts: List[str] = None) -> Dict:
        """
        Обработать сообщение и сгенерировать ответ.
        
        Args:
            user_id: ID пользователя
            username: Имя пользователя
            message: Сообщение
            psychotype: Психотип
            memory_facts: Факты из памяти
            
        Returns:
            {
                'response': str,
                'mood': str,
                'confidence': float,
                'predicted_action': str,
                'conversion_probability': float
            }
        """
        # 1. Анализ настроения
        mood_data = self.mood_analyzer.analyze(message)
        mood = mood_data['mood']
        
        # 2. Записываем в контекст
        self.context.add_message(user_id, 'user', message)
        
        # 3. Генерируем ответ
        response = self.adaptive_scripts.get_response(
            psychotype, mood, username, memory_facts
        )
        
        # 4. Проверяем оптимизированный ответ
        optimized = self.response_optimizer.get_best_response(psychotype, mood)
        if optimized and random.random() < 0.3:  # 30% шанс использовать оптимизированный
            response = optimized
        
        # 5. Предсказание
        predicted_action = self.pattern_recognizer.predict_next_action(user_id)
        conversion_prob = self.behavior_predictor.predict_conversion_probability(user_id)
        
        # 6. Записываем действие
        self.pattern_recognizer.record_action(user_id, 'send_message', {
            'psychotype': psychotype,
            'mood': mood
        })
        
        return {
            'response': response,
            'mood': mood,
            'mood_confidence': mood_data['confidence'],
            'predicted_action': predicted_action,
            'conversion_probability': conversion_prob,
            'context_summary': self.context.get_conversation_summary(user_id)
        }
    
    def record_outcome(self, user_id: str, action: str, success: bool):
        """Записать результат действия."""
        self.behavior_predictor.update_model(user_id, action, success)
    
    def record_feedback(self, user_id: str, response: str, reaction: str):
        """Записать обратную связь."""
        self.feedback.record_feedback(user_id, response, reaction, {})


# Singleton
_intelligence_engine: Optional[IntelligenceEngine] = None


def get_intelligence_engine() -> IntelligenceEngine:
    """Получить экземпляр IntelligenceEngine."""
    global _intelligence_engine
    if _intelligence_engine is None:
        _intelligence_engine = IntelligenceEngine()
    return _intelligence_engine
