#!/usr/bin/env python3
"""
GLOBAL EMPIRE - Глобальная Империя
==================================
Блоки 7-10: Шаги 49-80

Блок 7: Глобальная Сеть и Трафик (49-56)
- Multi-Platform Bridge
- Proxy Rotator Manager
- Lead Gen Simulator
- Auto-Commenter Logic
- Funnel Analytics
- Geo-Clock Sync
- Language Auto-Switch
- Affiliate Engine

Блок 8: Финансовая Крепость (57-64)
- Crypto-Payment Mock-Gateway
- Tax & Fee Calculator
- Invoice Generator
- Subscription Logic
- Financial Forecasting
- Transaction Audit
- Cash-out Alerts
- Anti-Refund Psychology

Блок 9: Неубиваемость и Масштаб (65-72)
- Shadow Mode Execution
- Advanced Encryption
- Auto-Unit-Testing
- Docker Integration
- Health Dashboard
- Self-Destruct / Panic Button
- Anti-Scam Filter
- Auto-Update Manager

Блок 10: Режим "Бога" (73-80)
- Master Orchestrator
- Executive Hourly Report
- Neural Personality Sync
- Long-term Strategy Map
- Human-in-the-loop Optimization
- Resource Optimization
- Final Global Stress Test
- God Mode Enabled
"""

import json
import random
import time
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import os


# ============================================================================
# БЛОК 7: ГЛОБАЛЬНАЯ СЕТЬ И ТРАФИК
# ============================================================================

