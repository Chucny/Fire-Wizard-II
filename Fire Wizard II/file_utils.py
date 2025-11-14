# file_utils.py

"""
file_utils.py

A small Python library similar to PHP's file_get_contents.
Provides functions to:
- Read entire file content
- Read a specific line (row) from a file
"""

def file_get_contents(file_path, encoding="utf-8"):
    """
    Reads the entire content of a file and returns it as a string.
    """
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


def file_lines(file_path):
    """
    Reads all lines of a file and returns a list of strings (lines without newline characters).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def line(file_path, line_number):
    """
    Returns a specific line (1-based index) from the file.
    Returns None if line_number is out of range.
    """
    lines_list = file_lines(file_path)
    if 1 <= line_number <= len(lines_list):
        return lines_list[line_number - 1]
    return None
