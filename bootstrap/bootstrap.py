import sys
import re


class SpiderError(Exception):
    pass


class SpiderBootstrap:
    def __init__(self):
        self.variables = {}

    def evaluate(self, expression):
        expression = expression.strip()

        # String
        if (
            len(expression) >= 2
            and expression.startswith('"')
            and expression.endswith('"')
        ):
            return expression[1:-1]

        # Integer
        if re.fullmatch(r"-?\d+", expression):
            return int(expression)

        # Float
        if re.fullmatch(r"-?\d+\.\d+", expression):
            return float(expression)

        # Boolean
        if expression == "true":
            return True

        if expression == "false":
            return False

        # Variable
        if expression in self.variables:
            return self.variables[expression]

        # Addition
        parts = self.split_operator(expression, "+")

        if len(parts) > 1:
            values = [self.evaluate(part) for part in parts]

            if all(isinstance(x, (int, float)) for x in values):
                return sum(values)

            return "".join(str(x) for x in values)

        # Subtraction
        parts = self.split_operator(expression, "-")

        if len(parts) > 1:
            result = self.evaluate(parts[0])

            for part in parts[1:]:
                result -= self.evaluate(part)

            return result

        # Multiplication
        parts = self.split_operator(expression, "*")

        if len(parts) > 1:
            result = self.evaluate(parts[0])

            for part in parts[1:]:
                result *= self.evaluate(part)

            return result

        # Division
        parts = self.split_operator(expression, "/")

        if len(parts) > 1:
            result = self.evaluate(parts[0])

            for part in parts[1:]:
                result /= self.evaluate(part)

            return result

        raise SpiderError(
            f"Unknown expression: {expression}"
        )

    def split_operator(self, expression, operator):
        parts = []
        current = ""
        inside_string = False
        parentheses = 0

        for char in expression:

            if char == '"':
                inside_string = not inside_string

            if char == "(" and not inside_string:
                parentheses += 1

            if char == ")" and not inside_string:
                parentheses -= 1

            if (
                char == operator
                and not inside_string
                and parentheses == 0
            ):
                parts.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            parts.append(current.strip())

        return parts

    def execute_line(self, line, line_number):

        line = line.strip()

        if not line:
            return

        if line.startswith("//"):
            return

        # print(...)
        if line.startswith("print(") and line.endswith(")"):

            expression = line[6:-1]

            value = self.evaluate(expression)

            print(value)

            return

        # let variable = value
        match = re.match(
            r"let\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)",
            line
        )

        if match:

            name = match.group(1)

            expression = match.group(2)

            self.variables[name] = self.evaluate(expression)

            return

        # variable = value
        match = re.match(
            r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)",
            line
        )

        if match:

            name = match.group(1)

            expression = match.group(2)

            if name not in self.variables:
                raise SpiderError(
                    f"Variable '{name}' does not exist"
                )

            self.variables[name] = self.evaluate(expression)

            return

        raise SpiderError(
            f"Unknown Spider statement: {line}"
        )

    def run_file(self, filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                for line_number, line in enumerate(
                    file,
                    start=1
                ):

                    try:

                        self.execute_line(
                            line,
                            line_number
                        )

                    except Exception as error:

                        print(
                            "\nSpider Error"
                            f"\nFile: {filename}"
                            f"\nLine: {line_number}"
                            f"\n{error}"
                        )

                        return

        except FileNotFoundError:

            print(
                f"Spider Error: File '{filename}' not found."
            )


def main():

    if len(sys.argv) < 2:

        print(
            "Spider Language Bootstrap v0.1"
        )

        print(
            "Usage:"
        )

        print(
            "python bootstrap.py <file.spider>"
        )

        return

    filename = sys.argv[1]

    if not filename.endswith(".spider"):

        print(
            "Spider Error:"
            " file must end with .spider"
        )

        return

    interpreter = SpiderBootstrap()

    interpreter.run_file(filename)


if __name__ == "__main__":

    main()
