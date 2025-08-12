"""Simple calculator app.

Usage:
    python calculator.py add 1 2
    python calculator.py --gui
"""
import argparse
import operator
import tkinter as tk
from tkinter import ttk

OPERATIONS = {
    'add': operator.add,
    'sub': operator.sub,
    'mul': operator.mul,
    'div': operator.truediv,
}


def calculate(op_name, a, b):
    if op_name not in OPERATIONS:
        raise ValueError(f"Unsupported operation: {op_name}")
    return OPERATIONS[op_name](a, b)


class CalculatorGUI:
    """Simple Tkinter-based interface with a result animation."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self._build_widgets()

    def _build_widgets(self):
        self.entry_a = ttk.Entry(self.root, width=10)
        self.entry_a.grid(row=0, column=0, padx=5, pady=5)

        ttk.Label(self.root, text="op").grid(row=0, column=1, padx=5)
        self.entry_b = ttk.Entry(self.root, width=10)
        self.entry_b.grid(row=0, column=2, padx=5, pady=5)

        self.op_var = tk.StringVar(value='add')
        for i, op in enumerate(OPERATIONS.keys()):
            ttk.Radiobutton(self.root, text=op, variable=self.op_var, value=op).grid(
                row=1, column=i, padx=5
            )

        ttk.Button(self.root, text="Calculate", command=self.on_calculate).grid(
            row=2, column=0, columnspan=4, pady=5
        )

        self.result_label = ttk.Label(self.root, text="", font=('Arial', 16))
        self.result_label.grid(row=3, column=0, columnspan=4, pady=10)

    def on_calculate(self):
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            result = calculate(self.op_var.get(), a, b)
            self._show_result(result)
        except Exception as exc:  # pragma: no cover - gui validation
            self._show_result(f"Error: {exc}")

    def _show_result(self, text):
        self.result_label.configure(text=str(text), foreground='#CCCCCC')
        self._animate_result(0)

    def _animate_result(self, step):
        colors = [
            '#CCCCCC', '#BBBBBB', '#AAAAAA', '#999999', '#888888', '#777777',
            '#666666', '#555555', '#444444', '#333333', '#222222', '#111111',
            '#000000'
        ]
        if step < len(colors):
            self.result_label.configure(foreground=colors[step])
            self.root.after(50, self._animate_result, step + 1)

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Simple calculator")
    parser.add_argument('operation', nargs='?', choices=OPERATIONS.keys())
    parser.add_argument('a', nargs='?', type=float)
    parser.add_argument('b', nargs='?', type=float)
    parser.add_argument('--gui', action='store_true', help="Launch GUI")
    args = parser.parse_args()

    if args.gui or args.operation is None:
        gui = CalculatorGUI()
        gui.run()
    else:
        result = calculate(args.operation, args.a, args.b)
        print(result)


if __name__ == '__main__':
    main()
