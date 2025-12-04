"""Модуль авторизации и управления пользователями."""

from __future__ import annotations

import sqlite3
import hashlib
import secrets
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import contextmanager

try:
    from flask import Flask, request, jsonify, session, render_template_string
    from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
    from werkzeug.security import generate_password_hash, check_password_hash
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
except ImportError:
    # Обработка случая, когда Flask не установлен
    pass


@dataclass
class User:
    """Модель пользователя."""
    
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    api_key: Optional[str] = None


class SimpleAuthManager:
    """Простой менеджер авторизации с SQLite базой данных."""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных пользователей."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    api_key TEXT,
                    api_usage INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 100
                )
            ''')
            
            # Создаём админа по умолчанию, если его нет
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
            if cursor.fetchone()[0] == 0:
                admin_password = generate_password_hash("admin123")
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, is_admin)
                    VALUES (?, ?, ?, ?)
                ''', ("admin", "admin@example.com", admin_password, True))
            
            conn.commit()
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Создаёт нового пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем уникальность username и email
                cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
                if cursor.fetchone():
                    return {"success": False, "error": "Username или email уже существует"}
                
                # Хешируем пароль
                password_hash = generate_password_hash(password)
                api_key = secrets.token_urlsafe(32)
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, api_key)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash, api_key))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "success": True, 
                    "user_id": user_id,
                    "api_key": api_key,
                    "message": "Пользователь успешно создан"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка создания пользователя: {e}"}
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Аутентификация пользователя."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, password_hash, is_active, is_admin, api_key, daily_limit
                    FROM users WHERE username = ? OR email = ?
                ''', (username, username))
                
                user_row = cursor.fetchone()
                if not user_row:
                    return {"success": False, "error": "Пользователь не найден"}
                
                user_id, username_db, email, password_hash, is_active, is_admin, api_key, daily_limit = user_row
                
                if not is_active:
                    return {"success": False, "error": "Аккаунт заблокирован"}
                
                if not check_password_hash(password_hash, password):
                    return {"success": False, "error": "Неверный пароль"}
                
                # Обновляем время последнего входа
                cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
                conn.commit()
                
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "username": username_db,
                        "email": email,
                        "is_admin": bool(is_admin),
                        "api_key": api_key,
                        "daily_limit": daily_limit
                    }
                }
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка аутентификации: {e}"}
    
    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Проверяет API ключ и возвращает информацию о пользователе."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, is_active, api_usage, daily_limit
                    FROM users WHERE api_key = ?
                ''', (api_key,))
                
                user_row = cursor.fetchone()
                if not user_row:
                    return {"success": False, "error": "Неверный API ключ"}
                
                user_id, username, email, is_active, api_usage, daily_limit = user_row
                
                if not is_active:
                    return {"success": False, "error": "Аккаунт заблокирован"}
                
                # Проверяем лимиты использования
                if api_usage >= daily_limit:
                    return {"success": False, "error": "Превышен дневной лимит запросов"}
                
                # Обновляем счётчик использования
                cursor.execute('UPDATE users SET api_usage = api_usage + 1 WHERE id = ?', (user_id,))
                conn.commit()
                
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "username": username,
                        "email": email,
                        "api_usage": api_usage + 1,
                        "daily_limit": daily_limit
                    }
                }
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка проверки API ключа: {e}"}
    
    def get_users_list(self, admin_user_id: int) -> Dict[str, Any]:
        """Получает список пользователей (только для админов)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем права админа
                cursor.execute('SELECT is_admin FROM users WHERE id = ?', (admin_user_id,))
                admin_row = cursor.fetchone()
                if not admin_row or not admin_row[0]:
                    return {"success": False, "error": "Недостаточно прав"}
                
                cursor.execute('''
                    SELECT id, username, email, is_active, is_admin, created_at, last_login, api_usage
                    FROM users ORDER BY created_at DESC
                ''')
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "is_active": bool(row[3]),
                        "is_admin": bool(row[4]),
                        "created_at": row[5],
                        "last_login": row[6],
                        "api_usage": row[7]
                    })
                
                return {"success": True, "users": users}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка получения списка пользователей: {e}"}
    
    def reset_daily_usage(self):
        """Сбрасывает дневное использование для всех пользователей."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET api_usage = 0')
            conn.commit()


