from docx import Document
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox

# Функция для обработки документа
def process_document(input_path, output_path):
    # Открываем исходный документ
    input_doc = Document(input_path)
    
    # Список для хранения всех персонажей из второго столбца всех таблиц
    characters = []
    
    # Проходим по всем таблицам в документе
    for table_idx, table in enumerate(input_doc.tables):
        print(f"Обработка таблицы {table_idx + 1} с {len(table.rows)} строками")  # Отладка
        # Проходим по строкам таблицы и собираем персонажей
        for row_idx, row in enumerate(table.rows):
            try:
                # Проверяем, что второй столбец существует
                if len(row.cells) > 1:
                    character = row.cells[1].text.strip()  # Второй столбец (персонаж)
                    if character:  # Проверяем, что ячейка не пустая
                        characters.append(character)
                else:
                    print(f"Строка {row_idx + 1} в таблице {table_idx + 1} имеет менее 2 столбцов")
            except IndexError:
                print(f"Ошибка в таблице {table_idx + 1}, строке {row_idx + 1}: нет второго столбца")
    
    # Если персонажей не найдено
    if not characters:
        raise ValueError("Не удалось найти персонажей во втором столбце ни в одной таблице")
    
    # Подсчитываем количество упоминаний и сортируем
    character_counts = Counter(characters)
    sorted_counts = character_counts.most_common()
    
    # Создаём новый документ
    output_doc = Document()
    
    # Добавляем заголовок и список персонажей
    output_doc.add_heading("Количество упоминаний персонажей", level=1)
    for char, count in sorted_counts:
        output_doc.add_paragraph(f"{char} - {count}")
    
    # Добавляем разделитель и исходные таблицы
    output_doc.add_paragraph("\nИсходный текст всех таблиц:\n")
    
    # Копируем все таблицы из исходного документа
    for table_idx, table in enumerate(input_doc.tables):
        output_doc.add_paragraph(f"Таблица {table_idx + 1}:")
        new_table = output_doc.add_table(rows=len(table.rows), cols=len(table.columns))
        new_table.style = 'Table Grid'  # Стиль таблицы с границами
        
        # Заполняем новую таблицу данными из исходной
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                new_table.rows[i].cells[j].text = cell.text
    
    # Сохраняем новый документ
    output_doc.save(output_path)

# Функция для выбора файла и запуска обработки
def select_file_and_process():
    input_file = filedialog.askopenfilename(
        title="Выберите .docx файл",
        filetypes=[("Word файлы", "*.docx")]
    )
    
    if input_file:
        output_file = input_file.replace(".docx", "_result.docx")
        
        try:
            process_document(input_file, output_file)
            messagebox.showinfo("Успех", f"Файл обработан и сохранён как:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")

# Создаём окно приложения
root = tk.Tk()
root.title("Обработка Word-файлов")
root.geometry("300x150")

label = tk.Label(root, text="Выберите .docx файл для обработки", pady=10)
label.pack()

process_button = tk.Button(root, text="Выбрать файл и обработать", command=select_file_and_process, padx=10, pady=5)
process_button.pack(pady=20)

root.mainloop()