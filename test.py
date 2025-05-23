from tempfile import NamedTemporaryFile

import pytest

from shikaku import can_place, get_numbers_positions, place_rectangle, read_puzzle, solve_shikaku


@pytest.mark.parametrize(
    "content, expected",
    [
        ("3 0 0\n0 2 6\n4 5 0", [[3, 0, 0], [0, 2, 6], [4, 5, 0]]),
        ("1 2\n3 4", [[1, 2], [3, 4]]),
        ("5", [[5]]),
    ],
)
def test_read_puzzle_valid(content: str, expected: list[list[int]]) -> None:
    """Проверяет корректное чтение головоломки из файла."""
    with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
        tmpfile.write(content)
        tmpfile_name = tmpfile.name

    assert read_puzzle(tmpfile_name) == expected


def test_read_puzzle_empty_file() -> None:
    """Проверяет, что пустой файл вызывает ValueError."""
    with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
        tmpfile.write("")
        tmpfile_name = tmpfile.name

    with pytest.raises(ValueError, match="Файл пуст"):
        read_puzzle(tmpfile_name)


def test_read_puzzle_inconsistent_rows() -> None:
    """Проверяет, что строки разной длины вызывают ValueError."""
    with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
        tmpfile.write("1 2\n3 4 5")
        tmpfile_name = tmpfile.name

    with pytest.raises(ValueError, match="разной длины"):
        read_puzzle(tmpfile_name)


def test_get_numbers_positions() -> None:
    """Проверяет корректность определения чисел и их координат."""
    board = [[3, 0, 0], [0, 2, 6], [4, 5, 0]]
    expected = [(0, 0, 3), (1, 1, 2), (1, 2, 6), (2, 0, 4), (2, 1, 5)]
    result = get_numbers_positions(board)
    assert sorted(result) == sorted(expected)


@pytest.mark.parametrize(
    "board,r,c,h,w,number_r,number_c,expected",
    [
        ([[3, 0, 0], [0, 2, 6], [4, 5, 0]], 0, 0, 1, 1, 0, 0, True),
        ([[3, 0, 0], [0, 2, 6], [4, 5, 0]], 0, 0, 2, 2, 0, 0, False),
        ([[3, 0, 0], [0, 0, 0], [0, 0, 0]], 0, 0, 1, 3, 0, 0, True),
    ],
)
def test_can_place(
    board: list[list[int]],
    r: int,
    c: int,
    h: int,
    w: int,
    number_r: int,
    number_c: int,
    expected: bool,
) -> None:
    """Проверяет возможность размещения прямоугольника с учетом числа."""
    assert can_place(board, r, c, h, w, number_r, number_c) == expected


def test_place_rectangle() -> None:
    """Проверяет замену ячеек числом и неизменность исходной доски."""
    board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    expected = [[5, 5, 5], [5, 5, 5], [0, 0, 0]]
    result = place_rectangle(board, 0, 0, 2, 3, 5)
    assert result == expected
    assert board != result  # Ensure original was not modified


def test_solve_shikaku_simple() -> None:
    """Проверяет наличие хотя бы одного решения на простой сетке."""
    board = [
        [4, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    numbers = get_numbers_positions(board)
    solutions: list[list[list[int]]] = []
    solve_shikaku(board, numbers, solutions)
    assert len(solutions) >= 1
