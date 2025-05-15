import sys
from copy import deepcopy


def read_puzzle(filename: str) -> list[list[int]]:
    """Чтение головоломки из файла."""
    try:
        with open(filename) as f:
            puzzle = [list(map(int, line.strip().split())) for line in f if line.strip()]
        if not puzzle:
            print("Ошибка: файл пуст.")
            sys.exit(1)
        width = len(puzzle[0])
        for row in puzzle:
            if len(row) != width:
                print("Ошибка: файл содержит строки разной длины.")
                sys.exit(1)
        return puzzle
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден.")
        sys.exit(1)


def print_board(board: list[list[int]]) -> None:
    """Вывод доски в консоль."""
    for row in board:
        formatted_row = []
        for cell in row:
            if cell == 0:
                formatted_row.append(".")
            else:
                formatted_row.append(str(cell))
        print(" ".join(formatted_row))
    print()


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


def main() -> None:
    """Основная функция."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Решатель головоломки Shikaku.", epilog="Пример использования: python shikaku_solver.py puzzle.txt"
    )
    parser.add_argument(
        "file",
        help="Путь к файлу с головоломкой Shikaku. "
        "Файл должен содержать сетку чисел, разделённых пробелами, где 0 обозначает пустую ячейку.",
    )
    args = parser.parse_args()

    puzzle = read_puzzle(args.file)
    print("Исходная головоломка:")
    print_board(puzzle)

    numbers = get_numbers_positions(puzzle)
    total_cells = len(puzzle) * len(puzzle[0])
    sum_of_numbers = sum(num for _, _, num in numbers)

    if sum_of_numbers != total_cells:
        print("Ошибка: сумма чисел не равна количеству ячеек. Невозможно найти решение.")
        return
    for r, c, num in numbers:
        possible = False
        for h in range(1, num + 1):
            if num % h != 0:
                continue
            w = num // h
            for tr in range(max(0, r - h + 1), min(len(puzzle) - h + 1, r + 1)):
                for tc in range(max(0, c - w + 1), min(len(puzzle[0]) - w + 1, c + 1)):
                    conflict = False
                    for dr in range(h):
                        for dc in range(w):
                            x, y = tr + dr, tc + dc
                            if puzzle[x][y] != 0 and (x != r or y != c):
                                conflict = True
                                break
                        if conflict:
                            break
                    if not conflict:
                        possible = True
                        break
                if possible:
                    break
            if possible:
                break
        if not possible:
            print(f"Ошибка: невозможно разместить число {num} в ({r}, {c})")
            return

    solutions: list[list[list[int]]] = []
    solve_shikaku(puzzle, numbers, solutions)

    if not solutions:
        print("Решений не найдено. Возможно, головоломка некорректна или содержит противоречия.")
    else:
        print(f"Найдено {len(solutions)} решений:\n")
        for idx, solution in enumerate(solutions, 1):
            print(f"Решение #{idx}:")
            print_board(solution)


if __name__ == "__main__":
    main()
