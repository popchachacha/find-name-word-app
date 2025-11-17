"""Tkinter application for processing Word documents."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .processor import DocumentProcessor


def _resource_path(path: str | Path | None) -> str:
    return str(Path(path).expanduser()) if path else ""


class CharacterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Обработка Word-файлов")
        self.geometry("820x520")
        self.resizable(False, False)

        self.processor = DocumentProcessor()
        self.file_path: Path | None = None
        self.output_dir: Path | None = None

        self.min_mentions = tk.IntVar(value=1)
        self.column_var = tk.IntVar(value=2)
        self.ignore_case_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Загрузите документ для начала")

        self._configure_style()
        self._build_layout()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f7f7fb")
        style.configure("TLabel", background="#f7f7fb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Secondary.TButton", padding=6)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            container,
            text="Автоматическая обработка таблиц Word",
            style="Title.TLabel",
        )
        header.pack(anchor=tk.W)

        description = ttk.Label(
            container,
            text="Выделяйте персонажей из второго столбца, создавайте отчеты и сохраняйте их",
            wraplength=760,
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

        ttk.Checkbutton(
            options_frame,
            text="Игнорировать регистр имён",
            variable=self.ignore_case_var,
        ).grid(row=1, column=0, columnspan=3, pady=(8, 0), sticky=tk.W)

        table_frame = ttk.Frame(container)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("character", "count")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        self.tree.heading("character", text="Персонаж")
        self.tree.heading("count", text="Количество")
        self.tree.column("character", width=420)
        self.tree.column("count", width=120, anchor=tk.CENTER)
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

    def populate_tree(self, stats, minimum: int) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for stat in stats:
            if stat.count < minimum:
                continue
            self.tree.insert("", tk.END, values=(stat.name, stat.count))

    def copy_results(self) -> None:
        items = [self.tree.item(child)["values"] for child in self.tree.get_children()]
        if not items:
            messagebox.showinfo("Список пуст", "Сначала обработайте документ")
            return
        text = "\n".join(f"{name} — {count}" for name, count in items)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Готово", "Список скопирован в буфер обмена")


def run_app() -> None:
    app = CharacterApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
