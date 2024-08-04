import PyPDF2
import re
import os
from multichoice_question import MultichoiceQuestion
from question_converter import convert_multichoice_questions_to_aiken
from question_converter import convert_multichoice_questions_to_json

# constant
TEST_QUESTION_HEADER = "PREGUNTAS DE TEST"
SOLUTION_SECTION_HEADER = "SOLUCIONES A LAS PREGUNTAS DE TEST"
POSSIBLE_SEPARATORS = [".", ")"]

# global variables
isVerboseOutput = True
mcqs = []
cur_mcq = None
cur_q_elem = ""
title = ""
statement_separator = None
option_separator = None

def dscr(text):
    global isVerboseOutput
    if isVerboseOutput:
        print(text)

def convert_number_to_letter(number):
    # Ensure the number is within the valid range for lowercase letters
    if 1 <= number <= 26:
        # Calculate the corresponding ASCII value (97 is the ASCII for 'a')
        return chr(number + 96)
    else:
        raise ValueError("Number out of range. Must be between 1 and 26 inclusive.")

def check_line_starts_like_q_elem(counter_num, elem_separator, line_input, isLetter):
        # Sets a number or letter as question element ordinal
        elem_counter = counter_num
        if isLetter:
            try:
                elem_counter = convert_number_to_letter(elem_counter)
            except ValueError as ve:
                print(f"Error {ve}")

        # Calculates all possible starting strings

        possible_elem_starts = []
        if elem_separator is None:
            for q_elem_separator in POSSIBLE_SEPARATORS:
                possible_elem_starts.append([str(elem_counter) + q_elem_separator, q_elem_separator])
        else:
            possible_elem_starts.append([str(elem_counter) + elem_separator, elem_separator])

        # Trim line input
        line = line_input.strip()

        # Check if line follows the pattern of question element
        for option_start in possible_elem_starts:
            if line.startswith(option_start[0]):
                return option_start[1]
        return ""

def add_statement():
    global cur_q_elem
    global statement_separator

    if cur_q_elem != "":
        # Ensure there is no header text within the line
        cur_q_elem = cur_q_elem.replace(header_text, "").strip()

        dscr("Statement added: " + cur_q_elem)

        # Removes the letter and symbol
        pattern = r'^\d+' + re.escape(statement_separator) + r' '
        cur_q_elem = re.sub(pattern, "", cur_q_elem)

        # Adds the completed statement to statements array
        cur_mcq.add_statement(cur_q_elem)

        cur_q_elem = ""
def add_option():
    global cur_q_elem
    global option_separator

    if cur_q_elem != "":
        # Ensure there is no header text within the line
        cur_q_elem = cur_q_elem.replace(header_text, "").strip()

        # Removes the letter, separator and space from the beginning of sentence
        pattern = r'^[a-zA-Z]' + re.escape(option_separator) + r' '
        cur_q_elem = re.sub(pattern, "", cur_q_elem)

        dscr(">>> Option added: " + cur_q_elem)

        # Adds the completed option to options array
        cur_mcq.add_option(cur_q_elem)

    cur_q_elem = ""

def add_question(topic):
    global cur_mcq
    if cur_mcq is not None:
        # Add missing attributes
        cur_mcq.add_call(2022)
        cur_mcq.add_topic(topic)
        cur_mcq.add_source("ASTIC")

        dscr(">>> Question completed and added")

        # Add the completed question to questions array
        mcqs.append(cur_mcq)
    cur_mcq = MultichoiceQuestion()

def close_current_question(topic):
    add_option()
    add_question(topic)

def trim_line(text):
    trim_line = text

    # Remove strange characters
    # Happens in 029.pdf : ● 7. TEST / ○ 7.1 PREGUNTAS DE TEST
    strange_chars = "●○"
    translation_table = str.maketrans("", "", strange_chars)
    # Use translate to remove the strange characters
    trim_line = trim_line.translate(translation_table)

    #adds a single space between words
    trim_line = trim_line.strip()
    trim_line = ' '.join(trim_line.split()).strip()

    # Removes the precedent space before a dot.
    # Occurs in 030.pdf, line 817
    pattern = r'\s+\.'
    # Replace the matched pattern with just a dot
    trim_line = re.sub(pattern, '.', trim_line)

    return trim_line

