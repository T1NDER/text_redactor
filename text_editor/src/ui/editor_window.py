import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
import os
import re

class TextEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Editor")
        self.root.geometry("1000x700")
        
        # Инициализируем список вкладок ДО создания первой вкладки
        self.tabs = []
        self.current_file = None
        
        # Темы
        self.themes = {
            "Светлая": {
                "bg": "white",
                "fg": "black",
                "insert_bg": "black",
                "select_bg": "#c3d9ff",
                "toolbar_bg": "#f0f0f0",
                "status_bg": "#e0e0e0"
            },
            "Тёмная": {
                "bg": "#1e1e1e",
                "fg": "#d4d4d4",
                "insert_bg": "white",
                "select_bg": "#264f78",
                "toolbar_bg": "#2d2d2d",
                "status_bg": "#333333"
            }
        }
        self.current_theme = "Светлая"
        
        # Шрифты
        self.current_font_family = "Consolas"
        self.current_font_size = 12
        
        # Строка состояния (внизу)
        self.status_bar = ttk.Label(root, text="Готово")
        self.status_bar.pack(side="bottom", fill="x")
        
        # Панель инструментов (над строкой состояния)
        toolbar = ttk.Frame(root)
        toolbar.pack(side="bottom", fill="x")
        
        # Кнопки на панели инструментов
        ttk.Button(toolbar, text="Новая вкладка", command=self.create_new_tab).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Новый", command=self.new_file).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Открыть", command=self.open_file).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Сохранить", command=self.save_file).pack(side="left", padx=2, pady=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(toolbar, text="B", width=2, command=lambda: self.toggle_format("bold")).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="I", width=2, command=lambda: self.toggle_format("italic")).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="U", width=2, command=lambda: self.toggle_format("underline")).pack(side="left", padx=2, pady=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(toolbar, text="Отмена", command=self.undo_action).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Вырезать", command=self.cut_text).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Копировать", command=self.copy_text).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Вставить", command=self.paste_text).pack(side="left", padx=2, pady=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(toolbar, text="Найти", command=self.find_text).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Печать", command=self.print_document).pack(side="left", padx=2, pady=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(toolbar, text="Тема", command=self.toggle_theme).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="Шрифт", command=self.change_font).pack(side="left", padx=2, pady=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=5)
        ttk.Button(toolbar, text="Горячие клавиши", command=self.show_shortcuts).pack(side="left", padx=2, pady=2)
        
        # Вкладки (в центре)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Создаём первую вкладку
        self.create_new_tab()
        
        # Меню
        menubar = tk.Menu(root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новая вкладка", command=self.create_new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Печать...", command=self.print_document, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Закрыть вкладку", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Выход", command=root.quit, accelerator="Alt+F4")
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Отмена", command=self.undo_action, accelerator="Ctrl+Z")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Найти...", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_separator()
        format_menu = tk.Menu(edit_menu, tearoff=0)
        format_menu.add_command(label="Жирный", command=lambda: self.toggle_format("bold"), accelerator="Ctrl+B")
        format_menu.add_command(label="Курсив", command=lambda: self.toggle_format("italic"), accelerator="Ctrl+I")
        format_menu.add_command(label="Подчёркивание", command=lambda: self.toggle_format("underline"), accelerator="Ctrl+U")
        edit_menu.add_cascade(label="Форматирование", menu=format_menu)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_command(label="Светлая", command=lambda: self.set_theme("Светлая"))
        theme_menu.add_command(label="Тёмная", command=lambda: self.set_theme("Тёмная"))
        view_menu.add_cascade(label="Тема", menu=theme_menu)
        view_menu.add_command(label="Шрифт...", command=self.change_font)
        view_menu.add_command(label="Горячие клавиши", command=self.show_shortcuts, accelerator="Ctrl+H")
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Проверка орфографии", command=self.check_spelling, accelerator="F7")
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Горячие клавиши", command=self.show_shortcuts, accelerator="Ctrl+H")
        help_menu.add_command(label="О программе", command=self.about)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        root.config(menu=menubar)
        
        # Горячие клавиши
        root.bind("<Control-n>", lambda e: self.new_file())
        root.bind("<Control-o>", lambda e: self.open_file())
        root.bind("<Control-s>", lambda e: self.save_file())
        root.bind("<Control-Shift-S>", lambda e: self.save_as())
        root.bind("<Control-f>", lambda e: self.find_text())
        root.bind("<Control-z>", lambda e: self.undo_action())
        root.bind("<Control-x>", lambda e: self.cut_text())
        root.bind("<Control-c>", lambda e: self.copy_text())
        root.bind("<Control-v>", lambda e: self.paste_text())
        root.bind("<Control-t>", lambda e: self.create_new_tab())
        root.bind("<Control-w>", lambda e: self.close_current_tab())
        root.bind("<Control-h>", lambda e: self.show_shortcuts())
        root.bind("<F7>", lambda e: self.check_spelling())
        root.bind("<Control-b>", lambda e: self.toggle_format("bold"))
        root.bind("<Control-i>", lambda e: self.toggle_format("italic"))
        root.bind("<Control-u>", lambda e: self.toggle_format("underline"))
        root.bind("<Control-p>", lambda e: self.print_document())
        
        # Привязка событий для обновления статуса
        self.current_text_area.bind("<KeyRelease>", self.update_status_bar)
        self.current_text_area.bind("<ButtonRelease-1>", self.update_status_bar)
        
        self.update_status_bar()
        self.apply_theme()
        self.apply_font()
        
        # Привязка события переключения вкладок
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_new_tab(self, file_path=None):
        tab = ttk.Frame(self.notebook)
        
        if file_path:
            tab_name = os.path.basename(file_path)
        else:
            existing_names = [self.notebook.tab(t['frame'], 'text').rstrip('*') for t in self.tabs]
            new_number = 1
            while f"Новая вкладка {new_number}" in existing_names:
                new_number += 1
            tab_name = f"Новая вкладка {new_number}"
        
        self.notebook.add(tab, text=tab_name)
        
        # Создаём контейнер для текстового поля и прокрутки
        text_frame = tk.Frame(tab)
        text_frame.pack(fill="both", expand=True)
        
        # Текстовое поле с прокруткой
        text_area = tk.Text(text_frame, wrap="word", undo=True)
        text_area.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text_area.yview)
        
        tab_data = {
            'frame': tab,
            'text_area': text_area,
            'scrollbar': scrollbar,
            'file_path': file_path,
            'original_name': tab_name
        }
        
        self.tabs.append(tab_data)
        self.notebook.select(tab)
        self.current_text_area = text_area
        self.current_tab = tab_data
        
        self.apply_theme_to_text_area(text_area)
        self.apply_font_to_text_area(text_area)
        
        text_area.bind("<KeyRelease>", lambda e: self.update_status_bar())
        text_area.bind("<ButtonRelease-1>", lambda e: self.update_status_bar())
        
        if file_path:
            self.load_file_to_tab(file_path, tab_data)
        
        return tab_data

    def close_current_tab(self):
        if len(self.tabs) <= 1:
            return
            
        current_index = self.notebook.index(self.notebook.select())
        tab_data = self.tabs[current_index]
        
        if tab_data['file_path'] is None and tab_data['text_area'].get("1.0", "end-1c").strip():
            response = messagebox.askyesnocancel(
                "Сохранить изменения?",
                "Документ содержит несохранённые изменения. Сохранить перед закрытием?"
            )
            if response is True:
                self.save_file()
            elif response is None:
                return
        
        self.notebook.forget(tab_data['frame'])
        self.tabs.pop(current_index)
        
        if current_index >= len(self.tabs):
            current_index = len(self.tabs) - 1
        if self.tabs:
            self.notebook.select(self.tabs[current_index]['frame'])
            self.on_tab_change()

    def show_shortcuts(self):
        for tab in self.tabs:
            if hasattr(tab, 'is_shortcuts_tab'):
                self.notebook.select(tab['frame'])
                return
        
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Горячие клавиши")
        
        scroll_frame = tk.Frame(tab)
        scroll_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        title_label = tk.Label(scrollable_frame, text="Горячие клавиши", font=("Arial", 16, "bold"), pady=10)
        title_label.pack(fill="x", padx=10, pady=5)
        
        shortcuts = [
            ("Ctrl + N", "Создать новый файл"),
            ("Ctrl + O", "Открыть файл"),
            ("Ctrl + S", "Сохранить файл"),
            ("Ctrl + Shift + S", "Сохранить как..."),
            ("Ctrl + P", "Печать документа"),
            ("Ctrl + W", "Закрыть текущую вкладку"),
            ("Ctrl + T", "Создать новую вкладку"),
            ("Alt + F4", "Выход из программы"),
            ("", ""),
            ("Ctrl + Z", "Отмена последнего действия"),
            ("Ctrl + X", "Вырезать выделенный текст"),
            ("Ctrl + C", "Копировать выделенный текст"),
            ("Ctrl + V", "Вставить текст из буфера"),
            ("Ctrl + F", "Найти текст в документе"),
            ("F7", "Проверка орфографии"),
            ("", ""),
            ("Ctrl + B", "Сделать текст жирным"),
            ("Ctrl + I", "Сделать текст курсивом"),
            ("Ctrl + U", "Подчеркнуть текст"),
            ("", ""),
            ("Ctrl + H", "Открыть эту вкладку с горячими клавишами"),
            ("Ctrl + Tab", "Переключение между вкладками"),
            ("Ctrl + PageUp/PageDown", "Переключение между вкладками")
        ]
        
        for combo, description in shortcuts:
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill="x", padx=20, pady=2)
            
            if combo:
                combo_label = tk.Label(frame, text=combo, font=("Consolas", 10, "bold"), width=20, anchor="w")
                combo_label.pack(side="left")
                
                desc_label = tk.Label(frame, text=description, font=("Arial", 10))
                desc_label.pack(side="left", padx=10)
            else:
                separator = ttk.Separator(frame, orient="horizontal")
                separator.pack(fill="x", pady=5)
        
        info_label = tk.Label(scrollable_frame, 
                             text="Подсказка: Нажмите на комбинацию клавиш в таблице, чтобы скопировать её в буфер обмена",
                             font=("Arial", 9, "italic"),
                             fg="gray",
                             pady=10)
        info_label.pack(fill="x", padx=20, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tab_data = {
            'frame': tab,
            'is_shortcuts_tab': True,
            'text_area': None,
            'scrollbar': scrollbar,
            'file_path': None,
            'original_name': "Горячие клавиши"
        }
        
        self.tabs.append(tab_data)
        self.notebook.select(tab)

    def about(self):
        messagebox.showinfo("О программе", 
                           "Простой текстовый редактор\n"
                           "Версия 1.0\n"
                           "Python + Tkinter\n"
                           "Автор: Текстовый редактор")

    def apply_theme_to_text_area(self, text_area):
        if text_area is None:
            return
            
        theme = self.themes[self.current_theme]
        text_area.config(
            bg=theme["bg"],
            fg=theme["fg"],
            insertbackground=theme["insert_bg"],
            selectbackground=theme["select_bg"]
        )

    def apply_font_to_text_area(self, text_area):
        if text_area is None:
            return
            
        text_font = font.Font(family=self.current_font_family, size=self.current_font_size)
        text_area.config(font=text_font)

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        for tab in self.tabs:
            if 'text_area' in tab and tab['text_area'] is not None:
                self.apply_theme_to_text_area(tab['text_area'])
        self.status_bar.config(background=theme["status_bg"], foreground=theme["fg"])

    def apply_font(self):
        for tab in self.tabs:
            if 'text_area' in tab and tab['text_area'] is not None:
                self.apply_font_to_text_area(tab['text_area'])

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.apply_theme()

    def toggle_theme(self):
        if self.current_theme == "Светлая":
            self.set_theme("Тёмная")
        else:
            self.set_theme("Светлая")

    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Выбор шрифта")
        font_window.geometry("300x200")
        font_window.transient(self.root)
        font_window.grab_set()
        
        available_fonts = list(font.families())
        available_fonts.sort()
        
        current_family = tk.StringVar(value=self.current_font_family)
        current_size = tk.IntVar(value=self.current_font_size)
        
        tk.Label(font_window, text="Семейство шрифта:").pack(pady=5)
        font_combo = ttk.Combobox(font_window, textvariable=current_family, values=available_fonts, state="readonly")
        font_combo.pack(pady=5, padx=10, fill="x")
        font_combo.set(self.current_font_family)
        
        tk.Label(font_window, text="Размер шрифта:").pack(pady=5)
        size_spinbox = tk.Spinbox(font_window, from_=8, to=72, textvariable=current_size, width=10)
        size_spinbox.pack(pady=5)
        
        def apply_font_changes():
            self.current_font_family = current_family.get()
            self.current_font_size = current_size.get()
            self.apply_font()
            font_window.destroy()
        
        ttk.Button(font_window, text="Применить", command=apply_font_changes).pack(pady=10)

    def load_file_to_tab(self, file_path, tab_data):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tab_data['text_area'].delete("1.0", "end")
            tab_data['text_area'].insert("1.0", content)
            tab_data['file_path'] = file_path
            self.update_status_bar()
            self.status_bar.config(text=f"Открыт файл: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def on_tab_change(self, event=None):
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index < len(self.tabs):
            self.current_tab = self.tabs[tab_index]
            self.current_text_area = self.current_tab['text_area'] if self.current_tab['text_area'] else None
            self.current_file = self.current_tab['file_path']
            self.update_status_bar()

    def new_file(self):
        if self.current_text_area is None:
            return
            
        self.current_text_area.delete("1.0", "end")
        self.current_tab['file_path'] = None
        self.notebook.tab(self.current_tab['frame'], text=self.current_tab['original_name'])
        self.update_status_bar()
        self.status_bar.config(text="Создан новый файл")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            for tab in self.tabs:
                if tab.get('file_path') == file_path:
                    self.notebook.select(tab['frame'])
                    return
            self.create_new_tab(file_path)

    def save_file(self):
        if self.current_text_area is None:
            return
            
        if self.current_tab['file_path']:
            try:
                content = self.current_text_area.get("1.0", "end-1c")
                with open(self.current_tab['file_path'], "w", encoding="utf-8") as f:
                    f.write(content)
                clean_name = os.path.basename(self.current_tab['file_path'])
                self.notebook.tab(self.current_tab['frame'], text=clean_name)
                self.status_bar.config(text=f"Сохранено: {self.current_tab['file_path']}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
        else:
            self.save_as()

    def save_as(self):
        if self.current_text_area is None:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.current_tab['file_path'] = file_path
            self.save_file()

    def undo_action(self):
        if self.current_text_area is None:
            return
            
        try:
            self.current_text_area.edit_undo()
            self.update_status_bar()
        except tk.TclError:
            pass

    def cut_text(self):
        if self.current_text_area is None:
            return
            
        self.current_text_area.event_generate("<<Cut>>")
        self.update_status_bar()

    def copy_text(self):
        if self.current_text_area is None:
            return
            
        self.current_text_area.event_generate("<<Copy>>")

    def paste_text(self):
        if self.current_text_area is None:
            return
            
        self.current_text_area.event_generate("<<Paste>>")
        self.update_status_bar()

    def find_text(self):
        if self.current_text_area is None:
            return
            
        search_window = tk.Toplevel(self.root)
        search_window.title("Найти текст")
        search_window.geometry("300x100")
        search_window.transient(self.root)
        search_window.grab_set()
        
        tk.Label(search_window, text="Текст для поиска:").pack(pady=5)
        search_entry = ttk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        def do_search():
            search_text = search_entry.get()
            if not search_text:
                return
                
            self.current_text_area.tag_remove("highlight", "1.0", "end")
            start_pos = "1.0"
            found = False
            
            while True:
                start_pos = self.current_text_area.search(search_text, start_pos, nocase=True, stopindex="end")
                if not start_pos:
                    break
                    
                found = True
                end_pos = f"{start_pos}+{len(search_text)}c"
                self.current_text_area.tag_add("highlight", start_pos, end_pos)
                self.current_text_area.tag_config("highlight", background="yellow", foreground="black")
                start_pos = end_pos
            
            if found:
                self.current_text_area.see("highlight.first")
                search_window.destroy()
            else:
                messagebox.showinfo("Поиск", "Текст не найден")
        
        ttk.Button(search_window, text="Найти", command=do_search).pack(pady=5)
        search_window.bind("<Return>", lambda e: do_search())

    def toggle_format(self, format_type):
        if self.current_text_area is None:
            return
            
        try:
            current_tags = self.current_text_area.tag_names("sel.first")
        except tk.TclError:
            return
        
        tag_name = format_type
        if tag_name not in self.current_text_area.tag_names():
            base_font = font.Font(family=self.current_font_family, size=self.current_font_size)
            if format_type == "bold":
                bold_font = font.Font(family=self.current_font_family, size=self.current_font_size, weight="bold")
                self.current_text_area.tag_configure(tag_name, font=bold_font)
            elif format_type == "italic":
                italic_font = font.Font(family=self.current_font_family, size=self.current_font_size, slant="italic")
                self.current_text_area.tag_configure(tag_name, font=italic_font)
            elif format_type == "underline":
                underline_font = font.Font(family=self.current_font_family, size=self.current_font_size, underline=True)
                self.current_text_area.tag_configure(tag_name, font=underline_font)
        
        has_tag = False
        for tag in current_tags:
            if tag == tag_name:
                has_tag = True
                break
        
        if has_tag:
            self.current_text_area.tag_remove(tag_name, "sel.first", "sel.last")
        else:
            self.current_text_area.tag_add(tag_name, "sel.first", "sel.last")

    def print_document(self):
        if self.current_text_area is None:
            return
            
        content = self.current_text_area.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showwarning("Печать", "Документ пуст")
            return
        
        messagebox.showinfo("Печать", 
                           f"Документ готов к печати:\n\n"
                           f"Название: {self.current_tab['file_path'] or 'Новый документ'}\n"
                           f"Количество строк: {content.count(chr(10)) + 1}\n"
                           f"Количество символов: {len(content)}\n\n"
                           f"В реальном приложении здесь была бы отправка на принтер.")

    def check_spelling(self):
        if self.current_text_area is None:
            return
            
        content = self.current_text_area.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showinfo("Проверка орфографии", "Документ пуст")
            return
        
        words = re.findall(r'[а-яА-ЯёЁa-zA-Z]+', content)
        
        dictionary = {
            "привет", "мир", "текст", "редактор", "файл", "сохранить", "открыть", "новый", "самолёт", "слово",
            "проверка", "орфография", "форматирование", "печать", "найти", "вставить", "вырезать", "копировать",
            "отмена", "вкладка", "документ", "строка", "символ", "слово", "текстовый", "редактор", "работа", "код",
            "функция", "метод", "класс", "переменная", "цикл", "условие", "если", "то", "иначе", "для", "пока", "вернуть"
        }
        
        misspelled = []
        for word in words:
            clean_word = word.lower()
            if clean_word and clean_word not in dictionary:
                misspelled.append(word)
        
        if misspelled:
            result = f"Возможные ошибки ({len(misspelled)}):\n\n" + "\n".join(misspelled[:10])
            if len(misspelled) > 10:
                result += f"\n\nи ещё {len(misspelled) - 10} слов..."
            messagebox.showinfo("Проверка орфографии", result)
        else:
            messagebox.showinfo("Проверка орфографии", "Ошибок не найдено")

    def update_status_bar(self, event=None):
        if self.current_text_area is None:
            self.status_bar.config(text="Готово")
            return
            
        content = self.current_text_area.get("1.0", "end-1c")
        
        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        lines = content.count("\n") + 1 if content else 1
        
        if self.current_tab['file_path']:
            file_name = os.path.basename(self.current_tab['file_path'])
        else:
            file_name = self.current_tab['original_name']
        
        status_text = f"Файл: {file_name} | Строк: {lines} | Слов: {words} | Символов: {chars}"
        self.status_bar.config(text=status_text)