class FlaskAuthAPI:
    """Flask API для авторизации."""
    
    def __init__(self, auth_manager: SimpleAuthManager, secret_key: str = None):
        self.auth_manager = auth_manager
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        
        self.app = Flask(__name__)
        self.app.secret_key = self.secret_key
        
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'
        
        self._setup_routes()
        self._setup_api_routes()
    
    def _setup_routes(self):
        """Настройка веб-маршрутов для авторизации."""
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                result = self.auth_manager.authenticate_user(username, password)
                if result['success']:
                    return jsonify(result)
                else:
                    return jsonify(result), 401
            
            return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Вход в систему</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; }
                        .form-group { margin-bottom: 15px; }
                        label { display: block; margin-bottom: 5px; }
                        input { width: 100%; padding: 8px; box-sizing: border-box; }
                        button { background: #007bff; color: white; padding: 10px 15px; border: none; cursor: pointer; }
                        .error { color: red; }
                    </style>
                </head>
                <body>
                    <h2>Вход в систему</h2>
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="username">Имя пользователя или Email:</label>
                            <input type="text" id="username" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Пароль:</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        <button type="submit">Войти</button>
                    </form>
                    <div id="message"></div>
                    
                    <script>
                        document.getElementById('loginForm').addEventListener('submit', async (e) => {
                            e.preventDefault();
                            const formData = {
                                username: document.getElementById('username').value,
                                password: document.getElementById('password').value
                            };
                            
                            try {
                                const response = await fetch('/login', {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify(formData)
                                });
                                
                                const result = await response.json();
                                
                                if (result.success) {
                                    document.getElementById('message').innerHTML = 
                                        '<p class="success">Успешный вход! Добро пожаловать, ' + 
                                        result.user.username + '</p>';
                                } else {
                                    document.getElementById('message').innerHTML = 
                                        '<p class="error">' + result.error + '</p>';
                                }
                            } catch (error) {
                                document.getElementById('message').innerHTML = 
                                    '<p class="error">Ошибка соединения</p>';
                            }
                        });
                    </script>
                </body>
                </html>
            ''')
    
    def _setup_api_routes(self):
        """Настройка API маршрутов."""
        
        @self.app.route('/api/register', methods=['POST'])
        def register():
            data = request.get_json()
            result = self.auth_manager.create_user(
                data['username'], 
                data['email'], 
                data['password']
            )
            return jsonify(result)
        
        @self.app.route('/api/verify', methods=['POST'])
        def verify_api():
            data = request.get_json()
            api_key = data.get('api_key')
            result = self.auth_manager.verify_api_key(api_key)
            return jsonify(result)
        
        @self.app.route('/api/users', methods=['GET'])
        def get_users():
            # В реальном приложении здесь должна быть проверка авторизации
            admin_id = request.args.get('admin_id', 1)
            result = self.auth_manager.get_users_list(int(admin_id))
            return jsonify(result)
    
    def run(self, host='localhost', port=5000, debug=False):
        """Запускает сервер авторизации."""
        print(f"Запуск сервера авторизации на {host}:{port}")
        print("Логин администратора: admin / admin123")
        self.app.run(host=host, port=port, debug=debug)


class APILimiter:
    """Ограничитель запросов для API."""
    
    def __init__(self, auth_manager: SimpleAuthManager):
        self.auth_manager = auth_manager
    
    def check_rate_limit(self, user_id: int) -> Dict[str, Any]:
        """Проверяет лимиты пользователя."""
        try:
            with sqlite3.connect(self.auth_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT api_usage, daily_limit FROM users WHERE id = ?', (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return {"success": False, "error": "Пользователь не найден"}
                
                usage, limit = row
                
                if usage >= limit:
                    return {"success": False, "error": "Превышен лимит запросов", "usage": usage, "limit": limit}
                
                return {"success": True, "usage": usage, "limit": limit}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка проверки лимитов: {e}"}


def create_auth_system(db_path: str = "users.db") -> SimpleAuthManager:
    """Создаёт систему авторизации."""
    return SimpleAuthManager(db_path)


def create_auth_api(auth_manager: SimpleAuthManager, port: int = 5000) -> FlaskAuthAPI:
    """Создаёт Flask API для авторизации."""
    return FlaskAuthAPI(auth_manager, secret_key="your-secret-key-here")


# Утилиты для работы с авторизацией
def generate_secure_api_key() -> str:
    """Генерирует безопасный API ключ."""
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет пароль."""
    return check_password_hash(password_hash, password)


def schedule_daily_reset(auth_manager: SimpleAuthManager):
    """Планирует ежедневный сброс лимитов (нужно интегрировать с системным планировщиком)."""
    import threading
    import time
    from datetime import datetime, timedelta
    
    def reset_worker():
        while True:
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            tomorrow_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            sleep_duration = (tomorrow_midnight - now).total_seconds()
            
            time.sleep(sleep_duration)
            auth_manager.reset_daily_usage()
            print(f"Сброшены дневные лимиты в {datetime.now()}")
    
    reset_thread = threading.Thread(target=reset_worker, daemon=True)
    reset_thread.start()