def must_discard_line(line):
    global header_text

    # Check whether line is blank
    if line == "":
        return True

    # Check whether is a number (it is usually the page number)
    if line.isnumeric():
        return True

    # Check whether is the header_text
    if line == header_text:
        return True

    # string that contains only the character -
    #pattern = r'^[-_]+$'
    ## string that contains only the character -
    #pattern = re.compile(r'^[^a-zA-Z]*$')
    # string that contains only special characters (like -)
    pattern = re.compile(r'^[\W_]+$')
    if re.match(pattern, line.strip()):
        return True

    return False

def create_junk_patterns(header):
    # Create a list of junk patterns
    qs_junk_patterns = [
        r"\d+\.\d+\. PREGUNTAS DE TEST",
        r"\d+\.\d+ PREGUNTAS DE TEST",
        r"\d+\. PREGUNTAS DE TEST",
        r"\d+ PREGUNTAS DE TEST",
        r"PREGUNTAS DE TEST",
        r"\d+\. TEST",
        r"\d+ TEST"
    ]
    many_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in qs_junk_patterns]

    literal_patterns = []

    # Add literal pattern with dot if header does not end with dot
    if header[-1] != ".":
        literal_patterns.append(header + ".")

    literal_patterns.append(header)

    # Removes the header text after removing symbols in the end
    # This case happens in 029.pdf
    symbols_to_remove = "."
    header_text_wo_end_symbols = header.rstrip(symbols_to_remove)
    if header_text_wo_end_symbols != header:
        literal_patterns.append(header_text_wo_end_symbols)

    # Debugging: Check the value of header
    dscr(f"Header text: '{header}'")

    # Debugging: Check literal patterns
    dscr("Literal patterns:")
    for pattern in literal_patterns:
        dscr(f"- {pattern}")

    # accept empty spaces between characters
    #     single_pattern = r'\s*'.join(single_pattern)

    # Create regex patterns
    regex_patterns = [re.compile(re.escape(pattern), re.IGNORECASE) for pattern in literal_patterns]

    return regex_patterns + many_patterns


    #
    #
    #
    # global header_text
    #
    # new_text = text
    #
    # # Create a local copy of all patterns
    # many_patterns = qs_junk_patterns.copy()
    #
    # literal_patterns = []
    #
    # # Also removes the header text after removing symbols in the end
    # # This case happens in 029.pdf
    # symbols_to_remove = "."
    # header_text_wo_end_symbols = header_text.rstrip(symbols_to_remove)
    # literal_patterns.append(header_text_wo_end_symbols)
    #
    # # Add literal patterns
    # literal_patterns.append(header_text)
    #
    # # It adds a . at the end of the header, in case there is not
    # # This case happens in 033.pdf
    # if header_text[-1] != ".":
    #     literal_patterns.append(header_text+".")
    #
    # for literal_pattern in literal_patterns:
    #     # includes runtime junk text, like the doc title, in the first position
    #     single_pattern = re.escape(literal_pattern)
    #     # accept empty spaces between characters
    #     single_pattern = r'\s*'.join(single_pattern)
    #     # ignore case
    #     single_pattern = re.compile(single_pattern, re.IGNORECASE)
    #     # put the first in the array
    #     many_patterns = [single_pattern] + many_patterns
    #
    # return many_patterns

def remove_junk_text2(text, junk_patterns, where):
    # Junk text are:
    # - Header text. Example: Tema 29. La información en las organizaciones. Las organizaciones basadas en la información. La
    # - Quetions titles after the tile: ● 7. TEST / 7.1 PREGUNTAS DE TEST
    #dscr(f"Input text: {text}")

    new_text = text

    for pattern in junk_patterns:
        if where == "start":
            pattern_copy = re.compile(f'^{pattern.pattern}', pattern.flags)
        else:
            pattern_copy = pattern

        new_text = re.sub(pattern_copy, "", new_text)
        new_text = new_text.strip()

        #dscr(f"Intermediate text: {new_text}")

    return new_text
