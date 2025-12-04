"""
Clean and simple GUI for Word document character analysis.
Focuses on core functionality without heavy dependencies.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from .core_processor import DocumentProcessor, CharacterStat


class CharacterAnalysisGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Word Character Analyzer")
        self.geometry("800x600")
        self.resizable(True, True)

        # Core components
        self.processor = DocumentProcessor()
        self.file_path: Optional[Path] = None
        self.output_dir: Optional[Path] = None

        # UI Variables
        self.min_mentions = tk.IntVar(value=1)
        self.column_var = tk.IntVar(value=2)
        self.ignore_case_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Select a document to begin")

        # Results data
        self.characters_data: List[CharacterStat] = []

        self._configure_style()
        self._build_layout()

    def _configure_style(self) -> None:
        """Configure the visual style of the application."""
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Color scheme
        style.configure("TFrame", background="#f8f9fa")
        style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        style.configure("Secondary.TButton", padding=6)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Success.TLabel", background="#d4edda", font=("Segoe UI", 9))
        style.configure("Error.TLabel", background="#f8d7da", font=("Segoe UI", 9))

    def _build_layout(self) -> None:
        """Build the main application layout."""
        # Main container
        container = ttk.Frame(self, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(
            container,
            text="Word Character Analyzer",
            style="Title.TLabel",
        )
        header.pack(anchor=tk.W, pady=(0, 5))

        description = ttk.Label(
            container,
            text="Extract and analyze character names from Word document tables",
            style="Subtitle.TLabel",
        )
        description.pack(anchor=tk.W, pady=(0, 20))

        # File selection section
        file_frame = ttk.LabelFrame(container, text="Document Selection", padding=15)
        file_frame.pack(fill=tk.X, pady=(0, 15))

        # Document selection
        doc_frame = ttk.Frame(file_frame)
        doc_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            doc_frame,
            text="Select Word Document",
            style="Accent.TButton",
            command=self.select_file,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.file_label = ttk.Label(
            doc_frame,
            text="No document selected",
            width=50,
        )
        self.file_label.pack(side=tk.LEFT)

        # Output directory selection
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X)

        ttk.Button(
            output_frame,
            text="Output Directory",
            style="Secondary.TButton",
            command=self.select_directory,
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.dir_label = ttk.Label(output_frame, text="Use document directory")
        self.dir_label.pack(side=tk.LEFT)

        # Settings section
        settings_frame = ttk.LabelFrame(container, text="Analysis Settings", padding=15)
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # Settings grid
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill=tk.X)

        # Minimum mentions
        ttk.Label(settings_grid, text="Minimum mentions:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.min_spinbox = ttk.Spinbox(
            settings_grid,
            from_=1,
            to=99,
            width=8,
            textvariable=self.min_mentions,
        )
        self.min_spinbox.grid(row=0, column=1, padx=(0, 20))

        # Column index
        ttk.Label(settings_grid, text="Character column (1-based):").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )
        self.column_spinbox = ttk.Spinbox(
            settings_grid,
            from_=1,
            to=20,
            width=8,
            textvariable=self.column_var,
        )
        self.column_spinbox.grid(row=0, column=3, padx=(0, 20))

        # Case insensitive checkbox
        ttk.Checkbutton(
            settings_grid,
            text="Ignore case",
            variable=self.ignore_case_var,
        ).grid(row=1, column=0, columnspan=2, pady=(15, 0), sticky=tk.W)

        # Action buttons
        actions_frame = ttk.Frame(settings_grid)
        actions_frame.grid(row=0, column=4, rowspan=2, padx=(20, 0))

        self.analyze_button = ttk.Button(
            actions_frame,
            text="Analyze Document",
            style="Accent.TButton",
            command=self.analyze_document,
        )
        self.analyze_button.pack(pady=(0, 5))

        self.copy_button = ttk.Button(
            actions_frame,
            text="Copy Results",
            style="Secondary.TButton",
            command=self.copy_results,
            state=tk.DISABLED,
        )
        self.copy_button.pack()

        # Results section
        results_frame = ttk.LabelFrame(container, text="Results", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Results treeview
        columns = ("character", "count")
        self.tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        self.tree.heading("character", text="Character Name")
        self.tree.heading("count", text="Mentions")
        self.tree.column("character", width=400)
        self.tree.column("count", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for results
        scrollbar = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Status bar
        status_frame = ttk.Frame(container)
        status_frame.pack(fill=tk.X, pady=(15, 0))

        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
        )
        self.status_label.pack(anchor=tk.W)

    def select_file(self) -> None:
        """Open file dialog to select a Word document."""
        file_path = filedialog.askopenfilename(
            title="Select Word Document",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ],
        )
        
        if file_path:
            self.file_path = Path(file_path)
            self.file_label.config(text=self.file_path.name)
            self.status_var.set("Document selected. Configure settings and click Analyze.")
            self._update_button_states()

    def select_directory(self) -> None:
        """Open directory dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        
        if directory:
            self.output_dir = Path(directory)
            self.dir_label.config(text=f"Custom: {self.output_dir.name}")
        else:
            self.output_dir = None
            self.dir_label.config(text="Use document directory")

    def analyze_document(self) -> None:
        """Analyze the selected document."""
        if not self.file_path:
            messagebox.showwarning("No Document", "Please select a Word document first.")
            return

        # Get settings
        minimum = max(1, self.min_mentions.get())
        column_index = max(1, self.column_var.get()) - 1  # Convert to 0-based
        ignore_case = self.ignore_case_var.get()

        try:
            # Update status
            self.status_var.set("Analyzing document...")
            self.update()

            # Process document
            result = self.processor.process(self.file_path, column_index=column_index)
            
            # Generate statistics
            stats = self.processor.summarise(result.characters, ignore_case=ignore_case)
            
            # Filter by minimum mentions
            filtered_stats = [stat for stat in stats if stat.count >= minimum]
            self.characters_data = filtered_stats

            # Update display
            self._display_results()
            
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
            
            # Update status
            self.status_var.set(f"Analysis complete! Found {len(filtered_stats)} characters.")
            messagebox.showinfo(
                "Analysis Complete",
                f"Document analyzed successfully!\n\n"
                f"Characters found: {len(stats)}\n"
                f"Characters with {minimum}+ mentions: {len(filtered_stats)}\n"
                f"Report saved: {output_path.name}"
            )
            
            self._update_button_states()

        except Exception as exc:
            error_msg = f"Analysis failed: {str(exc)}"
            self.status_var.set(error_msg)
            messagebox.showerror("Analysis Error", error_msg)

    def _display_results(self) -> None:
        """Display the analysis results in the treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add character data
        for stat in self.characters_data:
            self.tree.insert("", tk.END, values=(stat.name, stat.count))

    def copy_results(self) -> None:
        """Copy results to clipboard."""
        if not self.characters_data:
            messagebox.showinfo("No Results", "No analysis results to copy.")
            return
        
        # Format results for clipboard
        lines = []
        for stat in self.characters_data:
            lines.append(f"{stat.name} — {stat.count}")
        
        result_text = "\n".join(lines)
        
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(result_text)
        
        messagebox.showinfo("Copied", f"Copied {len(lines)} characters to clipboard.")

    def _update_button_states(self) -> None:
        """Update button states based on current conditions."""
        has_file = self.file_path is not None
        has_results = len(self.characters_data) > 0
        
        # Analyze button
        self.analyze_button.config(state=tk.NORMAL if has_file else tk.DISABLED)
        
        # Copy button
        self.copy_button.config(state=tk.NORMAL if has_results else tk.DISABLED)


def run_app() -> None:
    """Main entry point for the application."""
    app = CharacterAnalysisGUI()
    app.mainloop()


if __name__ == "__main__":
    run_app()