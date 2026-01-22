import math
import datetime


class Calculator:
    def __init__(self):
        self.history = []

    def _save_history(self, expression, result):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = f"[{time}] {expression} = {result}"
        self.history.append(record)

    def add(self, a, b):
        result = a + b
        self._save_history(f"{a} + {b}", result)
        return result

    def subtract(self, a, b):
        result = a - b
        self._save_history(f"{a} - {b}", result)
        return result

    def multiply(self, a, b):
        result = a * b
        self._save_history(f"{a} * {b}", result)
        return result

    def divide(self, a, b):
        if b == 0:
            return "Error: Division by zero"
        result = a / b
        self._save_history(f"{a} / {b}", result)
        return result

    def power(self, a, b):
        result = a ** b
        self._save_history(f"{a} ^ {b}", result)
        return result

    def modulus(self, a, b):
        result = a % b
        self._save_history(f"{a} % {b}", result)
        return result

    def square_root(self, a):
        if a < 0:
            return "Error: Negative number"
        result = math.sqrt(a)
        self._save_history(f"√{a}", result)
        return result

    def show_history(self):
        if not self.history:
            print("No history found.")
        else:
            print("\n--- Calculation History ---")
            for item in self.history:
                print(item)

    def clear_history(self):
        self.history.clear()
        print("History cleared!")


def get_number(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("Invalid input! Please enter a number.")


def main():
    calc = Calculator()

    while True:
        print("\n====== Advanced Calculator ======")
        print("1. Addition")
        print("2. Subtraction")
        print("3. Multiplication")
        print("4. Division")
        print("5. Power")
        print("6. Modulus")
        print("7. Square Root")
        print("8. Show History")
        print("9. Clear History")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            a = get_number("Enter first number: ")
            b = get_number("Enter second number: ")
            print("Result:", calc.add(a, b))

        elif choice == "2":
            a = get_number("Enter first number: ")
            b = get_number("Enter second number: ")
            print("Result:", calc.subtract(a, b))

        elif choice == "3":
            a = get_number("Enter first number: ")
            b = get_number("Enter second number: ")
            print("Result:", calc.multiply(a, b))

        elif choice == "4":
            a = get_number("Enter first number: ")
            b = get_number("Enter second number: ")
            print("Result:", calc.divide(a, b))

        elif choice == "5":
            a = get_number("Enter base: ")
            b = get_number("Enter power: ")
            print("Result:", calc.power(a, b))

        elif choice == "6":
            a = get_number("Enter first number: ")
            b = get_number("Enter second number: ")
            print("Result:", calc.modulus(a, b))

        elif choice == "7":
            a = get_number("Enter number: ")
            print("Result:", calc.square_root(a))

        elif choice == "8":
            calc.show_history()

        elif choice == "9":
            calc.clear_history()

        elif choice == "0":
            print("Thanks for using Advanced Calculator 👋")
            break

        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
