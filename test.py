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
    """
    Проверяет, что при попытке открыть пустой файл программа завершает работу с кодом 1.

    Тест записывает пустой файл, вызывает `read_puzzle` и проверяет, что она завершает выполнение с ошибкой.
    """
    with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
        tmpfile.write("")
        tmpfile_name = tmpfile.name

    with pytest.raises(SystemExit) as e:
        read_puzzle(tmpfile_name)
    assert e.value.code == 1


def test_read_puzzle_inconsistent_rows() -> None:
    """
    Проверяет, что при наличии строк разной длины в файле программа завершает работу с кодом 1.

    Тест создаёт файл с несогласованными строками, вызывает `read_puzzle` и проверяет,

    что она завершает выполнение с ошибкой.
    """
    with NamedTemporaryFile(mode="w+", delete=False) as tmpfile:
        tmpfile.write("1 2\n3 4 5")
        tmpfile_name = tmpfile.name

    with pytest.raises(SystemExit) as e:
        read_puzzle(tmpfile_name)
    assert e.value.code == 1


def test_get_numbers_positions() -> None:
    """
    Проверяет, что функция `get_numbers_positions` корректно находит все числа на доске и их координаты.

    Тест использует фиксированную доску и сравнивает результат с ожидаемым списком позиций.
    """
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
    """Проверяет, что функция `can_place` корректно определяет возможность размещения прямоугольника."""
    assert can_place(board, r, c, h, w, number_r, number_c) == expected


def test_place_rectangle() -> None:
    """
    Проверяет, что функция `place_rectangle` корректно заменяет ячейки заданным числом.

    Тест также проверяет, что исходная доска не была изменена.
    """
    board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    expected = [[5, 5, 5], [5, 5, 5], [0, 0, 0]]
    result = place_rectangle(board, 0, 0, 2, 3, 5)
    assert result == expected
    assert board != result


def test_solve_shikaku_simple() -> None:
    """
    Проверяет, что функция `solve_shikaku` находит хотя бы одно решение для простой головоломки.

    Тест использует минимальную сетку с одним числом, равным размеру сетки.
    """
    board = [
        [4, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    numbers = get_numbers_positions(board)
    solutions: list[list[list[int]]] = []
    solve_shikaku(board, numbers, solutions)
    assert len(solutions) >= 1