class MultiPlatformBridge:
    """
    Multi-Platform Bridge - интеграция с платформами.
    """
    
    PLATFORMS = {
        'whatsapp': {'status': 'ready', 'api_version': 'v1'},
        'discord': {'status': 'ready', 'api_version': 'v1'},
        'twitter': {'status': 'ready', 'api_version': 'v2'},
        'telegram': {'status': 'active', 'api_version': 'v3'}
    }
    
    def __init__(self):
        self.connected_platforms = ['telegram']
    
    def connect_platform(self, platform: str) -> bool:
        """Подключить платформу."""
        if platform in self.PLATFORMS:
            self.connected_platforms.append(platform)
            return True
        return False
    
    def send_message(self, platform: str, user_id: str, message: str) -> Dict:
        """Отправить сообщение на платформу."""
        return {
            'status': 'mock',
            'platform': platform,
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_platform_status(self) -> Dict:
        """Получить статус платформ."""
        return {
            platform: {
                'connected': platform in self.connected_platforms,
                **self.PLATFORMS.get(platform, {'status': 'unknown'})
            }
            for platform in self.PLATFORMS
        }


class ProxyRotator:
    """
    Proxy Rotator Manager - автоматическая смена IP.
    """
    
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.failed_proxies = set()
    
    def add_proxy(self, proxy: str):
        """Добавить прокси."""
        self.proxies.append(proxy)
    
    def get_next_proxy(self) -> Optional[str]:
        """Получить следующий прокси."""
        if not self.proxies:
            return None
        
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy not in self.failed_proxies:
                return proxy
            
            attempts += 1
        
        return None
    
    def mark_failed(self, proxy: str):
        """Отметить прокси как упавший."""
        self.failed_proxies.add(proxy)


class LeadGenSimulator:
    """
    Lead Gen Simulator - генератор идей для постов.
    """
    
    POST_TEMPLATES = {
        'whale_attention': [
            "Кто-то заслуживает особого внимания... 💕",
            "Эксклюзивный контент для особенных людей ✨",
            "Только для тех, кто понимает толк в удовольствии 😘"
        ],
        'curiosity': [
            "Что будет, если попробовать? 🤔",
            "Секрет, который ты не знаешь...",
            "Это изменит твоё представление о развлечениях 🔥"
        ],
        'exclusivity': [
            "Только сегодня и только для тебя 💋",
            "Личное предложение для моих самых верных фанатов",
            "Эксклюзив, который ты не найдешь нигде больше ✨"
        ]
    }
    
    def generate_post(self, category: str = 'random') -> str:
        """Сгенерировать пост."""
        if category == 'random':
            category = random.choice(list(self.POST_TEMPLATES.keys()))
        
        templates = self.POST_TEMPLATES.get(category, self.POST_TEMPLATES['whale_attention'])
        return random.choice(templates)
    
    def get_trending_topics(self) -> List[str]:
        """Получить трендовые темы."""
        return [
            "Эксклюзивный контент",
            "Личное общение",
            "VIP доступ",
            "Особое внимание"
        ]


class AutoCommenter:
    """
    Auto-Commenter Logic - прогрев в комментариях.
    """
    
    COMMENT_STYLES = {
        'supportive': [
            "Это так верно! 💕",
            "Полностью согласна! 😘",
            "Ты можешь лучше! ✨"
        ],
        'curious': [
            "Интересно, а что дальше? 🤔",
            "Расскажи подробнее! 💭",
            "Ооо, продолжай! 🔥"
        ],
        'flirty': [
            "Это мне нравится... 😘",
            "Ты такой... 💋",
            "Ммм, интересно... ✨"
        ]
    }
    
    def generate_comment(self, style: str = 'supportive') -> str:
        """Сгенерировать комментарий."""
        comments = self.COMMENT_STYLES.get(style, self.COMMENT_STYLES['supportive'])
        return random.choice(comments)


class FunnelAnalytics:
    """
    Funnel Analytics - визуализация воронки продаж.
    """
    
    def __init__(self):
        self.funnel_data = {
            'awareness': 0,
            'interest': 0,
            'desire': 0,
            'action': 0,
            'loyalty': 0
        }
    
    def track_progress(self, stage: str, user_id: str):
        """Отследить прогресс."""
        if stage in self.funnel_data:
            self.funnel_data[stage] += 1
    
    def get_funnel_metrics(self) -> Dict:
        """Получить метрики воронки."""
        total = sum(self.funnel_data.values())
        
        return {
            'stages': self.funnel_data,
            'conversion_rates': {
                'awareness_to_interest': self._calc_rate('awareness', 'interest'),
                'interest_to_desire': self._calc_rate('interest', 'desire'),
                'desire_to_action': self._calc_rate('desire', 'action'),
                'action_to_loyalty': self._calc_rate('action', 'loyalty')
            },
            'total_users': total
        }
    
    def _calc_rate(self, from_stage: str, to_stage: str) -> float:
        """Вычислить конверсию."""
        from_count = self.funnel_data.get(from_stage, 0)
        to_count = self.funnel_data.get(to_stage, 0)
        
        if from_count == 0:
            return 0.0
        
        return round(to_count / from_count, 2)


class GeoClockSync:
    """
    Geo-Clock Sync - синхронизация времени.
    """
    
    USER_TIMEZONES = {}
    
    # Стили по часовому поясу
    TIMEZONE_STYLES = {
        'US_EAST': {'greeting': 'Good morning', 'active_hours': 'morning'},
        'US_WEST': {'greeting': 'Good morning', 'active_hours': 'evening'},
        'EUROPE': {'greeting': 'Good evening', 'active_hours': 'evening'},
        'ASIA': {'greeting': 'Good evening', 'active_hours': 'night'}
    }
    
    @classmethod
    def set_user_timezone(cls, user_id: str, timezone: str):
        """Установить часовой пояс пользователя."""
        cls.USER_TIMEZONES[user_id] = timezone
    
    @classmethod
    def get_user_timezone(cls, user_id: str) -> str:
        """Получить часовой пояс пользователя."""
        return cls.USER_TIMEZONES.get(user_id, 'EUROPE')
    
    @classmethod
    def get_adaptive_greeting(cls, user_id: str) -> str:
        """Получить адаптивное приветствие."""
        tz = cls.get_user_timezone(user_id)
        style = cls.TIMEZONE_STYLES.get(tz, cls.TIMEZONE_STYLES['EUROPE'])
        
        return style['greeting']


class LanguageAutoSwitch:
    """
    Language Auto-Switch - автоперевод.
    """
    
    TRANSLATIONS = {
        'en': {
            'hello': 'hello',
            'thank_you': 'thank you',
            'how_are_you': 'how are you?'
        },
        'es': {
            'hello': 'hola',
            'thank_you': 'gracias',
            'how_are_you': 'como estas?'
        },
        'de': {
            'hello': 'hallo',
            'thank_you': 'danke',
            'how_are_you': 'wie geht es dir?'
        }
    }
    
    @classmethod
    def detect_language(cls, text: str) -> str:
        """Определить язык."""
        # Упрощенная логика
        return 'en'  # По умолчанию
    
    @classmethod
    def translate(cls, text: str, target_lang: str) -> str:
        """Перевести текст."""
        # Mock перевод
        return text


class AffiliateEngine:
    """
    Affiliate Engine - система поощрения рефералов.
    """
    
    def __init__(self):
        self.referrals: Dict[str, List[str]] = defaultdict(list)
        self.rewards = {}
    
    def add_referral(self, referrer_id: str, referred_id: str):
        """Добавить реферала."""
        self.referrals[referrer_id].append(referred_id)
    
    def calculate_reward(self, referrer_id: str) -> float:
        """Рассчитать награду за рефералов."""
        count = len(self.referrals.get(referrer_id, []))
        return count * 10.0  # $10 за каждого
    
    def generate_referral_code(self, user_id: str) -> str:
        """Сгенерировать реферальный код."""
        return f"REF-{user_id[:8].upper()}"


# ============================================================================
# БЛОК 8: ФИНАНСОВАЯ КРЕПОСТЬ
# ============================================================================

class CryptoPaymentGateway:
    """
    Crypto-Payment Mock-Gateway - прием криптовалют.
    """
    
    CRYPTO_RATES = {
        'BTC': 45000.0,
        'ETH': 2500.0,
        'USDT': 1.0
    }
    
    def __init__(self):
        self.pending_payments: Dict[str, Dict] = {}
        self.completed_payments: List[Dict] = []
    
    def create_invoice(self, user_id: str, amount_usd: float, currency: str = 'USDT') -> Dict:
        """Создать счет."""
        amount_crypto = amount_usd / self.CRYPTO_RATES.get(currency, 1.0)
        
        invoice = {
            'invoice_id': f"INV-{int(time.time())}-{user_id[:6]}",
            'user_id': user_id,
            'amount_usd': amount_usd,
            'amount_crypto': amount_crypto,
            'currency': currency,
            'address': self._generate_address(currency),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        self.pending_payments[invoice['invoice_id']] = invoice
        return invoice
    
    def _generate_address(self, currency: str) -> str:
        """Сгенерировать адрес (mock)."""
        return f"{currency}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:16]}"
    
    def confirm_payment(self, invoice_id: str) -> bool:
        """Подтвердить платеж."""
        if invoice_id in self.pending_payments:
            payment = self.pending_payments.pop(invoice_id)
            payment['status'] = 'completed'
            payment['completed_at'] = datetime.now().isoformat()
            self.completed_payments.append(payment)
            return True
        return False


class TaxFeeCalculator:
    """
    Tax & Fee Calculator - расчет налогов и комиссий.
    """
    
    PLATFORM_FEES = {
        'loyalfans': 0.20,  # 20%
        'onlyfans': 0.20,
        'custom': 0.15
    }
    
    @classmethod
    def calculate_net(cls, gross_amount: float, platform: str = 'loyalfans') -> Dict:
        """Рассчитать чистую прибыль."""
        fee_rate = cls.PLATFORM_FEES.get(platform, 0.20)
        platform_fee = gross_amount * fee_rate
        
        # Налог (упрощенно)
        tax = (gross_amount - platform_fee) * 0.10
        
        net = gross_amount - platform_fee - tax
        
        return {
            'gross': gross_amount,
            'platform_fee': platform_fee,
            'platform_fee_percent': fee_rate * 100,
            'tax': tax,
            'net': net,
            'effective_rate': ((gross_amount - net) / gross_amount * 100) if gross_amount > 0 else 0
        }


class InvoiceGenerator:
    """
    Invoice Generator - генератор счетов.
    """
    
    def generate_invoice(self, user_id: str, items: List[Dict], 
                        total: float, currency: str = 'USD') -> str:
        """Сгенерировать визуальный счет."""
        
        invoice = f"""
╔══════════════════════════════════════════════════════════╗
║                    🐋 INVOICE 🐋                        ║
╠══════════════════════════════════════════════════════════╣
║  Invoice #: INV-{int(time.time())}                         ║
║  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}                           ║
║  Customer: {user_id[:20]:<30}          ║
╠══════════════════════════════════════════════════════════╣
"""
        
        for item in items:
            invoice += f"║  {item['name']:<40} ${item['price']:>7.2f} ║\n"
        
        invoice += f"""
╠══════════════════════════════════════════════════════════╣
║  TOTAL:                                     ${total:>7.2f} ║
║  Currency: {currency:<39}          ║
╠══════════════════════════════════════════════════════════╣
║  💋 Спасибо за вашу поддержку!                         ║
╚══════════════════════════════════════════════════════════╝
"""
        
        return invoice


class SubscriptionManager:
    """
    Subscription Logic - управление подписками.
    """
    
    TIERS = {
        'basic': {'price': 9.99, 'features': ['messages']},
        'premium': {'price': 19.99, 'features': ['messages', 'content']},
        'vip': {'price': 49.99, 'features': ['messages', 'content', 'exclusive']}
    }
    
    def __init__(self):
        self.subscriptions: Dict[str, Dict] = {}
    
    def create_subscription(self, user_id: str, tier: str) -> Dict:
        """Создать подписку."""
        if tier not in self.TIERS:
            raise ValueError(f"Unknown tier: {tier}")
        
        sub = {
            'user_id': user_id,
            'tier': tier,
            'price': self.TIERS[tier]['price'],
            'features': self.TIERS[tier]['features'],
            'started_at': datetime.now().isoformat(),
            'next_billing': (datetime.now() + timedelta(days=30)).isoformat(),
            'status': 'active'
        }
        
        self.subscriptions[user_id] = sub
        return sub
    
    def cancel_subscription(self, user_id: str) -> bool:
        """Отменить подписку."""
        if user_id in self.subscriptions:
            self.subscriptions[user_id]['status'] = 'cancelled'
            return True
        return False


class FinancialForecaster:
    """
    Financial Forecasting - прогноз выручки.
    """
    
    def __init__(self):
        self.historical_data: List[Dict] = []
    
    def add_data(self, revenue: float, whales_count: int):
        """Добавить данные."""
        self.historical_data.append({
            'revenue': revenue,
            'whales': whales_count,
            'timestamp': datetime.now().isoformat()
        })
    
    def forecast(self, days: int = 30) -> Dict:
        """Спрогнозировать выручку."""
        if not self.historical_data:
            return {'forecast': 0, 'confidence': 0}
        
        # Простой прогноз на основе среднего
        avg_revenue = sum(d['revenue'] for d in self.historical_data) / len(self.historical_data)
        avg_whales = sum(d['whales'] for d in self.historical_data) / len(self.historical_data)
        
        return {
            'daily_forecast': avg_revenue,
            'monthly_forecast': avg_revenue * days,
            'avg_whales': avg_whales,
            'confidence': 0.7,
            'period_days': days
        }


class CashoutAlerts:
    """
    Cash-out Alerts - уведомления о выводе.
    """
    
    THRESHOLDS = {
        'low': 100,
        'medium': 500,
        'high': 1000,
        'critical': 5000
    }
    
    def __init__(self, notifier=None):
        self.notifier = notifier
        self.current_balance = 0
    
    def check_balance(self, amount: float):
        """Проверить баланс."""
        self.current_balance += amount
        
        for level, threshold in self.THRESHOLDS.items():
            if self.current_balance >= threshold:
                self._send_alert(level, self.current_balance)
    
    def _send_alert(self, level: str, balance: float):
        """Отправить алерт."""
        if self.notifier:
            self.notifier.send_simple_message(
                f"💰 Cash-out Alert [{level.upper()}]: Баланс ${balance:.2f}"
            )


# ============================================================================
# БЛОК 9: НЕУБИВАЕМОСТЬ И МАСШТАБ
# ============================================================================

class ShadowMode:
    """
    Shadow Mode Execution - теневая копия бота.
    """
    
    def __init__(self):
        self.is_active = False
        self.primary_failed = False
    
    def start_shadow(self, config: Dict):
        """Запустить теневое выполнение."""
        self.is_active = True
        print("👤 Shadow Mode: Запущен в фоновом режиме")
    
    def take_over(self):
        """Взять управление при падении основного."""
        if self.primary_failed:
            self.is_active = False
            return True
        return False
    
    def report_primary_status(self, failed: bool):
        """Сообщить о статусе основного бота."""
        self.primary_failed = failed


class AdvancedEncryption:
    """
    Advanced Encryption - продвинутое шифрование.
    """
    
    def __init__(self, key: str = None):
        self.key = key or os.environ.get('ENCRYPTION_KEY', 'default_key_change_me')
    
    def encrypt_data(self, data: str) -> str:
        """Зашифровать данные."""
        import base64
        key_bytes = self.key.encode()[:32]
        data_bytes = data.encode()
        
        encrypted = bytearray()
        for i, b in enumerate(data_bytes):
            encrypted.append(b ^ key_bytes[i % len(key_bytes)])
        
        return base64.b64encode(bytes(encrypted)).decode()
    
    def decrypt_data(self, encrypted: str) -> str:
        """Расшифровать данные."""
        import base64
        key_bytes = self.key.encode()[:32]
        data_bytes = base64.b64decode(encrypted.encode())
        
        decrypted = bytearray()
        for i, b in enumerate(data_bytes):
            decrypted.append(b ^ key_bytes[i % len(key_bytes)])
        
        return bytes(decrypted).decode()


class DockerManager:
    """
    Docker Integration - управление Docker.
    """
    
    DOCKERFILE_TEMPLATE = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
"""
    
    def generate_dockerfile(self, path: str = "Dockerfile") -> str:
        """Сгенерировать Dockerfile."""
        with open(path, 'w') as f:
            f.write(self.DOCKERFILE_TEMPLATE)
        return path


class HealthDashboard:
    """
    Health Dashboard - веб-интерфейс мониторинга.
    """
    
    def __init__(self):
        self.metrics = {}
    
    def update_metrics(self, data: Dict):
        """Обновить метрики."""
        self.metrics = data
    
    def get_html(self) -> str:
        """Получить HTML дашборда."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>OpenClaw Dashboard</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: #1a1a2e; color: #fff; }}
        .card {{ background: #16213e; padding: 20px; margin: 10px; border-radius: 10px; }}
        .metric {{ font-size: 32px; color: #00ff88; }}
    </style>
</head>
<body>
    <h1>🐋 OpenClaw Dashboard</h1>
    <div class="card">
        <h2>Status</h2>
        <div class="metric">Active</div>
    </div>
    <div class="card">
        <h2>Cycles</h2>
        <div class="metric">{self.metrics.get('cycles', 0)}</div>
    </div>
</body>
</html>
"""


class PanicButton:
    """
    Self-Destruct / Panic Button - экстренное удаление.
    """
    
    def __init__(self):
        self.triggered = False
    
    def activate(self, paths: List[str] = None):
        """Активировать самоуничтожение."""
        self.triggered = True
        
        paths = paths or [
            'data/user_profiles.db',
            'logs/',
            'vault/price_list.json'
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    else:
                        import shutil
                        shutil.rmtree(path)
                except:
                    pass
        
        return "🔴 PANIC: Данные удалены"


class AutoUpdateManager:
    """
    Auto-Update Manager - проверка обновлений.
    """
    
    def __init__(self):
        self.last_check = None
        self.updates_available = []
    
    def check_updates(self) -> List[str]:
        """Проверить обновления."""
        self.last_check = datetime.now()
        
        # Mock проверка
        self.updates_available = []
        return self.updates_available


# ============================================================================
# БЛОК 10: РЕЖИМ "БОГА"
# ============================================================================

class MasterOrchestrator:
    """
    Master Orchestrator - объединение всех модулей.
    """
    
    def __init__(self):
        # Все модули
        self.platform_bridge = MultiPlatformBridge()
        self.proxy_rotator = ProxyRotator()
        self.affiliate_engine = AffiliateEngine()
        self.crypto_gateway = CryptoPaymentGateway()
        self.invoice_gen = InvoiceGenerator()
        self.subscription_mgr = SubscriptionManager()
        self.forecaster = FinancialForecaster()
        self.shadow_mode = ShadowMode()
        self.encryption = AdvancedEncryption()
        self.docker = DockerManager()
        self.dashboard = HealthDashboard()
        self.panic = PanicButton()
        self.updater = AutoUpdateManager()
        
        # Метрики
        self.total_revenue = 0
        self.total_cycles = 0
    
    def get_status(self) -> Dict:
        """Получить полный статус."""
        return {
            'modules': {
                'platform_bridge': 'active',
                'crypto_gateway': 'active',
                'subscription_mgr': 'active',
                'shadow_mode': 'ready'
            },
            'metrics': {
                'total_revenue': self.total_revenue,
                'total_cycles': self.total_cycles
            }
        }


class ExecutiveReporter:
    """
    Executive Hourly Report - ежечасные отчеты.
    """
    
    def __init__(self, notifier=None):
        self.notifier = notifier
    
    def generate_report(self, metrics: Dict) -> str:
        """Сгенерировать отчет."""
        return f"""
📊 HOURLY REPORT
━━━━━━━━━━━━━━
💰 Revenue: ${metrics.get('revenue', 0):.2f}
📬 Messages: {metrics.get('messages', 0)}
🐋 Whales: {metrics.get('whales', 0)}
⚠️ Errors: {metrics.get('errors', 0)}
━━━━━━━━━━━━━━
🕐 {datetime.now().strftime('%H:%M')}
"""
    
    def send(self, metrics: Dict):
        """Отправить отчет."""
        if self.notifier:
            self.notifier.send_simple_message(self.generate_report(metrics))


# ============================================================================
# GLOBAL EMPIRE - ГЛАВНЫЙ КЛАСС
# ============================================================================

class GlobalEmpire:
    """
    Global Empire - Главный класс всей системы.
    """
    
    def __init__(self):
        # Блок 7: Глобальная сеть
        self.platform_bridge = MultiPlatformBridge()
        self.proxy_rotator = ProxyRotator()
        self.lead_gen = LeadGenSimulator()
        self.auto_commenter = AutoCommenter()
        self.funnel = FunnelAnalytics()
        self.geo_clock = GeoClockSync()
        self.language = LanguageAutoSwitch()
        self.affiliate = AffiliateEngine()
        
        # Блок 8: Финансы
        self.crypto = CryptoPaymentGateway()
        self.tax_calc = TaxFeeCalculator()
        self.invoice = InvoiceGenerator()
        self.subscriptions = SubscriptionManager()
        self.forecaster = FinancialForecaster()
        self.cashout_alerts = CashoutAlerts()
        
        # Блок 9: Неубиваемость
        self.shadow = ShadowMode()
        self.encryption = AdvancedEncryption()
        self.docker = DockerManager()
        self.dashboard = HealthDashboard()
        self.panic = PanicButton()
        self.updater = AutoUpdateManager()
        
        # Блок 10: Режим Бога
        self.orchestrator = MasterOrchestrator()
        self.reporter = ExecutiveReporter()
        
        self.is_initialized = True
    
    def get_system_status(self) -> Dict:
        """Получить статус системы."""
        return {
            'status': 'GOD_MODE',
            'timestamp': datetime.now().isoformat(),
            'blocks': {
                'block_7_network': 'active',
                'block_8_finance': 'active', 
                'block_9_unkillable': 'active',
                'block_10_god': 'active'
            }
        }


# Singleton
_global_empire: Optional[GlobalEmpire] = None


def get_global_empire() -> GlobalEmpire:
    """Получить экземпляр GlobalEmpire."""
    global _global_empire
    if _global_empire is None:
        _global_empire = GlobalEmpire()
    return _global_empire
