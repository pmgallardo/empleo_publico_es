import re
import yaml
import datetime
from datetime import datetime

import os
import glob

def dbgt(text):
    if False:
        print(text)

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



class QuizQuestion:
    def __init__(self):
        self.statement = ""
        self.options = []
        # ordinal that corresponds to the correct answer, according to order (1 = A, etc.)
        self.correct_answer_no = 0

    def set_statement(self, statement):
        self.statement = statement

    def set_correct_answer_no(self, correct_answer_no):
        self.correct_answer_no = correct_answer_no

    def append_option(self, option):
        self.options.append(option)

    def has_statement(self):
        return bool(self.statement)

    def has_answer(self):
        return self.correct_answer_no > 0

    def get_statement_and_options_text(self):
        text = self.statement + "\n\n"
        for i, option in enumerate(self.options):
            opt_letter = number_to_letter(i+1)
            text += f"{opt_letter}) {option} \n"
        return text

    def to_dict(self):
        return {
            'enunciado': str(self.statement),
            'respuestas': [str(option) for option in self.options],
            'respuesta_correcta': self.correct_answer_no
        }

class AGEQuizQuestion(QuizQuestion):
    def __init__(self):
        super().__init__()

        # AGT specific fields
        self.body = ""
        self.call = ""
        self.source = ""
        self.date = ""
        self.mode = ""
        self.num = ""
        self.is_cancelled = None
        self.is_reserve = None
        self.topic_call = ""
        self.topic = ""
        # Block is used when it cannot be inferred from topic
        self.block = ""

    def set_body(body):
        self.body = body

    def set_date(date):
        self.date = date

    def set_call(call):
        self.call = call

    def get_id(self):
        body = self.empty_if_none(self.body)
        call = self.empty_if_none(self.call)
        source = self.empty_if_none(self.source)
        date = self.empty_if_none(self.date)
        mode = self.empty_if_none(self.mode)
        num = self.empty_if_none(self.num)
        id = self.body + ".".join([body, call, source, date, mode, num])
        return id

    def empty_if_none(self, body):
        if self.body is None:
            body = ""
        else:
            body = self.body
        return body

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            'anulada': self.is_cancelled if self.is_cancelled is not None else False,
            'reserva': self.is_reserve if self.is_reserve is not None else False,
            'convocatoria_tema': str(self.topic_call) if self.topic_call is not None else "",
            'tema': str(self.topic) if self.topic is not None else "",
        })
        return base_dict


def parse_aiken_exam(lines):
    # Initialize question parsing
    questions = []
    question = None
    option_count = 0
    cur_q_item = ""
    # Parse questions
    for i, line in enumerate(lines):
        # Ignore empty lines between questions
        if line != "" or question is not None:
            # If question is not started
            if question is None:
                question = AGEQuizQuestion()
                question.num = i+1
                cur_q_item = line.rstrip()
                dbgt(" > Save initial text: " + cur_q_item)
            else:
                # Check if it is the next expected option (a), b., etc.) or an answer pattern
                next_option_letter = number_to_letter(option_count + 1)
                lower_nol = next_option_letter.lower()
                upper_nol = next_option_letter.upper()

                # option_pattern = rf"^{re.escape(next_option_letter)}[.)] "
                option_pattern = rf"^[{re.escape(upper_nol)}{re.escape(lower_nol)}][.)] "
                answer_pattern = rf"^{re.escape('ANSWER')}:"

                if re.match(option_pattern, line) or re.match(answer_pattern, line):
                    # Save previous item element, whether it is a statement or question
                    if question.has_statement():
                        question.append_option(cur_q_item)
                        dbgt(" > Append option: " + cur_q_item)
                    else:
                        dbgt(" > Full raw statement before parsing: " + cur_q_item)

                        # Parse statement
                        is_cancelled, is_reserve, topic_call, topic, statement = parse_aiken_statement(cur_q_item)
                        question.is_cancelled = is_cancelled
                        question.is_reserve = is_reserve
                        question.topic_call = topic_call
                        question.topic = topic
                        question.statement = statement
                        dbgt(" > Save statement: " + statement)

                    # If it matches answer pattern
                    answer_match = re.match(answer_pattern, line)
                    if answer_match:
                        # Get the answer value, removing the end of line character
                        line_wo_answer_head = re.sub(answer_pattern, '', line).strip()
                        # If there is an answer
                        if line_wo_answer_head != "":
                            correct_answer_no = letter_to_number(line_wo_answer_head)
                            question.set_correct_answer_no(correct_answer_no)
                        questions.append(question)

                        # Initializes new question
                        question = AGEQuizQuestion()
                        option_count = 0
                        cur_q_item = ""
                    # If it matches option pattern
                    else:
                        # Get option letter from read line
                        # option_letter = answer_match.group()[:-2]

                        line_wo_option_head = re.sub(option_pattern, '', line).rstrip()
                        cur_q_item = line_wo_option_head

                        option_count += 1
                        dbgt(" > Save option text: " + cur_q_item)
                else:
                    cur_q_item += line.rstrip()
                    dbgt(" > Save question item text: " + line.rstrip())

    return questions

