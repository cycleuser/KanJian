"""
GUI interface for KanJian using tkinter.

Provides interactive visualization window with parameter controls.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
import threading

from kanjian.api import kanjian_simulate, kanjian_visualize


class KanJianGUI:
    """Main GUI application for KanJian."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KanJian - Interactive Visual Explanations")
        self.root.geometry("1000x700")

        self.current_concept = tk.StringVar(value="magma")
        self.params: Dict[str, Any] = {}
        self.visualization_label: Optional[tk.Label] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        title_label = ttk.Label(
            main_frame,
            text="KanJian - Interactive Visual Explanations",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        ttk.Label(control_frame, text="Concept:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        concepts = ["magma", "pythagorean", "circle", "linear", "quadratic", "trig"]
        concept_combo = ttk.Combobox(
            control_frame,
            textvariable=self.current_concept,
            values=concepts,
            state="readonly",
            width=30,
        )
        concept_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        concept_combo.bind("<<ComboboxSelected>>", self._on_concept_change)

        self.param_frame = ttk.Frame(control_frame)
        self.param_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        self._update_param_frame()

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        simulate_btn = ttk.Button(
            button_frame, text="Simulate", command=self._run_simulation
        )
        simulate_btn.grid(row=0, column=0, padx=5)

        visualize_btn = ttk.Button(
            button_frame, text="Visualize", command=self._run_visualization
        )
        visualize_btn.grid(row=0, column=1, padx=5)

        save_btn = ttk.Button(
            button_frame, text="Save Image...", command=self._save_image
        )
        save_btn.grid(row=0, column=2, padx=5)

        viz_frame = ttk.LabelFrame(main_frame, text="Visualization", padding="10")
        viz_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(0, weight=1)

        self.visualization_label = ttk.Label(
            viz_frame, text="Visualization will appear here", anchor="center"
        )
        self.visualization_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(
            status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def _on_concept_change(self, event=None) -> None:
        """Handle concept selection change."""
        self._update_param_frame()

    def _update_param_frame(self) -> None:
        """Update parameter input fields based on selected concept."""
        for widget in self.param_frame.winfo_children():
            widget.destroy()

        concept = self.current_concept.get()
        params_config = {
            "magma": [
                ("length", 100, int),
                ("steps", 100, int),
                ("alpha", 0.1, float),
            ],
            "pythagorean": [
                ("a", 3, int),
                ("b", 4, int),
            ],
            "circle": [
                ("radius", 5, int),
                ("segments", 16, int),
            ],
            "linear": [
                ("slope", 1.0, float),
                ("intercept", 0.0, float),
            ],
            "quadratic": [
                ("a", 1.0, float),
                ("b", 0.0, float),
                ("c", 0.0, float),
            ],
            "trig": [
                ("func", "sin", str),
                ("amplitude", 1.0, float),
                ("frequency", 1.0, float),
            ],
        }

        params = params_config.get(concept, [])
        self.params = {}

        for i, (name, default, ptype) in enumerate(params):
            ttk.Label(self.param_frame, text=f"{name}:").grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2
            )

            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(self.param_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

            self.params[name] = (var, ptype, default)

    def _get_param_values(self) -> Dict[str, Any]:
        """Get current parameter values from input fields."""
        values = {}
        for name, (var, ptype, default) in self.params.items():
            try:
                values[name] = ptype(var.get())
            except ValueError:
                values[name] = default
        return values

    def _run_simulation(self) -> None:
        """Run simulation with current parameters."""

        def run():
            self.status_label.config(text="Running simulation...")
            concept = self.current_concept.get()
            params = self._get_param_values()
            steps = params.pop("steps", 100) if concept == "magma" else 1

            result = kanjian_simulate(concept=concept, steps=steps, params=params)

            self.root.after(0, self._on_simulation_complete, result)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _on_simulation_complete(self, result) -> None:
        """Handle simulation completion."""
        if result.success:
            self.status_label.config(
                text=f"Simulation completed: {result.data.get('concept', 'unknown')}"
            )
            messagebox.showinfo(
                "Simulation Complete",
                f"Concept: {result.data.get('concept', 'unknown')}\n"
                f"Steps: {result.data.get('steps', 0)}",
            )
        else:
            self.status_label.config(text="Simulation failed")
            messagebox.showerror("Simulation Error", result.error)

    def _run_visualization(self) -> None:
        """Run visualization with current parameters."""

        def run():
            self.status_label.config(text="Generating visualization...")
            concept = self.current_concept.get()
            params = self._get_param_values()

            result = kanjian_visualize(concept=concept, params=params)

            self.root.after(0, self._on_visualization_complete, result)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _on_visualization_complete(self, result) -> None:
        """Handle visualization completion."""
        if result.success:
            self.status_label.config(text="Visualization generated")
            if self.visualization_label:
                self.visualization_label.config(
                    text="✓ Visualization generated successfully!"
                )
            messagebox.showinfo(
                "Visualization Complete",
                f"Concept: {result.data.get('concept_data', {}).get('formula', 'N/A')}",
            )
        else:
            self.status_label.config(text="Visualization failed")
            messagebox.showerror("Visualization Error", result.error)

    def _save_image(self) -> None:
        """Save visualization to file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )

        if file_path:

            def run():
                self.status_label.config(text="Saving image...")
                concept = self.current_concept.get()
                params = self._get_param_values()

                result = kanjian_visualize(
                    concept=concept, params=params, output_path=file_path
                )

                self.root.after(0, self._on_save_complete, result)

            thread = threading.Thread(target=run, daemon=True)
            thread.start()

    def _on_save_complete(self, result) -> None:
        """Handle save completion."""
        if result.success:
            self.status_label.config(
                text=f"Image saved to: {result.data.get('file', 'unknown')}"
            )
            messagebox.showinfo(
                "Save Complete",
                f"Image saved to:\n{result.data.get('file', 'unknown')}",
            )
        else:
            self.status_label.config(text="Save failed")
            messagebox.showerror("Save Error", result.error)

    def run(self) -> int:
        """Start the GUI application."""
        self.root.mainloop()
        return 0


def main() -> int:
    """Main entry point for GUI."""
    app = KanJianGUI()
    return app.run()


if __name__ == "__main__":
    import sys

    sys.exit(main())
