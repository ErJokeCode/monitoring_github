import asyncio
import logging
from typing import Any
from nats.aio.client import Client as NATS
import json
import time
from config import settings

_log = logging.getLogger(__name__)

class NATSClient:
    def __init__(self):
        self.server = settings.NATS_URL
        self.nc = NATS()
        self.running = False
    
    async def connect(self):
        """Подключение к серверу NATS"""
        await self.nc.connect(self.server)
        _log.info(f"Подключено к {self.server}")
    
    async def publish(self, data, subject: str | None = None):
        """Отправка сообщения"""
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()
            
        if subject is None:
            subject = settings.NATS_subject_events
        
        await self.nc.publish(subject, data)
        _log.info(f"Отправлено в {subject}: {data[:50]}...")
    
    async def subscribe(self, subject: str | None = None, callback: Any | None = None):
        """Подписка на тему"""
        if callback is None:
            callback = self.default_callback
        if subject is None:
            subject = settings.NATS_subject_events
        
        sid = await self.nc.subscribe(subject, cb=callback)
        _log.info(f"Подписан на {subject}")
        return sid
    
    async def default_callback(self, msg):
        """Обработчик сообщений по умолчанию"""
        subject = msg.subject
        data = msg.data.decode()
        _log.info(f"[{time.strftime('%H:%M:%S')}] Получено из {subject}: {data}")
    
    async def request(self, subject, data, timeout=5):
        """Запрос-ответ"""
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()
        
        response = await self.nc.request(subject, data, timeout=timeout)
        return response.data.decode()
    
    async def close(self):
        """Закрытие соединения"""
        await self.nc.close()
        _log.info("Соединение закрыто")