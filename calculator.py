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
        self.current = ""
        self.first_operand = None
        self.operation = None
        self.display_var = tk.StringVar(value="0")
        self._build_widgets()

    def _build_widgets(self):
        self.result_label = ttk.Label(
            self.root, textvariable=self.display_var, font=("Arial", 24), anchor="e"
        )
        self.result_label.grid(row=0, column=0, columnspan=4, sticky="we", pady=10)

        buttons = [
            ('7', self.on_digit), ('8', self.on_digit), ('9', self.on_digit), ('+', self.on_operation),
            ('4', self.on_digit), ('5', self.on_digit), ('6', self.on_digit), ('-', self.on_operation),
            ('1', self.on_digit), ('2', self.on_digit), ('3', self.on_digit), ('*', self.on_operation),
            ('C', self.on_clear), ('0', self.on_digit), ('=', self.on_equal), ('/', self.on_operation),
        ]

        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)

        for idx, (text, handler) in enumerate(buttons):
            row = idx // 4 + 1
            col = idx % 4
            ttk.Button(
                self.root, text=text, command=lambda t=text: handler(t)
            ).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def on_digit(self, char):
        self.current += char
        self.display_var.set(self.current)

    def on_operation(self, op_char):
        if self.current:
            self.first_operand = float(self.current)
            self.operation = {"+": "add", "-": "sub", "*": "mul", "/": "div"}[op_char]
            self.current = ""

    def on_equal(self, _):
        if self.current and self.operation:
            try:
                second = float(self.current)
                result = calculate(self.operation, self.first_operand, second)
                self._show_result(result)
                self.current = str(result)
                self.first_operand = None
                self.operation = None
            except Exception as exc:  # pragma: no cover - gui validation
                self._show_result(f"Error: {exc}")

    def on_clear(self, _):
        self.current = ""
        self.first_operand = None
        self.operation = None
        self.display_var.set("0")

    def _show_result(self, text):
        self.display_var.set(str(text))
        self.result_label.configure(foreground="#CCCCCC")
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
