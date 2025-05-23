import json
import os
import tkinter as tk
from copy import deepcopy
from itertools import product
from tkinter import Tk, filedialog, messagebox

STATE_FILE = "last_state.json"


def read_puzzle(filename: str) -> list[list[int]]:
    """Чтение головоломки из файла."""
    try:
        with open(filename) as f:
            puzzle = [list(map(int, line.strip().split())) for line in f if line.strip()]
        if not puzzle:
            raise ValueError("Файл пуст.")
        width = len(puzzle[0])
        for row in puzzle:
            if len(row) != width:
                raise ValueError("Файл содержит строки разной длины.")
        return puzzle
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{filename}' не найден.")


def get_numbers_positions(board: list[list[int]]) -> list[tuple[int, int, int]]:
    """Получение позиций чисел на доске."""
    positions = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] > 0:
                positions.append((i, j, board[i][j]))
    return sorted(positions, key=lambda x: -x[2])


def can_place(board: list[list[int]], r: int, c: int, h: int, w: int, number_r: int, number_c: int) -> bool:
    """Проверяет,можно ли разместить прямоугольник h x w с верхним левым углом (r,c),содержащий (number_r, number_c)."""
    rows = len(board)
    cols = len(board[0])

    if r + h > rows or c + w > cols:
        return False

    has_number = False
    for dr in range(h):
        for dc in range(w):
            val = board[r + dr][c + dc]
            if val != 0 and (r + dr != number_r or c + dc != number_c):
                return False
            if r + dr == number_r and c + dc == number_c:
                has_number = True
    return has_number


def place_rectangle(board: list[list[int]], r: int, c: int, h: int, w: int, num: int) -> list[list[int]]:
    """Размещает прямоугольник с заданным числом."""
    new_board = deepcopy(board)
    for dr in range(h):
        for dc in range(w):
            new_board[r + dr][c + dc] = num
    return new_board


def solve_shikaku(
    board: list[list[int]], numbers: list[tuple[int, int, int]], solutions: list[list[list[int]]]
) -> None:
    """Рекурсивный поиск всех решений."""
    if not numbers:
        solutions.append(deepcopy(board))
        return

    number_r, number_c, num = numbers[0]

    for h in range(1, num + 1):
        if num % h != 0:
            continue
        w = num // h

        rows = len(board)
        cols = len(board[0])

        for top_r in range(max(0, number_r - h + 1), min(rows - h + 1, number_r + 1)):
            for top_c in range(max(0, number_c - w + 1), min(cols - w + 1, number_c + 1)):

                if can_place(board, top_r, top_c, h, w, number_r, number_c):
                    new_board = place_rectangle(board, top_r, top_c, h, w, num)
                    solve_shikaku(new_board, numbers[1:], solutions)


class ShikakuGUI:
    """Графический Интерфейс."""

    def __init__(self, root: Tk) -> None:
        """Инициализатор."""
        self.root = root
        self.root.title("Shikaku Solver")
        self.canvas = tk.Canvas(root, width=600, height=600)
        self.solutions: list[list[list[int]]] = []
        self.current = 0
        self.cell_size = 40

        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Открыть файл", command=self.load_file).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="◀", command=self.prev_solution).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="▶", command=self.next_solution).pack(side=tk.LEFT)
        self.canvas.pack()

        self.last_filepath = ""
        self.load_state()

    def draw_board(self, board: list[list[int]]) -> None:
        """Рендеринг поля."""
        self.canvas.delete("all")
        rows, cols = len(board), len(board[0])
        for r in range(rows):
            for c in range(cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                val = board[r][c]
                hex1 = (val * 25) % 255
                hex2 = (val * 50) % 255
                hex3 = (val * 75) % 255
                color = f"#{hex1:02x}{hex2:02x}{hex3:02x}" if val != 0 else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                if val != 0:
                    self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(val), font=("Arial", 12))

    def load_file(self) -> None:
        """Загрузка файла."""
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file:
            return
        try:
            puzzle = read_puzzle(file)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            return

        numbers = get_numbers_positions(puzzle)
        total_cells = len(puzzle) * len(puzzle[0])
        sum_of_numbers = sum(num for _, _, num in numbers)

        if sum_of_numbers != total_cells:
            messagebox.showerror("Ошибка", "Сумма чисел не равна количеству ячеек.")
            return

        for r, c, num in numbers:
            possible = any(
                not any(
                    puzzle[tr + dr][tc + dc] != 0 and (tr + dr != r or tc + dc != c)
                    for dr, dc in product(range(h), range(w))
                )
                for h in filter(lambda h: num % h == 0, range(1, num + 1))
                for w in [num // h]
                for tr in range(max(0, r - h + 1), min(len(puzzle) - h + 1, r + 1))
                for tc in range(max(0, c - w + 1), min(len(puzzle[0]) - w + 1, c + 1))
            )
            if not possible:
                messagebox.showerror("Ошибка", f"Невозможно разместить число {num} в ({r}, {c})")
                return

        self.solutions.clear()
        solve_shikaku(puzzle, numbers, self.solutions)
        if not self.solutions:
            messagebox.showinfo("Результат", "Решения не найдены.")
        else:
            self.current = 0
            self.last_filepath = file
            self.save_state(file)
            self.draw_board(self.solutions[0])

    def next_solution(self) -> None:
        """Показывает следующее решение."""
        if self.solutions:
            self.current = (self.current + 1) % len(self.solutions)
            self.draw_board(self.solutions[self.current])
            self.save_state(self.last_filepath)

    def prev_solution(self) -> None:
        """Показывает предыдущее решение."""
        if self.solutions:
            self.current = (self.current - 1) % len(self.solutions)
            self.draw_board(self.solutions[self.current])
            self.save_state(self.last_filepath)

    def save_state(self, filepath: str) -> None:
        """Сохранение состояния приложения."""
        state = {"filepath": filepath, "current": self.current}
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

    def load_state(self) -> None:
        """Загрузка состояния приложения."""
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            filepath = state.get("filepath")
            self.current = state.get("current", 0)
            if filepath and os.path.exists(filepath):
                puzzle = read_puzzle(filepath)
                numbers = get_numbers_positions(puzzle)
                self.solutions.clear()
                solve_shikaku(puzzle, numbers, self.solutions)
                if self.solutions:
                    self.draw_board(self.solutions[self.current % len(self.solutions)])
                self.last_filepath = filepath
        except Exception as e:
            print("Ошибка восстановления состояния:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = ShikakuGUI(root)
    root.mainloop()
