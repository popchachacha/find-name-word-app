"""Модуль для ИИ анализа персонажей в тексте."""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import Counter
import re
import json
import os

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
except ImportError:
    # Обработка случая, когда библиотеки Transformers не установлены
    pass

from .processor import CharacterStat


@dataclass
class AIAnalysisResult:
    """Результат ИИ анализа персонажа."""
    
    character_name: str
    sentiment: str  # positive, negative, neutral
    sentiment_score: float
    emotion: str    # joy, anger, fear, sadness, etc.
    emotion_score: float
    character_type: str  # protagonist, antagonist, supporting, etc.
    importance_score: float  # от 0 до 1
    description: str


class SimpleTextAnalyzer:
    """Простой анализатор текста без использования тяжёлых ИИ моделей."""
    
    def __init__(self):
        # База знаний для анализа персонажей
        self.character_patterns = {
            'protagonist': ['главный', 'герой', 'героиня', 'основной', 'центральный'],
            'antagonist': ['злодей', 'враг', 'противник', 'антагонист', 'негативный'],
            'supporting': ['друг', 'помощник', 'союзник', 'поддерживающий'],
            'neutral': ['нейтральный', 'обычный', 'простой']
        }
        
        self.emotion_keywords = {
            'joy': ['радость', 'счастье', 'весёлый', 'радостный', 'смех', 'улыбка'],
            'anger': ['гнев', 'злость', 'ярость', 'сердитый', 'злой', 'бешенство'],
            'fear': ['страх', 'ужас', 'опасение', 'боязнь', 'испуг', 'паника'],
            'sadness': ['грусть', 'печаль', 'тоска', 'уныние', 'депрессия'],
            'surprise': ['удивление', 'шок', 'изумление', 'ошеломление'],
            'disgust': ['отвращение', 'омерзение', 'гадливость', 'брезгливость']
        }
        
        self.sentiment_positive = ['хороший', 'добрый', 'милый', 'красивый', 'умный', 'смелый']
        self.sentiment_negative = ['плохой', 'злой', 'уродливый', 'глупый', 'трус', 'жестокий']
    
    def analyze_character(self, character_name: str, context: str = "") -> AIAnalysisResult:
        """Анализирует одного персонажа."""
        # Простой анализ на основе контекста и ключевых слов
        context_lower = context.lower()
        name_lower = character_name.lower()
        
        # Анализ важности (простая эвристика)
        importance_score = self._calculate_importance_score(character_name, context)
        
        # Анализ типа персонажа
        character_type = self._determine_character_type(character_name, context)
        
        # Анализ эмоций
        emotion, emotion_score = self._analyze_emotions(context)
        
        # Анализ тональности
        sentiment, sentiment_score = self._analyze_sentiment(context)
        
        # Генерируем описание
        description = self._generate_description(character_name, character_type, sentiment, emotion)
        
        return AIAnalysisResult(
            character_name=character_name,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            emotion=emotion,
            emotion_score=emotion_score,
            character_type=character_type,
            importance_score=importance_score,
            description=description
        )
    
    def _calculate_importance_score(self, character_name: str, context: str) -> float:
        """Вычисляет важность персонажа на основе простых эвристик."""
        score = 0.5  # базовая оценка
        
        # Длинные имена обычно более важны
        if len(character_name) > 8:
            score += 0.1
        
        # Частота упоминания в контексте
        if context:
            frequency = context.lower().count(character_name.lower())
            score += min(frequency * 0.1, 0.3)
        
        # Ключевые слова важности
        importance_words = ['главный', 'основной', 'центральный', 'важный', 'ключевой']
        for word in importance_words:
            if word in context.lower():
                score += 0.15
        
        return min(score, 1.0)
    
    def _determine_character_type(self, character_name: str, context: str) -> str:
        """Определяет тип персонажа."""
        context_lower = context.lower()
        
        for char_type, keywords in self.character_patterns.items():
            for keyword in keywords:
                if keyword in context_lower:
                    return char_type
        
        return 'neutral'
    
    def _analyze_emotions(self, context: str) -> tuple[str, float]:
        """Анализирует эмоции в контексте."""
        if not context:
            return 'neutral', 0.5
        
        context_lower = context.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in context_lower)
            emotion_scores[emotion] = score
        
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return 'neutral', 0.5
        
        top_emotion = max(emotion_scores, key=emotion_scores.get)
        score = emotion_scores[top_emotion]
        confidence = min(score / max(len(context.split()) / 10, 1), 1.0)
        
        return top_emotion, confidence
    
    def _analyze_sentiment(self, context: str) -> tuple[str, float]:
        """Анализирует тональность текста."""
        if not context:
            return 'neutral', 0.5
        
        context_lower = context.lower()
        
        positive_count = sum(1 for word in self.sentiment_positive if word in context_lower)
        negative_count = sum(1 for word in self.sentiment_negative if word in context_lower)
        
        if positive_count > negative_count:
            return 'positive', min(positive_count / max(positive_count + negative_count, 1), 1.0)
        elif negative_count > positive_count:
            return 'negative', min(negative_count / max(positive_count + negative_count, 1), 1.0)
        else:
            return 'neutral', 0.5
    
    def _generate_description(self, character_name: str, char_type: str, sentiment: str, emotion: str) -> str:
        """Генерирует описание персонажа."""
        type_descriptions = {
            'protagonist': 'Главный персонаж',
            'antagonist': 'Антагонист',
            'supporting': 'Второстепенный персонаж',
            'neutral': 'Нейтральный персонаж'
        }
        
        emotion_descriptions = {
            'joy': 'радостный',
            'anger': 'гневливый',
            'fear': 'пугливый',
            'sadness': 'грустный',
            'surprise': 'удивлённый',
            'disgust': 'отвращённый',
            'neutral': 'спокойный'
        }
        
        sentiment_descriptions = {
            'positive': 'положительный',
            'negative': 'отрицательный',
            'neutral': 'нейтральный'
        }
        
        parts = [
            type_descriptions.get(char_type, 'Персонаж'),
            f"({sentiment_descriptions.get(sentiment, 'нейтральный')})",
            f"с эмоцией {emotion_descriptions.get(emotion, 'спокойствие')}"
        ]
        
        return f"{character_name} — {', '.join(parts)}"


