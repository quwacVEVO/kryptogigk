def to_uppercase(text: str) -> str:
    return text.upper()

def to_lowercase(text: str) -> str:
    return text.lower()

def remove_diacritics(text: str) -> str:
    replacements = {
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E',
        'Ł': 'L', 'Ń': 'N', 'Ó': 'O',
        'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }

    return "".join([replacements.get(char, char) for char in text])

def remove_whitespace(text: str) -> str:
    return "".join(c for c in text if not c.isspace())

def remove_digits(text: str) -> str:
    return "".join(c for c in text if not c.isdigit())

def format_columns(text: str, rows: int = 7, column_width: int = 5) -> str:
    text = "".join(text[i:i+column_width] + " " for i in range(0, len(text), column_width))
    row_width = (column_width + 1) * rows
    return "\n".join(text[i:i+row_width] for i in range(0, len(text), row_width))

def alfa_26(text: str) -> str:
    text = to_uppercase(text)
    text = remove_diacritics(text)
    text = remove_whitespace(text)
    text = remove_digits(text)
    return "".join(c for c in text if c.isalpha())

def alfa_37(text: str) -> str:
    text = to_uppercase(text)
    text = remove_diacritics(text)
    return "".join(c for c in text if c.isalnum() or c.isspace())

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path: str, content: str) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_file(input_path: str, output_path: str = None, mode: str = "alfa_26") -> str:
    content = read_file(input_path)
    
    if mode == "alfa_37":
        result = alfa_37(content)
    else:
        result = alfa_26(content)
        
    if output_path:
        write_file(output_path, result)
        
    return result