def remove_junk_text_anywhere2(text):
    global header_text

    new_text = text

    # Create a local copy of all patterns
    many_patterns = qs_junk_patterns.copy()

    # includes runtime junk text, like the doc title, in the first position
    single_pattern = re.escape(header_text)
    many_patterns = [single_pattern] + many_patterns

    # Also removes the header text after removing symbols in the end
    # This case happens in 029.pdf
    symbols_to_remove = ". "
    header_text_wo_end_symbols = header_text.rstrip(symbols_to_remove)
    if header_text != header_text_wo_end_symbols:
        single_pattern = re.escape(header_text_wo_end_symbols)
        many_patterns = many_patterns[:1] + [single_pattern] + many_patterns[1:]

    # Replaces the junk text with nothing
    for pattern in many_patterns:
        new_text = re.sub(pattern, "", new_text)
        new_text = new_text.strip()

    return new_text

def do_when_title_found(title):
    state = 3
    junk_patterns = create_junk_patterns(title)
    dscr(">>> Full title is: " + title)

    #return state, header and junk_patterns
    return state, title, junk_patterns

def extract_questions(lines, topic):
    global cur_q_elem
    global title
    global header_text
    global statement_separator
    global option_separator

    qcounter = 0
    ocounter = 0

    # STATE
    # 1 = Reading topic content, not doc title read
    # 2 = Reading topic content, doc title read started
    # 3 = Reading topic content, doc title read finished
    # 4 = Reading questions
    # 5 = Reading solutions
    # 6 = Reading remaining topic content
    state = 1

    # Regular expression to match the start of a topic line
    title_start_pattern = re.compile(r'^Tema \d+\. ', re.MULTILINE)
    # Regular expression to find a period at the end of a line
    title_end_pattern = re.compile(r'\.$')

    junk_patterns = ""

    for i, line in enumerate(lines):
        dscr(f">>> READING LINE {i}:\n{line}")

        # State 1 : Reading topic content, not doc title read
        if state == 1:
            if title_start_pattern.match(line):
                # Start the title
                title = ' '.join(line.split())

                if title_end_pattern.search(line):
                    state, header_text, junk_patterns = do_when_title_found(title)
                else:
                    state = 2
                    dscr(">>> Start of title is: " + title)
        # State 2 = Reading topic content, doc title read started
        elif state == 2:
            title += ' ' + ' '.join(line.split())
            title = title.strip()
            if title_end_pattern.search(line) or line.strip() == "":
                # End of title
                state, header_text, junk_patterns = do_when_title_found(title)
            else:
                dscr(">>> Current title is: " + title)
        # State 3 = Looking for question section header
        elif state == 3:
            tline = " ".join(line.strip().split())

            #pattern = r"^.*\d+\.1 " + TEST_QUESTION_HEADER + "$"
            #pattern = r"(^.*\d+\.1 " + TEST_QUESTION_HEADER + ")(?![^\d]*\d).*|(^" + TEST_QUESTION_HEADER + ")(?!\d).*"
            pattern = r"(^.*" + TEST_QUESTION_HEADER + ")(?![^\d]*\d).*"
            # Use re.match to check if the pattern matches the input string
            if re.match(pattern, tline):
                dscr(">>> Question header identified: " + line)
                # Change state to reading question-statements
                state = 4
        # State 4 = Looking for questions
        elif state == 4:
            # Trim line
            tline = trim_line(line)

            # Check if line must be discarded
            if must_discard_line(tline):
                dscr("¨>>> Line is discarded: " + tline)
                continue

            # Remove junk from the beginning of the line (in case it is mixed with another line)
            tline = remove_junk_text2(tline, junk_patterns,"start")
            dscr(">>> Line after reviewing start: " + tline)

            # Recheck whether line must be discarded
            if must_discard_line(tline):
                dscr("¨>>> Line is discarded " + tline)
                continue

            # Check whether question section is completed
            if SOLUTION_SECTION_HEADER in tline:
                # Registers that all questions have been read
                state = 5
                dscr(">>> Solution found")

                # Removes the whole line
                tline = ""
                ## Removes the end of the line after the solution section header instance
                #tline = tline.split(SOLUTION_SECTION_HEADER)[0]

                # Recheck whether line must be discarded
                if must_discard_line(tline):
                    tline = ""

            # If line starts with question element (statement or option), close accumulated string and rest
            s_sep = check_line_starts_like_q_elem(qcounter + 1, statement_separator, tline, False)
            if s_sep != "":
                if statement_separator is None:
                    statement_separator = s_sep
                    dscr(f">>> Statement separator is: " + statement_separator)

                # Closes current question, if exists
                close_current_question(topic)

                # Initializes current statement
                cur_q_elem = tline
                qcounter += 1
                ocounter = 0

                dscr(f">>> Question {qcounter} is started" )
                dscr(f">>> Elem for question {qcounter} is: {cur_q_elem}")
            else:
                # Check whether line follows the option pattern
                o_sep = check_line_starts_like_q_elem(ocounter + 1, option_separator, tline, True)
                if o_sep != "":
                     if option_separator is None:
                         option_separator = o_sep

                     # Stores previous statement or option, if exists
                     if ocounter == 0:
                         add_statement()
                     else:
                         add_option()

                     # Initializes current option
                     cur_q_elem = tline
                     ocounter +=1

                     dscr(f">>> New option {ocounter} for question {qcounter} is: {cur_q_elem}")
                else:
                    # Concatenate current line to accumulated
                    if tline != "":
                        # If cur_q_elem it's not empty, add space
                        if cur_q_elem != "":
                            cur_q_elem += " "
                        cur_q_elem += tline

                    # Remove junk within the accumulated, anywhere
                    cur_q_elem = remove_junk_text2(cur_q_elem, junk_patterns, "anywhere")
                    dscr(">>> Line after removing junk anywhere: " + cur_q_elem)

                    # Check whether current cummulated must be deleted
                    if must_discard_line(cur_q_elem):
                        dscr(f">>> Curr element is dropped: {cur_q_elem}")
                        cur_q_elem = ""

                    # If line is equal to text, it is dropped.
                    if cur_q_elem.strip() == header_text:
                        dscr(f">>> Text is dropped because it is equal to header: {cur_q_elem}")
                        cur_q_elem = ""
                    else:
                        dscr(f">>> Appended elem for question {qcounter}: {cur_q_elem}")

            if state == 5:
                close_current_question(topic)
                dscr(">>> ALL QUESTIONS COPIED")

        elif state == 5:
            # Program may add answers to questions
            pass
        else:
            print("Status unknown " + str(state) )

    return mcqs

def extract_questions_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        text = []
        for page_num in range(num_pages):

            page = reader.pages[page_num]
            page_text = page.extract_text()
            lines = page_text.split('\n')
            text += lines

        print('\n'.join(text))

        return extract_questions(text)

def extract_questions_from_textfile(textfile_path):
    filename = os.path.splitext(os.path.basename(textfile_path))[0]
    match = re.match(r'(\d+)', filename)
    topic = int(match.group(0)) if match else None

    with open(textfile_path, "r") as file:
        text = file.read().split('\n')
        file.close()

        return extract_questions(text, topic)

# Usage example
#pdf_path = "temario/040.pdf"
#questions = extract_questions_from_pdf(pdf_path)

textfile_path = "temario_txt/101.txt"
questions = extract_questions_from_textfile(textfile_path)

aiken_output = convert_multichoice_questions_to_aiken(questions)
print(aiken_output)

json_output = convert_multichoice_questions_to_json(questions)
print(json_output)

#for i, question in enumerate(questions):
#    print(f"Question {i + 1}:\n{question.print()}")
