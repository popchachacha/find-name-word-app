"""
Modern, animated GUI for Word document character analysis.
Features smooth animations, modern styling, and enhanced user experience.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional
import math
import time
import threading

from .core_processor import DocumentProcessor, CharacterStat


class AnimatedButton(tk.Frame):
    """Custom animated button with hover effects and smooth transitions."""
    
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.text = text
        self.command = command
        self.style = style
        self.is_hovering = False
        self.is_pressed = False
        self.animation_progress = 0.0
        self.target_progress = 0.0
        
        # Button appearance based on style
        self.colors = {
            "primary": {"normal": "#007bff", "hover": "#0056b3", "text": "white"},
            "secondary": {"normal": "#6c757d", "hover": "#545b62", "text": "white"},
            "success": {"normal": "#28a745", "hover": "#1e7e34", "text": "white"},
            "danger": {"normal": "#dc3545", "hover": "#bd2130", "text": "white"}
        }
        
        self.setup_ui()
        self.start_animation()
    
    def setup_ui(self):
        """Setup the button UI components."""
        self.configure(bg="#f8f9fa")
        
        # Main button canvas
        self.canvas = tk.Canvas(
            self, 
            height=40, 
            width=120, 
            highlightthickness=0,
            bg="#f8f9fa"
        )
        self.canvas.pack()
        
        # Button text
        self.text_label = tk.Label(
            self.canvas,
            text=self.text,
            font=("Segoe UI", 10, "bold"),
            bg="#f8f9fa",
            fg=self.colors[self.style]["normal"]
        )
        self.text_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        
        self.canvas.bind("<Button-1>", lambda e: self.event_generate("<<ButtonClicked>>"))
    
    def on_press(self, event):
        """Handle button press animation."""
        self.is_pressed = True
        self.target_progress = 1.0
        if self.command:
            self.command()
    
    def on_release(self, event):
        """Handle button release animation."""
        self.is_pressed = False
    
    def on_enter(self, event):
        """Handle mouse enter animation."""
        self.is_hovering = True
        self.target_progress = 0.7
    
    def on_leave(self, event):
        """Handle mouse leave animation."""
        self.is_hovering = False
        self.is_pressed = False
        self.target_progress = 0.0
    
    def start_animation(self):
        """Start the button animation loop."""
        def animate():
            while True:
                if self.winfo_exists():
                    # Smooth animation using easing
                    easing = 0.1
                    self.animation_progress += (self.target_progress - self.animation_progress) * easing
                    
                    # Update button appearance
                    self.update_button_appearance()
                    
                    time.sleep(0.016)  # ~60 FPS
                else:
                    break
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    def update_button_appearance(self):
        """Update button appearance based on animation progress."""
        if not hasattr(self, 'canvas'):
            return
            
        normal_color = self.colors[self.style]["normal"]
        hover_color = self.colors[self.style]["hover"]
        text_color = self.colors[self.style]["text"]
        
        # Interpolate colors
        if self.animation_progress > 0.5:
            current_color = hover_color
            scale = 0.95 - (self.animation_progress - 0.5) * 0.1
        else:
            current_color = normal_color
            scale = 1.0
        
        # Update canvas
        width = int(120 * scale)
        height = int(40 * scale)
        
        self.canvas.config(width=width, height=height)
        
        # Redraw button
        self.canvas.delete("all")
        x1, y1 = 2, 2
        x2, y2 = width-2, height-2
        
        self.canvas.create_rounded_rectangle(
            x1, y1, x2, y2, 
            radius=8,
            fill=current_color,
            outline="",
            width=0
        )
        
        # Update text
        self.text_label.config(fg=text_color)
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Create rounded rectangle on canvas."""
        points = []
        for i in range(4):
            if i == 0:  # Top-left
                points.extend([x1 + radius, y1])
            elif i == 1:  # Top-right
                points.extend([x2 - radius, y1])
            elif i == 2:  # Bottom-right
                points.extend([x2, y1 + radius])
            elif i == 3:  # Bottom-left
                points.extend([x2 - radius, y2])
        
        # Create arcs
        return self.canvas.create_polygon(points, smooth=True, **kwargs)


