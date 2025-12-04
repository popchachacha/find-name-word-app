"""Tkinter application for processing Word documents."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Dict, Any, Optional

from .processor import DocumentProcessor
from .google_sheets import GoogleSheetsProcessor, GoogleSheetsConfig
from .ai_analysis import AIAnalysisManager, AIAnalysisResult
from .auth import SimpleAuthManager


def _resource_path(path: str | Path | None) -> str:
    return str(Path(path).expanduser()) if path else ""


class CharacterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Обработка Word-файлов - Enhanced Edition")
        self.geometry("1000x700")
        self.resizable(True, True)

        self.processor = DocumentProcessor()
        self.file_path: Path | None = None
        self.output_dir: Path | None = None

        # Новые компоненты
        self.google_sheets = GoogleSheetsProcessor()
        self.ai_analyzer = AIAnalysisManager(use_advanced=False)  # Простой анализатор по умолчанию
        self.auth_manager = SimpleAuthManager()
        
        # Переменные интерфейса
        self.min_mentions = tk.IntVar(value=1)
        self.column_var = tk.IntVar(value=2)
        self.ignore_case_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Загрузите документ для начала")
        
        # Новые настройки
        self.use_ai_var = tk.BooleanVar(value=False)
        self.use_google_sheets_var = tk.BooleanVar(value=False)
        self.export_ai_analysis_var = tk.BooleanVar(value=False)
        self.selected_spreadsheet_id = tk.StringVar(value="")
        self.authentication_status = tk.StringVar(value="Не авторизован")

        # Данные результатов
        self.characters_data: List = []
        self.ai_analysis_results: List[AIAnalysisResult] = []

        self._configure_style()
        self._build_layout()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f7f7fb")
        style.configure("TLabel", background="#f7f7fb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Secondary.TButton", padding=6)
        style.configure("Success.TButton", padding=6)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("AI.TLabel", background="#e8f5e8", font=("Segoe UI", 9))
        style.configure("Sheets.TLabel", background="#e3f2fd", font=("Segoe UI", 9))

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            container,
            text="Автоматическая обработка таблиц Word - Enhanced Edition",
            style="Title.TLabel",
        )
        header.pack(anchor=tk.W)

        description = ttk.Label(
            container,
            text="Выделяйте персонажей из второго столбца, создавайте отчеты, анализируйте с ИИ и экспортируйте в Google Sheets",
            wraplength=940,
        )
        description.pack(anchor=tk.W, pady=(4, 12))

        controls = ttk.Frame(container)
        controls.pack(fill=tk.X, pady=5)

        file_button = ttk.Button(
            controls,
            text="Выбрать документ",
            style="Accent.TButton",
            command=self.select_file,
        )
        file_button.grid(row=0, column=0, padx=(0, 10))

        self.file_label = ttk.Label(
            controls,
            text="Файл не выбран",
            width=45,
        )
        self.file_label.grid(row=0, column=1, sticky=tk.W)

        directory_button = ttk.Button(
            controls,
            text="Папка сохранения",
            style="Secondary.TButton",
            command=self.select_directory,
        )
        directory_button.grid(row=1, column=0, pady=5, padx=(0, 10), sticky=tk.W)

        self.dir_label = ttk.Label(controls, text="Используется папка документа", width=45)
        self.dir_label.grid(row=1, column=1, sticky=tk.W)

        options_frame = ttk.Frame(container)
        options_frame.pack(fill=tk.X, pady=10)

        ttk.Label(options_frame, text="Минимальное количество упоминаний:").grid(
            row=0, column=0, sticky=tk.W
        )
        self.min_spinbox = ttk.Spinbox(
            options_frame,
            from_=1,
            to=99,
            width=5,
            textvariable=self.min_mentions,
        )
        self.min_spinbox.grid(row=0, column=1, padx=(8, 20))

        ttk.Label(options_frame, text="Столбец с персонажами:").grid(
            row=0, column=2, sticky=tk.W
        )
        self.column_spinbox = ttk.Spinbox(
            options_frame,
            from_=1,
            to=20,
            width=5,
            textvariable=self.column_var,
        )
        self.column_spinbox.grid(row=0, column=3, padx=(8, 0))

        run_button = ttk.Button(
            options_frame,
            text="Обработать документ",
            style="Accent.TButton",
            command=self.process_file,
        )
        run_button.grid(row=0, column=4, padx=(20, 0))

        copy_button = ttk.Button(
            options_frame,
            text="Скопировать список",
            style="Secondary.TButton",
            command=self.copy_results,
        )
        copy_button.grid(row=0, column=5, padx=(10, 0))

        # Новые кнопки для экспорта
        export_button = ttk.Button(
            options_frame,
            text="Экспорт в Google Sheets",
            style="Success.TButton",
            command=self.export_to_google_sheets,
            state=tk.DISABLED
        )
        export_button.grid(row=0, column=6, padx=(10, 0))

        ai_button = ttk.Button(
            options_frame,
            text="ИИ Анализ",
            style="Success.TButton",
            command=self.run_ai_analysis,
            state=tk.DISABLED
        )
        ai_button.grid(row=0, column=7, padx=(10, 0))

        # Сохраняем ссылки на кнопки для управления их состоянием
        self.export_button = export_button
        self.ai_button = ai_button

        ttk.Checkbutton(
            options_frame,
            text="Игнорировать регистр имён",
            variable=self.ignore_case_var,
        ).grid(row=1, column=0, columnspan=3, pady=(8, 0), sticky=tk.W)

        # Секция новых возможностей
        enhanced_frame = ttk.LabelFrame(container, text="Расширенные возможности", padding=10)
        enhanced_frame.pack(fill=tk.X, pady=10)

        # ИИ Анализ
        ai_frame = ttk.Frame(enhanced_frame)
        ai_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            ai_frame,
            text="Использовать ИИ анализ персонажей",
            variable=self.use_ai_var,
            command=self._toggle_ai_options
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Checkbutton(
            ai_frame,
            text="Экспортировать ИИ анализ",
            variable=self.export_ai_analysis_var,
            state=tk.DISABLED
        ).grid(row=1, column=0, padx=(20, 0), sticky=tk.W)

        self.ai_status_label = ttk.Label(
            ai_frame,
            text="ИИ: Не загружен",
            style="AI.TLabel"
        )
        self.ai_status_label.grid(row=0, column=1, padx=(20, 0), sticky=tk.W)

        # Google Sheets
        sheets_frame = ttk.Frame(enhanced_frame)
        sheets_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            sheets_frame,
            text="Экспортировать в Google Sheets",
            variable=self.use_google_sheets_var,
            command=self._toggle_google_sheets_options
        ).grid(row=0, column=0, sticky=tk.W)

        ttk.Button(
            sheets_frame,
            text="Авторизация Google",
            command=self._google_auth,
            style="Secondary.TButton"
        ).grid(row=0, column=1, padx=(20, 0))

        self.google_status_label = ttk.Label(
            sheets_frame,
            text="Google Sheets: Не авторизован",
            style="Sheets.TLabel"
        )
        self.google_status_label.grid(row=1, column=0, sticky=tk.W)

        # Авторизация
        auth_frame = ttk.Frame(enhanced_frame)
        auth_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            auth_frame,
            text="Создать пользователя",
            command=self._create_user_dialog,
            style="Secondary.TButton"
        ).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(
            auth_frame,
            text="Авторизация",
            command=self._login_dialog,
            style="Secondary.TButton"
        ).grid(row=0, column=1)

        ttk.Label(
            auth_frame,
            textvariable=self.authentication_status
        ).grid(row=1, column=0, sticky=tk.W)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("character", "count", "type", "sentiment", "emotion")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )
        self.tree.heading("character", text="Персонаж")
        self.tree.heading("count", text="Количество")
        self.tree.heading("type", text="Тип")
        self.tree.heading("sentiment", text="Тональность")
        self.tree.heading("emotion", text="Эмоция")
        self.tree.column("character", width=250)
        self.tree.column("count", width=80, anchor=tk.CENTER)
        self.tree.column("type", width=100)
        self.tree.column("sentiment", width=100)
        self.tree.column("emotion", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        status_frame = ttk.Frame(container)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)

    def select_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Выберите .docx файл",
            filetypes=[("Word файлы", "*.docx")],
        )
        if not file_path:
            return
        self.file_path = Path(file_path)
        self.file_label.config(text=self.file_path.name)
        self.status_var.set("Файл выбран. Укажите параметры и запустите обработку")

    def select_directory(self) -> None:
        directory = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not directory:
            return
        self.output_dir = Path(directory)
        self.dir_label.config(text=self.output_dir.name)

    def process_file(self) -> None:
        if not self.file_path:
            messagebox.showwarning("Нет файла", "Сначала выберите документ")
            return

        minimum = max(1, self.min_mentions.get())
        column_index = max(1, self.column_var.get()) - 1
        ignore_case = self.ignore_case_var.get()

        try:
            result = self.processor.process(
                self.file_path, column_index=column_index
            )
            output_dir = self.output_dir or self.file_path.parent
            output_name = f"{self.file_path.stem}_result.docx"
            output_path = output_dir / output_name
            self.processor.export_report(
                result,
                output_path,
                minimum_mentions=minimum,
                ignore_case=ignore_case,
            )
            stats = self.processor.summarise(
                result.characters, ignore_case=ignore_case
            )
            self.populate_tree(stats, minimum)
            self.status_var.set(
                f"Готово! Файл сохранён: {_resource_path(output_path)}"
            )
            messagebox.showinfo(
                "Успех",
                f"Файл обработан и сохранён как:\n{_resource_path(output_path)}",
            )
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Ошибка", str(exc))
            self.status_var.set("Ошибка обработки. Проверьте документ.")
            self._update_button_states()

    def _toggle_ai_options(self):
        """Обработка включения/выключения ИИ анализа."""
        state = tk.NORMAL if self.use_ai_var.get() else tk.DISABLED
        self.export_ai_analysis_var.set(False)
        
        # Обновляем статус ИИ
        if self.use_ai_var.get():
            self.ai_status_label.config(text="ИИ: Анализ включён")
        else:
            self.ai_status_label.config(text="ИИ: Отключён")
        
        self._update_button_states()

    def _toggle_google_sheets_options(self):
        """Обработка включения/выключения Google Sheets."""
        if self.use_google_sheets_var.get():
            self.google_status_label.config(text="Google Sheets: Ожидание авторизации...")
        else:
            self.google_status_label.config(text="Google Sheets: Отключён")
        
        self._update_button_states()

    def _google_auth(self):
        """Авторизация в Google Sheets."""
        if not self.use_google_sheets_var.get():
            messagebox.showwarning("Внимание", "Сначала включите экспорт в Google Sheets")
            return

        self.status_var.set("Выполняется авторизация в Google...")
        self.update()

        success = self.google_sheets.authenticate()
        if success:
            self.google_status_label.config(text="Google Sheets: Авторизован")
            self.status_var.set("Авторизация в Google Sheets успешна")
            messagebox.showinfo("Успех", "Авторизация в Google Sheets выполнена успешно!")
        else:
            self.google_status_label.config(text="Google Sheets: Ошибка авторизации")
            self.status_var.set("Ошибка авторизации в Google Sheets")
            messagebox.showerror("Ошибка", "Не удалось авторизоваться в Google Sheets. Проверьте файл credentials.json")
        
        self._update_button_states()

    def _create_user_dialog(self):
        """Диалог создания нового пользователя."""
        dialog = tk.Toplevel(self)
        dialog.title("Создание пользователя")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Поля ввода
        ttk.Label(dialog, text="Имя пользователя:").pack(pady=5)
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.pack()

        ttk.Label(dialog, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(dialog, width=30)
        email_entry.pack()

        ttk.Label(dialog, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(dialog, show="*", width=30)
        password_entry.pack()

        result_label = ttk.Label(dialog, text="")
        result_label.pack(pady=10)

        def create_user():
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            if not all([username, email, password]):
                result_label.config(text="Заполните все поля", foreground="red")
                return

            result = self.auth_manager.create_user(username, email, password)
            if result["success"]:
                result_label.config(
                    text=f"Пользователь создан!\nAPI ключ: {result['api_key'][:20]}...",
                    foreground="green"
                )
            else:
                result_label.config(text=result["error"], foreground="red")

        ttk.Button(dialog, text="Создать", command=create_user).pack(pady=10)
        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack()

    def _login_dialog(self):
        """Диалог авторизации пользователя."""
        dialog = tk.Toplevel(self)
        dialog.title("Авторизация")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Поля ввода
        ttk.Label(dialog, text="Имя пользователя или Email:").pack(pady=5)
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.pack()

        ttk.Label(dialog, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(dialog, show="*", width=30)
        password_entry.pack()

        result_label = ttk.Label(dialog, text="")
        result_label.pack(pady=10)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not all([username, password]):
                result_label.config(text="Заполните все поля", foreground="red")
                return

            result = self.auth_manager.authenticate_user(username, password)
            if result["success"]:
                user = result["user"]
                self.authentication_status.set(f"Авторизован: {user['username']}")
                result_label.config(text="Успешная авторизация!", foreground="green")
                dialog.destroy()
            else:
                result_label.config(text=result["error"], foreground="red")

        ttk.Button(dialog, text="Войти", command=login).pack(pady=10)
        ttk.Button(dialog, text="Закрыть", command=dialog.destroy).pack()

    def run_ai_analysis(self):
        """Запуск ИИ анализа персонажей."""
        if not self.characters_data:
            messagebox.showwarning("Внимание", "Сначала обработайте документ")
            return

        self.status_var.set("Выполняется ИИ анализ...")
        self.update()

        try:
            # Создаём контекст для каждого персонажа (упрощённо)
            context_data = {}
            for char in self.characters_data:
                # В реальном приложении здесь должен быть контекст из документа
                context_data[char.name] = f"Персонаж {char.name} упоминается {char.count} раз"

            self.ai_analysis_results = self.ai_analyzer.analyze_characters(
                self.characters_data, context_data
            )

            self.status_var.set("ИИ анализ завершён")
            messagebox.showinfo("Успех", f"ИИ анализ выполнен для {len(self.ai_analysis_results)} персонажей")

            # Обновляем отображение с новыми данными
            self._update_tree_with_ai()
            
        except Exception as e:
            self.status_var.set("Ошибка ИИ анализа")
            messagebox.showerror("Ошибка", f"Ошибка ИИ анализа: {e}")

        self._update_button_states()

    def export_to_google_sheets(self):
        """Экспорт данных в Google Sheets."""
        if not self.characters_data:
            messagebox.showwarning("Внимание", "Сначала обработайте документ")
            return

        if not self.google_sheets.service:
            messagebox.showerror("Ошибка", "Необходима авторизация в Google Sheets")
            return

        self.status_var.set("Экспорт в Google Sheets...")
        self.update()

        try:
            success = self.google_sheets.export_characters(self.characters_data)
            if success:
                self.status_var.set("Экспорт в Google Sheets завершён")
                messagebox.showinfo("Успех", "Данные успешно экспортированы в Google Sheets!")

                # Добавляем ИИ анализ, если он есть и включена соответствующая опция
                if self.ai_analysis_results and self.export_ai_analysis_var.get():
                    analysis_data = [result.description for result in self.ai_analysis_results]
                    # Здесь нужно получить spreadsheet_id после создания
                    # self.google_sheets.add_analysis_column(spreadsheet_id, analysis_data)
                    
            else:
                self.status_var.set("Ошибка экспорта в Google Sheets")
                messagebox.showerror("Ошибка", "Не удалось экспортировать данные в Google Sheets")

        except Exception as e:
            self.status_var.set("Ошибка экспорта")
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")

        self._update_button_states()

    def _update_tree_with_ai(self):
        """Обновляет отображение таблицы с результатами ИИ анализа."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for char in self.characters_data:
            # Ищем результат ИИ анализа для этого персонажа
            ai_result = None
            for result in self.ai_analysis_results:
                if result.character_name == char.name:
                    ai_result = result
                    break

            if ai_result:
                self.tree.insert("", tk.END, values=(
                    char.name,
                    char.count,
                    ai_result.character_type,
                    ai_result.sentiment,
                    ai_result.emotion
                ))
            else:
                self.tree.insert("", tk.END, values=(
                    char.name,
                    char.count,
                    "-",
                    "-",
                    "-"
                ))

    def _update_button_states(self):
        """Обновляет состояние кнопок в зависимости от текущих настроек."""
        has_data = len(self.characters_data) > 0
        
        # Кнопка ИИ анализа
        if self.ai_button:
            self.ai_button.config(state=tk.NORMAL if (has_data and self.use_ai_var.get()) else tk.DISABLED)
        
        # Кнопка экспорта в Google Sheets
        if self.export_button:
            can_export_sheets = (has_data and self.use_google_sheets_var.get() and 
                               self.google_sheets.service is not None)
            self.export_button.config(state=tk.NORMAL if can_export_sheets else tk.DISABLED)

    def populate_tree(self, stats, minimum: int) -> None:
        # Сохраняем данные персонажей для последующего анализа
        self.characters_data = [stat for stat in stats if stat.count >= minimum]
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for stat in self.characters_data:
            self.tree.insert("", tk.END, values=(stat.name, stat.count, "-", "-", "-"))
        
        # Обновляем состояние кнопок
        self._update_button_states()

    def copy_results(self) -> None:
        items = [self.tree.item(child)["values"] for child in self.tree.get_children()]
        if not items:
            messagebox.showinfo("Список пуст", "Сначала обработайте документ")
            return
        
        # Формируем текст в зависимости от наличия ИИ анализа
        if self.ai_analysis_results:
            # С ИИ анализом
            lines = []
            for values in items:
                name, count, char_type, sentiment, emotion = values
                if char_type != "-" and sentiment != "-":
                    lines.append(f"{name} — {count} раз (тип: {char_type}, тональность: {sentiment}, эмоция: {emotion})")
                else:
                    lines.append(f"{name} — {count} раз")
            text = "\n".join(lines)
        else:
            # Без ИИ анализа
            text = "\n".join(f"{name} — {count}" for name, count, *_ in items)
        
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Готово", "Список скопирован в буфер обмена")


def run_app() -> None:
    app = CharacterApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