def parse_aiken_statement(statement):
    new_statement = statement

    # Parse number
    new_statement = parse_number_in_statement_aiken(new_statement)
    # Parse cancelled
    isCancelled, new_statement = parse_cancelled_in_statement_aiken(new_statement)
    # Parse reserve
    isReserve, new_statement = parse_reserve_in_statement_aiken(new_statement)
    # Parse topic
    q_topic_call, q_topic, new_statement = parse_topic_in_statement_aiken(new_statement)

    return isCancelled, isReserve, q_topic_call, q_topic, new_statement

def parse_number_in_statement_aiken(statement):
    pattern = r"^\d+[.)]\s*"
    # Use re.sub to replace the pattern with an empty string
    new_statement = re.sub(pattern, '', statement)
    return new_statement

def parse_cancelled_in_statement_aiken(statement):
    substring = "[ANULADA]"

    # Escape the substring if necessary for regex
    escaped_substring = re.escape(substring)

    # Create the regex pattern to match the substring and the following spaces
    pattern = r'{}(\s*)'.format(escaped_substring)

    # Search for the pattern in the input string
    match = re.search(pattern, statement)

    if match:
        # Remove the first occurrence of the substring and any following spaces
        result = re.sub(pattern, '', statement, count=1)
        return True, result
    else:
        # If the substring is not found, return False and the original string
        return False, statement

def parse_reserve_in_statement_aiken(statement):
    substring = "[RESERVA]"

    # Escape the substring if necessary for regex
    escaped_substring = re.escape(substring)

    # Create the regex pattern to match the substring and the following spaces
    pattern = r'{}(\s*)'.format(escaped_substring)

    # Search for the pattern in the input string
    match = re.search(pattern, statement)

    if match:
        # Remove the first occurrence of the substring and any following spaces
        result = re.sub(pattern, '', statement, count=1)
        return True, result
    else:
        # If the substring is not found, return False and the original string
        return False, statement

def parse_topic_in_statement_aiken(statement):
    # Define the regex pattern to match [TEMA <call>.<topic number>]
    pattern = r'\[TEMA="(\d+\.\d+)"\]'

    # Search for the pattern in the input string
    match = re.search(pattern, statement)

    if match:
        # Extract the full topic id from the match
        full_topic_id = match.group(1)
        q_call, q_topic = full_topic_id.split('.')

        # Remove the matched substring from the input string
        result_string = re.sub(pattern, '', statement, count=1).strip()

        return q_call, q_topic, result_string
    else:
        # If no match is found, return None and the original string
        return None, None, statement