class AnimatedProgressBar(tk.Frame):
    """Animated progress bar with smooth filling animation."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.progress = 0.0
        self.target_progress = 0.0
        self.is_animating = False
        
        self.setup_ui()
        self.start_animation()
    
    def setup_ui(self):
        """Setup progress bar UI."""
        self.configure(bg="#f8f9fa")
        
        self.canvas = tk.Canvas(
            self,
            height=20,
            width=300,
            highlightthickness=1,
            highlightbackground="#dee2e6",
            bg="white"
        )
        self.canvas.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=("Segoe UI", 9),
            bg="#f8f9fa",
            fg="#6c757d"
        )
        self.status_label.pack()
    
    def set_progress(self, progress, status_text=""):
        """Set progress with animation."""
        self.target_progress = max(0.0, min(1.0, progress))
        if status_text:
            self.status_label.config(text=status_text)
    
    def start_animation(self):
        """Start progress bar animation."""
        def animate():
            while self.winfo_exists():
                if abs(self.progress - self.target_progress) > 0.01:
                    self.progress += (self.target_progress - self.progress) * 0.1
                    self.update_display()
                
                time.sleep(0.016)
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    def update_display(self):
        """Update progress bar display."""
        if not hasattr(self, 'canvas'):
            return
            
        self.canvas.delete("all")
        
        # Background
        self.canvas.create_rectangle(
            2, 2, 298, 18,
            fill="white",
            outline="#dee2e6",
            width=1
        )
        
        # Progress fill
        if self.progress > 0:
            width = int(294 * self.progress)
            # Animated gradient effect
            color_start = "#007bff"
            color_end = "#0056b3"
            
            self.canvas.create_rectangle(
                3, 3, 3 + width, 17,
                fill=color_start,
                outline=""
            )


class ModernCharacterAnalysisGUI(tk.Tk):
    """Modern, animated GUI for character analysis."""
    
    def __init__(self):
        super().__init__()
        self.title("Word Character Analyzer Pro")
        self.geometry("1000x700")
        self.configure(bg="#f8f9fa")
        
        # Core components
        self.processor = DocumentProcessor()
        self.file_path: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        
        # UI variables
        self.min_mentions = tk.IntVar(value=1)
        self.column_var = tk.IntVar(value=2)
        self.ignore_case_var = tk.BooleanVar(value=True)
        self.status_text = tk.StringVar(value="Ready to analyze documents")
        
        # Results data
        self.characters_data: List[CharacterStat] = []
        self.animation_phase = 0
        
        self.setup_style()
        self.build_layout()
        self.start_background_animations()
    
    def setup_style(self):
        """Configure modern styling."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Custom styles
        style.configure("Modern.TFrame", background="#f8f9fa")
        style.configure("Modern.TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#f8f9fa", font=("Segoe UI", 18, "bold"), foreground="#343a40")
        style.configure("Subtitle.TLabel", background="#f8f9fa", font=("Segoe UI", 12), foreground="#6c757d")
        style.configure("Success.TLabel", background="#d4edda", font=("Segoe UI", 9), foreground="#155724")
        style.configure("Animated.Treeview", background="white", fieldbackground="white", foreground="#343a40")
        style.configure("Animated.Treeview.Heading", background="#007bff", foreground="white", font=("Segoe UI", 10, "bold"))
    
    def build_layout(self):
        """Build the main application layout."""
        # Main container
        main_container = tk.Frame(self, bg="#f8f9fa")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with animation
        self.build_header(main_container)
        
        # Content area with cards
        content_frame = tk.Frame(main_container, bg="#f8f9fa")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Left panel - Controls
        self.build_controls_panel(content_frame)
        
        # Right panel - Results
        self.build_results_panel(content_frame)
        
        # Bottom status bar
        self.build_status_bar(main_container)
    
    def build_header(self, parent):
        """Build animated header section."""
        header_frame = tk.Frame(parent, bg="#f8f9fa")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Main title
        title_label = tk.Label(
            header_frame,
            text="✨ Word Character Analyzer Pro",
            font=("Segoe UI", 24, "bold"),
            bg="#f8f9fa",
            fg="#343a40"
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Advanced document analysis with modern AI-powered insights",
            font=("Segoe UI", 12),
            bg="#f8f9fa",
            fg="#6c757d"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Animated decoration
        self.decoration_canvas = tk.Canvas(
            header_frame,
            height=30,
            width=400,
            bg="#f8f9fa",
            highlightthickness=0
        )
        self.decoration_canvas.pack(pady=(10, 0))
    
    def build_controls_panel(self, parent):
        """Build controls panel with modern card design."""
        # Card container
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)
        
        # Card header
        card_header = tk.Frame(card_frame, bg="#007bff", height=50)
        card_header.pack(fill=tk.X)
        card_header.pack_propagate(False)
        
        tk.Label(
            card_header,
            text="⚙️ Settings & Controls",
            font=("Segoe UI", 12, "bold"),
            bg="#007bff",
            fg="white"
        ).pack(pady=15)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Document selection
        self.build_document_section(content_frame)
        
        # Analysis settings
        self.build_settings_section(content_frame)
        
        # Action buttons
        self.build_action_buttons(content_frame)
    
    def build_document_section(self, parent):
        """Build document selection section."""
        section_frame = tk.Frame(parent, bg="white")
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            section_frame,
            text="📄 Document Selection",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#343a40"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # File selection button
        self.select_file_btn = AnimatedButton(
            section_frame,
            "Select Document",
            self.select_file,
            style="primary"
        )
        self.select_file_btn.pack(fill=tk.X, pady=(0, 10))
        
        # File info
        self.file_info_label = tk.Label(
            section_frame,
            text="No document selected",
            font=("Segoe UI", 9),
            bg="white",
            fg="#6c757d",
            wraplength=250
        )
        self.file_info_label.pack(anchor=tk.W)
        
        # Progress bar
        self.progress_bar = AnimatedProgressBar(section_frame)
        self.progress_bar.pack(fill=tk.X, pady=(15, 0))
    
    def build_settings_section(self, parent):
        """Build analysis settings section."""
        section_frame = tk.Frame(parent, bg="white")
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            section_frame,
            text="⚙️ Analysis Settings",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#343a40"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Settings grid
        settings_grid = tk.Frame(section_frame, bg="white")
        settings_grid.pack(fill=tk.X)
        
        # Minimum mentions
        tk.Label(
            settings_grid,
            text="Min mentions:",
            font=("Segoe UI", 9),
            bg="white"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.min_spinbox = ttk.Spinbox(
            settings_grid,
            from_=1, to=99, width=8,
            textvariable=self.min_mentions
        )
        self.min_spinbox.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        # Column index
        tk.Label(
            settings_grid,
            text="Column (1-based):",
            font=("Segoe UI", 9),
            bg="white"
        ).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.column_spinbox = ttk.Spinbox(
            settings_grid,
            from_=1, to=20, width=8,
            textvariable=self.column_var
        )
        self.column_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Case insensitive checkbox
        self.case_checkbox = tk.Checkbutton(
            settings_grid,
            text="Ignore case",
            variable=self.ignore_case_var,
            font=("Segoe UI", 9),
            bg="white",
            fg="#343a40",
            selectcolor="white"
        )
        self.case_checkbox.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def build_action_buttons(self, parent):
        """Build action buttons section."""
        buttons_frame = tk.Frame(parent, bg="white")
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Analyze button
        self.analyze_btn = AnimatedButton(
            buttons_frame,
            "🚀 Analyze",
            self.analyze_document,
            style="primary"
        )
        self.analyze_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Copy results button
        self.copy_btn = AnimatedButton(
            buttons_frame,
            "📋 Copy Results",
            self.copy_results,
            style="secondary"
        )
        self.copy_btn.pack(fill=tk.X)
    
    def build_results_panel(self, parent):
        """Build results panel with modern table design."""
        # Card container
        card_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=1)
        card_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=0)
        
        # Card header
        card_header = tk.Frame(card_frame, bg="#28a745", height=50)
        card_header.pack(fill=tk.X)
        card_header.pack_propagate(False)
        
        tk.Label(
            card_header,
            text="📊 Analysis Results",
            font=("Segoe UI", 12, "bold"),
            bg="#28a745",
            fg="white"
        ).pack(pady=15)
        
        # Results table
        self.build_results_table(card_frame)
    
    def build_results_table(self, parent):
        """Build modern results table."""
        # Table container
        table_container = tk.Frame(parent, bg="white")
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Treeview with custom styling
        columns = ("character", "count")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Animated.Treeview",
            height=20
        )
        
        # Column headers and styling
        self.tree.heading("character", text="Character Name", command=lambda: self.sort_by_column("character", False))
        self.tree.heading("count", text="Mentions", command=lambda: self.sort_by_column("count", False))
        
        self.tree.column("character", width=400)
        self.tree.column("count", width=120, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Configure treeview colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="white")
        self.tree.tag_configure("highlight", background="#e3f2fd")
    
    def build_status_bar(self, parent):
        """Build animated status bar."""
        status_frame = tk.Frame(parent, bg="#343a40", height=40)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("Segoe UI", 10),
            bg="#343a40",
            fg="white"
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Status icon (animated)
        self.status_icon_label = tk.Label(
            status_frame,
            text="●",
            font=("Segoe UI", 10),
            bg="#343a40",
            fg="#28a745"
        )
        self.status_icon_label.pack(side=tk.RIGHT, padx=15, pady=10)
    
    def start_background_animations(self):
        """Start background animations."""
        def animate_decoration():
            while self.winfo_exists():
                self.animation_phase += 0.05
                
                # Animate header decoration
                if hasattr(self, 'decoration_canvas'):
                    self.animate_decoration()
                
                # Animate status icon
                if hasattr(self, 'status_icon_label'):
                    self.animate_status_icon()
                
                time.sleep(0.1)
        
        animation_thread = threading.Thread(target=animate_decoration, daemon=True)
        animation_thread.start()
    
    def animate_decoration(self):
        """Animate header decoration elements."""
        self.decoration_canvas.delete("all")
        
        # Animated waves
        width = self.decoration_canvas.winfo_width()
        height = self.decoration_canvas.winfo_height()
        
        if width > 1:
            # Wave 1
            points = []
            for x in range(0, width, 5):
                y = height // 2 + math.sin(self.animation_phase + x * 0.01) * 5
                points.extend([x, y])
            
            if len(points) >= 4:
                self.decoration_canvas.create_line(
                    points, 
                    fill="#007bff", 
                    width=2
                )
            
            # Wave 2 (offset)
            points = []
            for x in range(0, width, 5):
                y = height // 2 + math.sin(self.animation_phase + x * 0.01 + math.pi) * 3
                points.extend([x, y])
            
            if len(points) >= 4:
                self.decoration_canvas.create_line(
                    points, 
                    fill="#28a745", 
                    width=1
                )
    
    def animate_status_icon(self):
        """Animate status icon."""
        # Pulsing animation
        pulse = 1 + math.sin(self.animation_phase * 2) * 0.2
        size = int(12 * pulse)
        self.status_icon_label.config(font=("Segoe UI", size))
    
    def sort_by_column(self, col, reverse):
        """Sort treeview by column."""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        
        # Convert to appropriate data type
        if col == "count":
            items = [(int(item[0]), item[1]) for item in items if item[0].isdigit()]
        else:
            items = [(item[0].lower(), item[1]) for item in items]
        
        items.sort(reverse=reverse)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, "", index)
    
    def select_file(self):
        """Enhanced file selection with animation."""
        file_path = filedialog.askopenfilename(
            title="Select Word Document",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ],
        )
        
        if file_path:
            self.file_path = Path(file_path)
            self.file_info_label.config(
                text=f"📄 {self.file_path.name}\n📁 {self.file_path.parent.name}",
                fg="#28a745"
            )
            self.progress_bar.set_progress(0, "Document ready for analysis")
            self.status_text.set("Document selected. Ready to analyze!")
    
    def analyze_document(self):
        """Enhanced document analysis with animations."""
        if not self.file_path:
            messagebox.showwarning("No Document", "Please select a Word document first.")
            return
        
        # Animate progress
        self.progress_bar.set_progress(0, "Starting analysis...")
        
        def analyze_with_animation():
            try:
                # Get settings
                minimum = max(1, self.min_mentions.get())
                column_index = max(1, self.column_var.get()) - 1
                ignore_case = self.ignore_case_var.get()
                
                # Simulate loading steps
                steps = [
                    (0.2, "Reading document..."),
                    (0.4, "Extracting table data..."),
                    (0.6, "Processing characters..."),
                    (0.8, "Calculating frequencies..."),
                    (1.0, "Generating report...")
                ]
                
                for progress, status in steps:
                    self.progress_bar.set_progress(progress, status)
                    time.sleep(0.5)  # Simulate processing time
                
                # Actual processing
                result = self.processor.process(self.file_path, column_index=column_index)
                stats = self.processor.summarise(result.characters, ignore_case=ignore_case)
                filtered_stats = [stat for stat in stats if stat.count >= minimum]
                
                self.characters_data = filtered_stats
                
                # Update display with animation
                self.display_results_with_animation()
                
                # Generate output file
                output_dir = self.output_dir or self.file_path.parent
                output_name = f"{self.file_path.stem}_analysis.docx"
                output_path = output_dir / output_name
                
                self.processor.export_report(
                    result,
                    output_path,
                    minimum_mentions=minimum,
                    ignore_case=ignore_case,
                )
                
                # Final status
                self.progress_bar.set_progress(1.0, f"Analysis complete! {len(filtered_stats)} characters found.")
                self.status_text.set(f"✅ Analysis complete! Found {len(filtered_stats)} characters.")
                
                messagebox.showinfo(
                    "Analysis Complete",
                    f"🎉 Document analyzed successfully!\n\n"
                    f"📊 Characters found: {len(stats)}\n"
                    f"🎯 Characters with {minimum}+ mentions: {len(filtered_stats)}\n"
                    f"📄 Report saved: {output_path.name}"
                )
                
            except Exception as exc:
                self.progress_bar.set_progress(0, "Analysis failed")
                self.status_text.set("❌ Analysis failed")
                error_msg = f"Analysis failed: {str(exc)}"
                messagebox.showerror("Analysis Error", error_msg)
        
        # Run analysis in background thread
        analysis_thread = threading.Thread(target=analyze_with_animation, daemon=True)
        analysis_thread.start()
    
    def display_results_with_animation(self):
        """Display results with smooth animation."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items with animation
        def add_items_animated():
            for i, stat in enumerate(self.characters_data):
                self.tree.insert("", tk.END, values=(stat.name, stat.count))
                self.tree.tag_configure("highlight", background="#e3f2fd")
                
                # Highlight the newly added item briefly
                item_id = self.tree.get_children()[-1]
                self.tree.item(item_id, tags=("highlight",))
                
                time.sleep(0.1)  # Stagger the appearance
                
                # Remove highlight
                self.tree.item(item_id, tags=())
        
        animation_thread = threading.Thread(target=add_items_animated, daemon=True)
        animation_thread.start()
    
    def copy_results(self):
        """Enhanced copy results with feedback."""
        if not self.characters_data:
            messagebox.showinfo("No Results", "No analysis results to copy.")
            return
        
        # Format results for clipboard
        lines = ["📋 Character Analysis Results:", ""]
        for stat in self.characters_data:
            lines.append(f"{stat.name} — {stat.count} mentions")
        
        result_text = "\n".join(lines)
        
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(result_text)
        
        # Animated feedback
        original_status = self.status_text.get()
        self.status_text.set("📋 Results copied to clipboard!")
        
        self.after(2000, lambda: self.status_text.set(original_status))
        
        messagebox.showinfo("Copied", f"✅ Copied {len(lines)-2} characters to clipboard!")


def run_enhanced_app():
    """Launch the enhanced application."""
    app = ModernCharacterAnalysisGUI()
    app.mainloop()


if __name__ == "__main__":
    run_enhanced_app()