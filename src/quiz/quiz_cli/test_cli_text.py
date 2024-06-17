


def print_title():
    with open('title.txt', 'r') as file:
        # Read the contents of the file
        print(file.read() + '\n')

def letter_to_number(letter):
    """
        Converts a letter to its corresponding number.
        a or A -> 1, b or B -> 2, ..., z or Z -> 26

        Parameters:
        letter (str): The letter to be converted.

        Returns:
        int: The corresponding number of the letter.
        """
    if not letter.isalpha() or len(letter) != 1:
        raise ValueError("Input must be a single alphabetic character.")
    return ord(letter.lower()) - ord('a') + 1


def number_to_letter(number):
    """
    Converts a number to its corresponding lowercase letter.
    1 -> a, 2 -> b, ..., 26 -> z

    Parameters:
    number (int): The number to be converted.

    Returns:
    str: The corresponding lowercase letter.
    """
    if not (1 <= number <= 26):
        raise ValueError("Input must be a number between 1 and 26.")
    return chr(number + ord('a') - 1)

def format_text(text, width, hanging_width=None):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Check if there's enough space for the word in the current line
        if len(current_line) + len(word) <= width:
            current_line += word + " "
        else:
            lines.append(current_line.rstrip())

            # Start a new line with hanging width, if applies
            current_line = ""
            if hanging_width is not None:
                current_line += " " * hanging_width
            current_line += word + " "
    # Add the last line
    if current_line:
        lines.append(current_line.rstrip())
    return '\n'.join(lines)
