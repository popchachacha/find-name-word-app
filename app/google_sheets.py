"""Модуль для работы с Google Sheets API."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    # Обработка случая, когда библиотеки Google не установлены
    pass

from .processor import CharacterStat


@dataclass
class GoogleSheetsConfig:
    """Конфигурация для Google Sheets API."""
    
    credentials_file: str = "credentials.json"
    token_file: str = "token.json"
    spreadsheet_id: Optional[str] = None
    sheet_name: str = "Characters"


class GoogleSheetsProcessor:
    """Процессор для экспорта данных в Google Sheets."""
    
    # Области доступа для Google Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, config: GoogleSheetsConfig = None):
        self.config = config or GoogleSheetsConfig()
        self.service = None
        self.credentials = None
    
    def authenticate(self) -> bool:
        """Аутентификация в Google API."""
        try:
            creds = None
            token_file = Path(self.config.token_file)
            
            # Загружаем сохранённые учетные данные, если они есть
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(
                    str(token_file), self.SCOPES
                )
            
            # Если нет валидных учетных данных, запрашиваем их
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Сохраняем учетные данные для следующего запуска
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('sheets', 'v4', credentials=creds)
            return True
            
        except FileNotFoundError:
            print(f"Не найден файл {self.config.credentials_file}")
            print("Инструкции по получению учетных данных:")
            print("1. Перейдите на https://console.cloud.google.com/")
            print("2. Создайте новый проект или выберите существующий")
            print("3. Включите Google Sheets API")
            print("4. Создайте учетные данные OAuth 2.0")
            print("5. Сохраните файл как 'credentials.json' в папку проекта")
            return False
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return False
    
    def create_spreadsheet(self, title: str) -> Optional[str]:
        """Создаёт новую таблицу и возвращает её ID."""
        if not self.service:
            return None
            
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            result = self.service.spreadsheets().create(
                body=spreadsheet, fields='spreadsheetId'
            ).execute()
            
            return result.get('spreadsheetId')
        except HttpError as error:
            print(f"Ошибка создания таблицы: {error}")
            return None
    
    def export_characters(
        self, 
        characters: List[CharacterStat], 
        spreadsheet_id: Optional[str] = None,
        sheet_name: str = "Characters"
    ) -> bool:
        """Экспортирует данные о персонажах в Google Sheets."""
        if not self.service:
            return False
        
        try:
            # Если не указан ID таблицы, создаём новую
            if not spreadsheet_id:
                spreadsheet_id = self.create_spreadsheet(
                    f"Анализ персонажей - {len(characters)} записей"
                )
                if not spreadsheet_id:
                    return False
            
            # Подготавливаем данные для экспорта
            values = [
                ['Персонаж', 'Количество упоминаний'],  # Заголовки
            ]
            
            for char in characters:
                values.append([char.name, char.count])
            
            # Создаём тело запроса
            body = {
                'values': values
            }
            
            # Записываем данные в таблицу
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Экспортировано {result.get('updates').get('updatedRows')} строк в Google Sheets")
            return True
            
        except HttpError as error:
            print(f"Ошибка экспорта в Google Sheets: {error}")
            return False
    
    def import_from_sheets(self, spreadsheet_id: str, range_name: str = "A:B") -> List[Dict[str, Any]]:
        """Импортирует данные из Google Sheets."""
        if not self.service:
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return []
            
            # Пропускаем заголовки
            headers = values[0]
            data = []
            
            for row in values[1:]:
                if len(row) >= 2:
                    data.append({
                        'name': row[0],
                        'count': int(row[1]) if row[1].isdigit() else 0
                    })
            
            return data
            
        except HttpError as error:
            print(f"Ошибка импорта из Google Sheets: {error}")
            return []
    
    def add_analysis_column(
        self, 
        spreadsheet_id: str, 
        analysis_data: List[str],
        column_name: str = "ИИ Анализ"
    ) -> bool:
        """Добавляет столбец с результатами ИИ анализа."""
        if not self.service or not analysis_data:
            return False
        
        try:
            # Подготавливаем данные (заголовок + результаты анализа)
            values = [[column_name]] + [[analysis] for analysis in analysis_data]
            
            body = {
                'values': values
            }
            
            # Записываем в столбец C
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range="C1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
            
        except HttpError as error:
            print(f"Ошибка добавления анализа: {error}")
            return False