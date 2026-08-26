import ast
import operator

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class SafeCalculator:
    """Evaluate basic arithmetic without using eval()."""

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def calculate(cls, expression):
        expression = expression.strip().replace("×", "*").replace("÷", "/")
        if not expression:
            raise ValueError("Enter a calculation.")
        if len(expression) > 100:
            raise ValueError("Calculation is too long.")
        tree = ast.parse(expression, mode="eval")
        return cls._node(tree.body)

    @classmethod
    def _node(cls, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in cls.OPERATORS:
            left = cls._node(node.left)
            right = cls._node(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError
            return cls.OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in cls.OPERATORS:
            return cls.OPERATORS[type(node.op)](cls._node(node.operand))
        raise ValueError("Use numbers and +, -, ×, ÷, or % only.")


class AccessibleCalculator(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)

        self.display = toga.TextInput(
            placeholder="Enter calculation",
            accessibility_label="Calculation input",
            style=Pack(flex=1, padding=10),
        )
        self.result = toga.Label(
            "Result: ready",
            accessibility_label="Calculator result",
            style=Pack(padding=10),
        )

        content = toga.Box(style=Pack(direction=COLUMN, padding=10))
        content.add(self.display)
        content.add(self.result)

        buttons = [
            ("7", "7"), ("8", "8"), ("9", "9"), ("÷", " / "),
            ("4", "4"), ("5", "5"), ("6", "6"), ("×", " * "),
            ("1", "1"), ("2", "2"), ("3", "3"), ("−", " - "),
            ("0", "0"), (".", "."), ("%", " % "), ("+", " + "),
        ]
        for row in range(4):
            box = toga.Box(style=Pack(direction=ROW, flex=1))
            for label, value in buttons[row * 4:(row + 1) * 4]:
                button = toga.Button(
                    label,
                    on_press=self.insert_value,
                    style=Pack(flex=1, padding=3),
                    accessibility_label=f"{label} button",
                )
                button.value = value
                box.add(button)
            content.add(box)

        actions = toga.Box(style=Pack(direction=ROW, flex=1))
        clear = toga.Button(
            "Clear", on_press=self.clear, style=Pack(flex=1, padding=3),
            accessibility_label="Clear calculation",
        )
        equals = toga.Button(
            "Equals", on_press=self.calculate, style=Pack(flex=1, padding=3),
            accessibility_label="Calculate result",
        )
        actions.add(clear)
        actions.add(equals)
        content.add(actions)

        self.main_window.content = content
        self.main_window.show()

    def insert_value(self, widget):
        self.display.value = (self.display.value or "") + widget.value
        self.result.text = f"Calculation: {self.display.value}"

    def clear(self, widget):
        self.display.value = ""
        self.result.text = "Result: ready"

    def calculate(self, widget):
        try:
            value = SafeCalculator.calculate(self.display.value)
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            self.result.text = f"Result: {value}"
        except ZeroDivisionError:
            self.result.text = "Error: cannot divide by zero"
        except (ValueError, SyntaxError):
            self.result.text = "Error: invalid calculation"


def main():
    return AccessibleCalculator("Accessible Calculator", "com.pbtechfacts.accessiblecalculator")
