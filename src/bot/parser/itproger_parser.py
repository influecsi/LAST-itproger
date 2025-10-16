import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ITProgerParser:
    def __init__(self):
        self.base_url = "https://itproger.com"
        self.news_url = "https://itproger.com/news"
        self.session = None
        self.cache = {}
        self.cache_timeout = timedelta(minutes=10)  # Кэш на 10 минут
        
    async def get_session(self):
        """Создает aiohttp сессию при необходимости"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
        return self.session

    async def close_session(self):
        """Закрывает сессию"""
        if self.session:
            await self.session.close()
            self.session = None

    def _get_cache_key(self, page: int) -> str:
        return f"news_page_{page}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Проверяет валидность кэша"""
        if cache_key in self.cache:
            cache_time, _ = self.cache[cache_key]
            return datetime.now() - cache_time < self.cache_timeout
        return False

    async def get_news_list(self, page: int = 1) -> List[Dict]:
        """Асинхронно получить список последних новостей"""
        cache_key = self._get_cache_key(page)
        
        # Проверяем кэш
        if self._is_cache_valid(cache_key):
            logger.info(f"Используем кэш для страницы {page}")
            return self.cache[cache_key][1]
        
        try:
            session = await self.get_session()
            
            async with session.get(f"{self.news_url}/{page}") as response:
                if response.status != 200:
                    logger.error(f"Ошибка HTTP {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                articles = soup.find_all('article', class_='article')
                
                news_list = []
                
                # Создаем задачи для параллельной обработки статей
                tasks = [self._parse_article(article) for article in articles]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, dict):
                        news_list.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Ошибка парсинга статьи: {result}")
                
                # Сохраняем в кэш
                self.cache[cache_key] = (datetime.now(), news_list)
                logger.info(f"Загружено {len(news_list)} статей с страницы {page}")
                
                return news_list
                
        except Exception as e:
            logger.error(f"Ошибка при получении списка новостей: {e}")
            return []

    async def _parse_article(self, article) -> Optional[Dict]:
        """Парсит отдельную статью"""
        try:
            # Извлекаем заголовок
            title_elem = article.find('h2')
            title = title_elem.text.strip() if title_elem else "Без заголовка"
            
            # Извлекаем ссылку
            link_elem = article.find('a')
            if not link_elem or not link_elem.has_attr('href'):
                return None
                
            link = self.base_url + link_elem['href']
            
            # Извлекаем изображение
            img_elem = article.find('img')
            image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else ""
            
            # Извлекаем краткое описание
            desc_elem = article.find('p')
            description = desc_elem.text.strip() if desc_elem else "Описание отсутствует"
            
            # Обрезаем длинное описание
            if len(description) > 200:
                description = description[:200] + "..."
            
            # Форматируем описание для markdown
            description = self._format_text_for_markdown(description)
            
            return {
                'title': title,
                'url': link,
                'image': image_url,
                'description': description,
                'full_content': None
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге статьи: {e}")
            return None

    async def get_article_content(self, article_url: str) -> Dict:
        """Асинхронно получить полное содержимое статьи"""
        cache_key = f"content_{article_url}"
        
        # Проверяем кэш контента
        if self._is_cache_valid(cache_key):
            logger.info(f"Используем кэш контента для {article_url}")
            return self.cache[cache_key][1]
        
        try:
            session = await self.get_session()
            
            async with session.get(article_url) as response:
                if response.status != 200:
                    return {"content": "Ошибка загрузки", "has_code": False}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Находим основной контент статьи
                content_div = soup.find('div', class_='content')
                
                if not content_div:
                    return {"content": "Контент не найден", "has_code": False}
                
                # Извлекаем текст и форматируем код
                content_text = ""
                has_code = False
                
                for element in content_div.find_all(['p', 'pre']):
                    if element.name == 'pre':
                        # Это блок кода
                        code_text = element.get_text().strip()
                        if code_text:
                            content_text += f"```\n{code_text}\n```\n\n"
                            has_code = True
                    else:
                        # Это обычный текст
                        text = element.get_text().strip()
                        if text:
                            content_text += f"{text}\n\n"
                
                result = {
                    "content": content_text.strip(),
                    "has_code": has_code
                }
                
                # Сохраняем в кэш
                self.cache[cache_key] = (datetime.now(), result)
                
                return result
                
        except Exception as e:
            logger.error(f"Ошибка при получении контента статьи: {e}")
            return {"content": "Ошибка при загрузке контента", "has_code": False}

    def _format_text_for_markdown(self, text: str) -> str:
        """Форматирование текста для markdown"""
        # Экранируем специальные символы Markdown
        text = re.sub(r'([*_`\[\]()])', r'\\\1', text)
        return text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()