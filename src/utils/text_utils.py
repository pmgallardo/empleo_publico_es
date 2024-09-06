def dbgt(text):
    dbgt_on = False
    if dbgt_on:
        printt(text)

def printt(text):
    term_width = 80
    print(shrink_text(text, term_width))

def shrink_text(text, width, hanging_width=None):
    paragraphs = text.split('\n')  # Split text into paragraphs by line breaks
    wrapped_paragraphs = []

    for paragraph in paragraphs:
        words = paragraph.split()
        lines = []
        current_line = ""

        for word in words:
            # Check if there's enough space for the word in the current line
            if len(current_line) + len(word) + 1 <= width:  # +1 for the space
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word

        # Add the last line if it exists
        if current_line:
            lines.append(current_line)

        # Apply hanging width if provided
        if hanging_width is not None:
            lines = [(" " * hanging_width) + line for line in lines]

        wrapped_paragraphs.append("\n".join(lines))

    return "\n".join(wrapped_paragraphs)

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



# NOT TEXT UTILS, BUT UTILS

def count_instances(a, b):
    # Initialize the dictionary with all unique values from a with a count of 0
    count_dict = {key: 0 for key in a}

    # Count the occurrences of each element in b
    for value in b:
        if value in count_dict:
            count_dict[value] += 1

    return count_dict

def count_occurrences_with_zeros(arr, min_val, max_val):
    if not arr:
        return {}

    # Determine the range of values
    #min_val = min(arr)
    #max_val = max(arr)

    # Initialize the count dictionary with zeros
    count_dict = {i: 0 for i in range(min_val, max_val + 1)}

    # Count occurrences
    for num in arr:
        count_dict[num] += 1

    return count_dict