class AdvancedAIAnalyzer:
    """Продвинутый ИИ анализатор с использованием трансформеров."""
    
    def __init__(self):
        self.classifier = None
        self.sentiment_analyzer = None
        self.emotion_analyzer = None
        self._load_models()
    
    def _load_models(self):
        """Загружает модели ИИ (если доступны)."""
        try:
            print("Загрузка ИИ моделей...")
            
            # Модель для анализа эмоций
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Модель для анализа тональности
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            print("Модели успешно загружены!")
            
        except Exception as e:
            print(f"Не удалось загрузить ИИ модели: {e}")
            print("Используется простой анализатор")
    
    def analyze_character(self, character_name: str, context: str = "") -> AIAnalysisResult:
        """Анализирует персонажа с использованием ИИ."""
        # Если модели не загружены, используем простой анализатор
        if not self.emotion_analyzer or not self.sentiment_analyzer:
            simple_analyzer = SimpleTextAnalyzer()
            return simple_analyzer.analyze_character(character_name, context)
        
        # ИИ анализ
        combined_text = f"{character_name}: {context}" if context else character_name
        
        # Анализ эмоций
        emotion_results = self.emotion_analyzer(combined_text)
        top_emotion = max(emotion_results[0], key=lambda x: x['score'])
        
        # Анализ тональности
        sentiment_results = self.sentiment_analyzer(combined_text)
        top_sentiment = max(sentiment_results[0], key=lambda x: x['score'])
        
        # Простое определение типа персонажа (можно улучшить)
        character_type = self._determine_character_type_ai(combined_text)
        
        # Вычисление важности
        importance_score = self._calculate_importance_score_ai(character_name, context)
        
        return AIAnalysisResult(
            character_name=character_name,
            sentiment=top_sentiment['label'].lower(),
            sentiment_score=top_sentiment['score'],
            emotion=top_emotion['label'].lower(),
            emotion_score=top_emotion['score'],
            character_type=character_type,
            importance_score=importance_score,
            description=f"ИИ анализ: {top_emotion['label']} эмоция, {top_sentiment['label']} тональность"
        )
    
    def _determine_character_type_ai(self, text: str) -> str:
        """Определяет тип персонажа с помощью ИИ."""
        # Простая эвристика - можно заменить на более сложную модель
        if any(word in text.lower() for word in ['главный', 'герой', 'основной']):
            return 'protagonist'
        elif any(word in text.lower() for word in ['злодей', 'враг', 'антигерой']):
            return 'antagonist'
        else:
            return 'supporting'
    
    def _calculate_importance_score_ai(self, character_name: str, context: str) -> float:
        """Вычисляет важность персонажа с помощью ИИ."""
        # Простая эвристика для важности
        base_score = 0.5
        if context:
            # Анализируем длину и сложность контекста
            words = context.split()
            if len(words) > 10:
                base_score += 0.2
            if len(character_name) > 5:
                base_score += 0.1
        return min(base_score, 1.0)


class AIAnalysisManager:
    """Менеджер для ИИ анализа персонажей."""
    
    def __init__(self, use_advanced: bool = False):
        self.use_advanced = use_advanced
        if use_advanced:
            self.analyzer = AdvancedAIAnalyzer()
        else:
            self.analyzer = SimpleTextAnalyzer()
    
    def analyze_characters(
        self, 
        characters: List[CharacterStat], 
        context_data: Optional[Dict[str, str]] = None
    ) -> List[AIAnalysisResult]:
        """Анализирует список персонажей."""
        results = []
        
        for char in characters:
            context = ""
            if context_data and char.name in context_data:
                context = context_data[char.name]
            
            result = self.analyzer.analyze_character(char.name, context)
            results.append(result)
        
        return results
    
    def export_analysis_to_json(self, results: List[AIAnalysisResult], filepath: str):
        """Экспортирует результаты анализа в JSON файл."""
        export_data = []
        for result in results:
            export_data.append({
                'character_name': result.character_name,
                'sentiment': result.sentiment,
                'sentiment_score': result.sentiment_score,
                'emotion': result.emotion,
                'emotion_score': result.emotion_score,
                'character_type': result.character_type,
                'importance_score': result.importance_score,
                'description': result.description
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def load_context_data(self, filepath: str) -> Dict[str, str]:
        """Загружает контекстные данные из файла."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}