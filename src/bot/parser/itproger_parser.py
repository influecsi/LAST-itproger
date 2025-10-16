import requests
from bs4 import BeautifulSoup
from data.config import Config
import logging

logger = logging.getLogger(__name__)

class ItProgerParser:
    def __init__(self):
        self.base_url = Config.ITPROGER_URL
        self.headers = Config.HEADERS
        
    def get_news(self, count=5):
        """
        Парсит последние новости с itproger.com
        Возвращает список словарей с новостями
        """
        try:
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # Поиск элементов с новостями (структура может меняться)
            articles = soup.find_all('article', class_=True) or soup.find_all('div', class_='article')
            
            for article in articles[:count]:
                try:
                    news_item = self._parse_article(article)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    logger.error(f"Error parsing article: {e}")
                    continue
                    
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def _parse_article(self, article):
        """Парсит отдельную статью"""
        # Заголовок
        title_elem = article.find(['h2', 'h3', 'h4']) or article.find('a')
        title = title_elem.get_text().strip() if title_elem else "Без заголовка"
        
        # Ссылка
        link_elem = article.find('a')
        link = link_elem.get('href') if link_elem else None
        if link and not link.startswith('http'):
            link = f"https://itproger.com{link}"
        
        # Описание
        desc_elem = article.find('p') or article.find('div', class_='content')
        description = desc_elem.get_text().strip() if desc_elem else ""
        
        # Дата (если есть)
        date_elem = article.find('time') or article.find('span', class_='date')
        date = date_elem.get_text().strip() if date_elem else ""
        
        return {
            'title': title,
            'description': description[:200] + "..." if len(description) > 200 else description,
            'link': link,
            'date': date
        }