def parse_aiken_file(input_fullpath):
    with open(input_fullpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    questions = parse_aiken_exam(lines)

    return questions

def browse_aiken_fullpaths(root_folder):
    body = "1166"

    # Step 1: Loop through all folders in the root folder (Level 1)
    for level1_folder in os.listdir(root_folder):
        level1_path = os.path.join(root_folder, level1_folder)
        if os.path.isdir(level1_path):  # Check if it's a folder
            print(f"Level 1 folder: {level1_folder}")
            source = level1_folder

            # Step 2: Loop through all folders in the Level 1 folder (Level 2)
            for level2_folder in sorted(os.listdir(level1_path)):
                level2_path = os.path.join(level1_path, level2_folder)
                if os.path.isdir(level2_path):  # Check if it's a folder
                    print(f"  Level 2 folder: {level2_folder}")
                    call = level2_folder

                    # Step 3: Loop through all folders in the Level 2 folder (Level 3)
                    for i, level3_folder in enumerate(sorted(os.listdir(level2_path))):
                        call_exam_count = i+1

                        level3_path = os.path.join(level2_path, level3_folder)
                        if os.path.isdir(level3_path):  # Check if it's a folder
                            print(f"    Level 3 folder: {level3_folder}")

                            input_fullpaths = []
                            parts_data = []
                            exam_date = datetime.strptime(level3_folder, "%Y%m%d")

                            # Step 4: Find all '.aiken' files in Level 3 folder
                            aiken_files = glob.glob(os.path.join(level3_path, "*.aiken"))
                            for aiken_file in sorted(aiken_files):
                                print(f"      Found .aiken file: {os.path.basename(aiken_file)}")

                                part_title = ""
                                input_fullpath = os.path.abspath(aiken_file)
                                filename_elems = os.path.basename(aiken_file).split('_')
                                if len(filename_elems) == 6:
                                    if filename_elems[5] == "e":
                                        part_title = "Parte temas especifícos"
                                    elif filename_elems[5] == 'g':
                                        part_title = "Parte temas generales"
                                #input_fullpaths.append(input_fullpath)
                                #part_titles.append(part_title)

                                part_data = {
                                    "input_fullpath": input_fullpath,
                                    "part_title": part_title
                                }
                                parts_data.append(part_data)

                            # Parse exams with all files within folder

                            parsed_exam = parse_exam(body, source, call, exam_date, call_exam_count, parts_data)

                            output_filepath = ''
                            output_filename = '1.yaml'
                            # output_fullpath = output_filepath + '/' + output_filename
                            output_fullpath = level3_path + '/' + output_filename

                            exam_to_yaml(parsed_exam, output_fullpath)

def parse_parts(parts_data):
    parts = []
    for i, part_data in enumerate(parts_data):
        input_fullpath = part_data["input_fullpath"]
        part_title = part_data["part_title"]

        # read and parse aiken file
        part_questions = parse_aiken_file(input_fullpath)

        part = {
            "numero_parte": i+1,
            "titulo_parte": part_title,
            "preguntas": part_questions
        }
        parts.append(part)

    return parts

def parse_exam(body, source, call, exam_date, call_exam_count, parts_data):
    if call_exam_count == 1:
        ordinareness = 'ordinario'
    else:
        ordinareness = 'extraordinario'

    exam_parts = parse_parts(parts_data)

    exam = {
        'cuerpo': str(body),
        'convocatoria': str(call),
        'fecha': exam_date,
        'fuente': source,
        'normalidad': ordinareness,
    }

    if source == "age":
        promocion_interna = {
            "modalidad": "i",
            "puntuacion_minima_directa": 0.0,
            "puntuacion_maxima_directa": 0.0
        }

        ingreso_libre  = {
            "modalidad": "p",
            "puntuacion_minima_directa": 0.0,
            "puntuacion_maxima_directa": 0.0
        }

        exam['puntuaciones'] = [promocion_interna, ingreso_libre]

    exam['partes'] = exam_parts

    return { 'exam' : exam }

def exam_to_yaml(exam2, output_fullpath):
    # Convert all exam parts (questions) to dictionaries
    exam = exam2['exam']

    for part in exam['partes']:
        questions = part['preguntas']
        for j, question in enumerate(questions):
            questions[j] = question.to_dict()

    # write to file
    with open(output_fullpath, 'w', encoding='utf-8') as f:
        yaml.dump(exam2, f, allow_unicode=True, sort_keys=False)


start_browse_path = '../../../data/processed/1166/test/'
folders = browse_aiken_fullpaths(start_browse_path)


# input_filepath = '../../../data/processed/1166/test/age/2010/20100101'
# input_filename = '1166_age_2010_20100101.aiken'
# # input_filename = 'test.aiken'
# input_fullpaths = [ input_filepath + '/' + input_filename ]



























