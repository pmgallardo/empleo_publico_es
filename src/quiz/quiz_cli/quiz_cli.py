import re

from utils.text_utils import number_to_letter
from utils.text_utils import letter_to_number
from utils.text_utils import dbgt
from utils.text_utils import printt

# Width of the terminal where text is going to be displayed
TERM_WIDTH = 80

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
            body = empty_if_none(self.body)
            call = empty_if_none(self.call)
            source = empty_if_none(self.source)
            date = empty_if_none(self.date)
            mode = empty_if_none(self.mode)
            num = empty_if_none(self.num)
            id = self.body + ".".join([body, call, source, date, mode, num])
            return id

        def empty_if_none(self, body):
            if self.body is None:
                body = ""
            else:
                body = self.body
            return body

class QuizQuestionPart:
    def __init__(self, questions, type):
        self.questions = questions
        # type example: general or specific questions
        self.type = type

    def get_text(self):
        text = ""
        for i, q in enumerate(self.questions):
            text += "Pregunta anulada = " + str(q.is_cancelled) + "\n"
            text += "Pregunta reserva = " + str(q.is_reserve) + "\n"
            text += "Tema = " + str(q.topic) + "\n"
            text += "#" + str(i+1) + " "
            text += q.statement + "\n"
            for j, option in enumerate(q.options):
                text += number_to_letter(j+1) + ") " + option + "\n"
            text += "Respuesta correcta: " + number_to_letter(q.correct_answer_no) + "\n"
            text += "\n"
        text += "\n"
        return text

class QuizQuestionGroup:
    def __init__(self, parts):
        self.parts = parts

        self.body = None
        self.call = None
        self.source = None
        self.date = None
        self.date = None

    def append_part(self, part):
        self.parts.append(part)

    def get_text(self):
        text = ""
        for i, part in enumerate(self.parts):
            text += "PARTE " + str(i+1) + "\n\n"
            text += part.get_text()
        return text

class QuizQuestionPool:
    def __init__(self):
        self.question_groups = []

        self.load_exams()

    def load_exams(self):
        aiken_filepaths = self.scrawl_aiken_exams()
        self.parse_aiken_exams(aiken_filepaths)

    def scrawl_aiken_exams(self):
        # fullpath = "../../../data/processed/1166/test/2020/20220514/1166_2020_20220514_esp.aiken"
        # fullpath = "../../../data/processed/1166/test/2020/20220514/1166_2020_20220514_gen.aiken"
        # fullpath = "../../../data/processed/1166/test/2020/20220527/1166_2020_20220527_esp.aiken"
        # fullpath = "../../../data/processed/1166/test/2020/20220527/1166_2020_20220527_gen.aiken"
        # fullpath = "../../../data/processed/1166/test/2022/20231006/1166_2022_20231006_esp.aiken"
        # fullpath = "../../../data/processed/1166/test/2022/20231006/1166_2022_20231006_gen.aiken"
        # fullpath = "../../../data/processed/1166/test/2022/20231026/1166_2022_20231026_esp.aiken"
        # fullpath = "../../../data/processed/1166/test/2022/20231026/1166_2022_20231026_gen.aiken"

        filepaths = ["../data/processed/1166/test/2022/20231006/1166_2022_20231006_esp.aiken"]
        #filepaths = [ "../data/processed/1166/test/2022/20231026/1166_2022_20231026_gen.aiken" ]


        return filepaths

    def parse_aiken_exams(self, aiken_filepaths):
        body = "1166"
        call = "2022"
        source = "agt"
        date = "20231026"
        mode = None

        for filepath in aiken_filepaths:
            # Read file and extract questions
            file = open(filepath, "r")
            lines = file.readlines()
            file.close()

            # Parse AIKEN files
            questions = self.parse_aiken_exam(lines)
            for question in questions:
                question.body = body
                question.call = call
                question.source = source
                question.date = date
                question.mode = mode

            question_part = QuizQuestionPart(questions, "")

            # A question group could be an exam or other group of questions
            question_group = QuizQuestionGroup([question_part])
            question_group.body = body
            question_group.call = call
            question_group.source = source
            question_group.mode = mode
            question_group.date = date
            self.question_groups.append(question_group)

    def parse_aiken_exam(self, lines):
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
                            is_cancelled, is_reserve, topic, statement = self.parse_aiken_statement(cur_q_item)
                            question.is_cancelled = is_cancelled
                            question.is_reserve = is_reserve
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
                            question = QuizQuestion()
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

    def parse_aiken_statement(self, statement):
        new_statement = statement

        # Parse number
        new_statement = self.parse_number_in_statement_aiken(new_statement)
        # Parse cancelled
        isCancelled, new_statement = self.parse_cancelled_in_statement_aiken(new_statement)
        # Parse reserve
        isReserve, new_statement = self.parse_reserve_in_statement_aiken(new_statement)
        # Parse topic
        topic, new_statement = self.parse_topic_in_statement_aiken(new_statement)

        return isCancelled, isReserve, topic, new_statement

    def parse_number_in_statement_aiken(self, statement):
        pattern = r"^\d+[.)]\s*"
        # Use re.sub to replace the pattern with an empty string
        new_statement = re.sub(pattern, '', statement)
        return new_statement

    def parse_cancelled_in_statement_aiken(self, statement):
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

    def parse_reserve_in_statement_aiken(self, statement):
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

    def parse_topic_in_statement_aiken(self, statement):
        # Define the regex pattern to match [TEMA <number>]
        pattern = r'\[TEMA (\d+)\]'

        # Search for the pattern in the input string
        match = re.search(pattern, statement)

        if match:
            # Extract the number from the match
            number = int(match.group(1))

            # Remove the matched substring from the input string
            result_string = re.sub(pattern, '', statement, count=1).strip()

            return number, result_string
        else:
            # If no match is found, return None and the original string
            return None, statement

    def get_quiz_by_exam(self, body_id, call, mode, date):
        quiz = AGEQuiz()

        for q_group in self.question_groups:
            q_group

        return quiz

    def get_quiz_by_topic(self, body, topic):
        quiz_parts = []
        quiz_questions = []

        # Add questions of topics from pool that matches selection
        for q_groups in self.question_groups:
            if body == q_groups.body:
                for part in q_groups.parts:
                    for k, q in enumerate(part.questions):
                        if q.topic is not None:
                            if topic == q.topic:
                                quiz_questions.append(q)

        part = QuizQuestionPart(quiz_questions, None)
        quiz_parts.append(part)
        q_group =QuizQuestionGroup(quiz_parts)
        quiz = AGEQuiz(q_group)
        return quiz

    def get_quiz_by_block(self, body_id, block):
        quiz = AGEQuiz()
        return quiz

class AGEQuiz:
    def __init__(self, q_group):
        self.q_group = q_group

    def get_text_questions(self):
        return self.q_group.get_text()

        # option_char = ")"
        #
        # text_qs = ""
        # for i, question in enumerate(self.questions):
        #     # text_qs += "STATEMENT "
        #     text_qs += "#" + str(i + 1) + " "
        #     text_qs += question.statement + "\n"
        #     for j, option in enumerate(question.options):
        #         text_qs += self.number_to_letter(j + 1) + option_char + " "
        #         text_qs += option + "\n"
        #
        #     text_qs += "ANSWER: "
        #     answer = question.correct_answer_no
        #     if answer != "":
        #         text_qs += self.number_to_letter(answer).upper()
        #     text_qs += "\n"
        #     if i < len(self.questions) - 1:
        #         text_qs += "\n"
        # return text_qs

    def play(self):
        # init counters
        num_cancelled_qs = []
        num_reserve_qs = []
        num_correct_answers = []
        num_incorrect_answers = []


        for i, part in enumerate(self.q_group.parts):
            # init counters
            num_cancelled_qs.append(0)
            num_reserve_qs.append(0)
            num_correct_answers.append(0)
            num_incorrect_answers.append(0)

            questions = part.questions

            printt("PARTE " + str(i+1) + "\n")

            for j, question in enumerate(questions):
                # Loop all questions
                    # Check whether question is cancelled, has no answer os is reserve
                    if question.is_cancelled:
                        num_cancelled_qs[i] += 1
                        printt("PREGUNTA ANULADA")
                    else:
                        if not question.has_answer:
                            num_cancelled_qs[i] += 1
                            printt("PREGUNTA SIN RESPUESTA, SE CONSIDERA NULA")
                        elif question.is_reserve:
                            num_reserve_qs[i] += 1

                    # Display statement
                    printt("\nPREGUNTA " + str(j + 1) + "/" + str(len(questions)))

                    # Display options
                    printt(question.get_statement_and_options_text())

                    if question.has_answer:
                        # Prompt answer
                        player_option = input("Introduzca respuesta [A-D]: ")

                        player_option_no = letter_to_number(player_option)
                        correct_option_no = question.correct_answer_no
                        # Check answer
                        if player_option_no == correct_option_no:
                            is_useless_reserve = question.is_reserve and (num_cancelled_qs[i] < num_reserve_qs[i])

                            if not (is_useless_reserve or question.is_cancelled):
                                # Add correct answer
                                num_correct_answers[i] += 1
                            printt("¡Correcto!")
                        else:
                            is_useless_reserve = question.is_reserve and (num_cancelled_qs[i] < num_reserve_qs[i])

                            if not (is_useless_reserve or question.is_cancelled):
                                # Add incorrect answer
                                num_incorrect_answers[i] += 1

                            correct_option_letter = number_to_letter(correct_option_no).upper()
                            printt("Incorrecto. La respuesta correcta era " + correct_option_letter + ".")

        # Display total result

        # values published after the correction of each test
        #min_direct_score = 39 # 2022 L ord
        #min_direct_score = 39 # 2022 L ext
        #min_direct_score = 37.2 # 2022 L ord
        #min_direct_score = 39 # 2022 L ext
        #min_direct_score = 9  # 2022 L ext ESP
        #min_direct_score = 30  # 2022 L ext GEN



        for i, part in enumerate(self.q_group.parts):

            print("RESULTADOS PARTE " + str(i+1) + "\n")

            questions = part.questions

            # maximum direct score should remove cancelled answers
            num_total_qs = len(questions)
            num_used_reserved_qs = self.calc_num_used_reserve_qs(num_reserve_qs[i], num_cancelled_qs[i])
            num_valid_qs = self.calc_num_valid_qs(num_total_qs, num_reserve_qs[i], num_cancelled_qs[i])
            max_direct_score = num_valid_qs

            #prop_min_direct_score = min_direct_score / max_direct_score
            prop_min_direct_score = 0.30
            min_direct_score = prop_min_direct_score * max_direct_score

            # Score calculation
            direct_score = num_correct_answers[i] - (num_incorrect_answers[i] / 3)
            prop_direct_score = direct_score / max_direct_score
            ## If direct score is negative, it is converted to zero
            #if direct_score < 0:
            #    direct_score = 0

            direct_score_2dec = "{:.2f}".format(round(direct_score, 2))
            per_direct_score_2dec = "{:.2f}".format(round(prop_direct_score*100, 2))
            per_min_direct_score_2dec = "{:.2f}".format(round(prop_min_direct_score*100, 2))

            unanswered_questions = num_valid_qs - num_correct_answers[i] - num_incorrect_answers[i]
            printt("\n¡Fin del exámen!\n")
            printt(f"Preguntas totales: {num_total_qs}")
            printt(f"Preguntas anuladas: {num_cancelled_qs[i]}")
            printt(f"Preguntas de reserva (usadas y sin usar): {num_reserve_qs[i]}")
            printt(f"Preguntas de reserva usadas: {num_used_reserved_qs}")
            printt(f"Preguntas totales válidas: {num_valid_qs}")
            printt(f"Preguntas acertadas: {num_correct_answers[i]}")
            printt(f"Preguntas erradas: {num_incorrect_answers[i]}")
            printt(f"Preguntas sin contestar: {unanswered_questions}\n")

            printt(f"Tu puntuación directa: {direct_score_2dec}")
            printt(f"Has obtenido un {per_direct_score_2dec} % de la máxima puntuación respecto al {per_min_direct_score_2dec} % mínimo exigido.")

            if direct_score < min_direct_score:
                print("Lo siento, no habrías aprobado el ejercicio.")
            else:
                print("Enhorabuena, ¡habrías aprobado el ejercicio!")

            ## Calculation of transformed score
            #if direct_score < min_direct_score:
            #    transformed_score = max_transformed_score / 2 * direct_score / min_direct_score
            #else:
            #    transformed_score = max_transformed_score / 2 * (1 + (direct_score - min_direct_score) / (max_direct_score - min_direct_score)

    def calc_num_used_reserve_qs(self, reserve_questions, cancelled_questions):
        if reserve_questions <= cancelled_questions:
            return reserve_questions
        else:
            return cancelled_questions

    def calc_num_valid_qs(self, num_total_qs, num_reserve_qs, num_cancelled_qs):
        if num_reserve_qs >= num_cancelled_qs:
            # Reserved are ignored as they have substituted all cancelled questions
            return num_total_qs - num_reserve_qs
        else:
            # Cancelled are ignored as the reserved questions are less
            return num_total_qs - num_cancelled_qs

class QuizConf:
    def __init__(self):
        self.body_id = ""
        self.practice_type = ""
        self.exam_no = 0
        self.topic_no = 0

        self.dbgt_on = False

class Quiz:
    def __init__(self):
        self.conf = QuizConf()
        self.questions = []

        self.dbgt_on = False

    def get_text_questions(self):
        option_char = ")"

        text_qs = ""
        for i, question in enumerate(self.questions):
            # text_qs += "STATEMENT "
            text_qs += "#" + str(i + 1) + " "
            text_qs += question.statement + "\n"
            for j, option in enumerate(question.options):
                text_qs += self.number_to_letter(j + 1) + option_char + " "
                text_qs += option + "\n"

            text_qs += "ANSWER: "
            answer = question.correct_answer_no
            if answer != "":
                text_qs += self.number_to_letter(answer).upper()
            text_qs += "\n"
            if i < len(self.questions) - 1:
                text_qs += "\n"
        return text_qs

    def dbgt(self, text):
        if self.dbgt_on:
            print(text)

    def shrink_text(self, text, width, hanging_width=None):
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

    def printt(self, text):
        print(self.shrink_text(text, TERM_WIDTH))

    def parse_aiken_quiz(self, lines):
        # Initialize question parsing
        question = None
        option_count = 0
        cur_q_item = ""
        # Parse questions
        for line in lines:
            # Ignore empty lines between questions
            if line != "" or question is not None:
                # If question is not started
                if question is None:
                    question = QuizQuestion()
                    cur_q_item = line.rstrip()
                    self.dbgt(" > Save initial text: " + cur_q_item)
                else:
                    # Check if it is the next expected option (a), b., etc.) or an answer pattern
                    next_option_letter = self.number_to_letter(option_count + 1)
                    lower_nol = next_option_letter.lower()
                    upper_nol = next_option_letter.upper()

                    # option_pattern = rf"^{re.escape(next_option_letter)}[.)] "
                    option_pattern = rf"^[{re.escape(upper_nol)}{re.escape(lower_nol)}][.)] "
                    answer_pattern = rf"^{re.escape('ANSWER')}:"

                    if re.match(option_pattern, line) or re.match(answer_pattern, line):
                        # Save previous item element, whether it is a statement or question
                        if question.has_statement():
                            question.append_option(cur_q_item)
                            self.dbgt(" > Append option: " + cur_q_item)
                        else:
                            question.set_statement(cur_q_item)
                            self.dbgt(" > Save statement: " + cur_q_item)

                        # If it matches answer pattern
                        answer_match = re.match(answer_pattern, line)
                        if answer_match:
                            # Get the answer value, removing the end of line character
                            line_wo_answer_head = re.sub(answer_pattern, '', line).strip()
                            # If there is an answer
                            if line_wo_answer_head != "":
                                correct_answer_no = self.letter_to_number(line_wo_answer_head)
                                question.set_correct_answer_no(correct_answer_no)
                            self.questions.append(question)

                            # Initializes new question
                            question = QuizQuestion()
                            option_count = 0
                            cur_q_item = ""
                        # If it matches option pattern
                        else:
                            # Get option letter from read line
                            # option_letter = answer_match.group()[:-2]

                            line_wo_option_head = re.sub(option_pattern, '', line).rstrip()
                            cur_q_item = line_wo_option_head

                            option_count += 1
                            self.dbgt(" > Save option text: " + cur_q_item)
                    else:
                        cur_q_item += line.rstrip()
                        self.dbgt(" > Save question item text: " + line.rstrip())

    def load_questions(self):
        # Check quiz configuration
        body_id = self.conf.body_id
        filepaths = []

        if self.conf.practice_type == 'E':
            # Get call ID
            call_id = "2022"
            # Get exam ID
            exam_id = "20230626"
            path = "../../../data/processed/" + str(body_id) + "/test/" + call_id + exam_id

            path = "../../../data/processed/1166/test/2022/20230626/"

            filename = "1166_2022_20230606_esp.aiken"
            # filenamee = "1166_2022_20230606_gen.aiken"
            # filenamee = "1166_2022_20230626_gen.aiken"
            # filenamee = "1166_2022_20230626_esp.aiken"
            #filepaths.append(path + filename)

            fullpath = path + filename

            #fullpath = "../../../data/processed/1166/test/2020/20220514/1166_2020_20220514_esp.aiken"
            #fullpath = "../../../data/processed/1166/test/2020/20220514/1166_2020_20220514_gen.aiken"
            #fullpath = "../../../data/processed/1166/test/2020/20220527/1166_2020_20220527_esp.aiken"
            #fullpath = "../../../data/processed/1166/test/2020/20220527/1166_2020_20220527_gen.aiken"
            fullpath = "../../../data/processed/1166/test/2022/20231006/1166_2022_20231006_esp.aiken"
            #fullpath = "../../../data/processed/1166/test/2022/20231006/1166_2022_20231006_gen.aiken"
            #fullpath = "../../../data/processed/1166/test/2022/20231026/1166_2022_20231026_esp.aiken"
            #fullpath = "../../../data/processed/1166/test/2022/20231026/1166_2022_20231026_gen.aiken"
            filepaths.append(fullpath)
        elif self.conf.practice_type == 'T':
            # Loop folders within the body

            # Loop files within folders
            path = "../../../data/processed/1166/test/2022/20230626/"
            filename = "1166_2022_20230626_gen.aiken"
            filepaths.append(path + filename)

        for filepath in filepaths:
            # Read file and extract questions

            file = open(filepath, "r")
            lines = file.readlines()
            file.close()

        # Parse AIKEN files
        self.parse_aiken_quiz(lines)

        # Filter valid questions only
        vquestions = []
        for question in self.questions:
            # Filter questions with answers
            if question.has_answer:
                # Check whether question has been cancelled

                # Add questions
                vquestions.append(question)
        self.questions = vquestions

    def play(self):
        # for each question
        # Display statement

        # Display options

        # Prompt answer

        # Check answer

        # Display total result


        self.load_questions()

        # values published after the correction of each test
        #min_direct_score = 39 # 2022 L ord
        #min_direct_score = 39 # 2022 L ext
        #min_direct_score = 37.2 # 2022 L ord
        #min_direct_score = 39 # 2022 L ext
        #min_direct_score = 9  # 2022 L ext ESP
        min_direct_score = 30  # 2022 L ext GEN

        # calculated values
        # maximum direct score should remove cancelled answers
        num_total_questions = len(self.questions)
        max_direct_score = num_total_questions
        prop_min_direct_score = min_direct_score / max_direct_score

        correct_answers = 0
        incorrect_answers = 0

        # Loop valid questions
        for i, question in enumerate(self.questions):

            # Loop all questions
            if question.has_answer():
                self.printt("\nPREGUNTA " + str(i+1) + "/" + str(len(self.questions)))

                self.printt(question.get_statement_and_options_text())
                player_option = input("Introduzca respuesta [A-D]: ")

                player_option_no = self.letter_to_number(player_option)
                correct_option_no = question.correct_answer_no
                if player_option_no == correct_option_no:
                    # Add correct answer
                    correct_answers += 1
                    self.printt("¡Correcto!")
                else:
                    # Add incorrect answer
                    incorrect_answers += 1

                    correct_option_letter = self.number_to_letter(correct_option_no).upper()
                    self.printt("Incorrecto. La respuesta correcta era " + correct_option_letter + ".")

        # Score calculation
        direct_score = correct_answers - (incorrect_answers / 3)
        prop_direct_score = direct_score / max_direct_score
        ## If direct score is negative, it is converted to zero
        #if direct_score < 0:
        #    direct_score = 0

        direct_score_2dec = "{:.2f}".format(round(direct_score, 2))
        per_direct_score_2dec = "{:.2f}".format(round(pro_direct_score*100, 2))
        per_min_direct_score_2dec = "{:.2f}".format(round(pro_min_direct_score*100, 2))

        unanswered_questions = num_total_questions - correct_answers - incorrect_answers
        self.printt("\n¡Fin del exámen!\n")
        self.printt(f"Preguntas totales válidas: {num_total_questions}")
        self.printt(f"Preguntas acertadas: {correct_answers}")
        self.printt(f"Preguntas erradas: {incorrect_answers}")
        self.printt(f"Preguntas sin contestar: {unanswered_questions}\n")

        self.printt(f"Tu puntuación directa: {direct_score_2dec}")
        self.printt(f"Has obtenido un {per_direct_score_2dec} % de la máxima puntuación respecto al {per_min_direct_score_2dec} % mínimo exigida.")

        if direct_score < min_direct_score:
            print("Lo siento, no habrías aprobado el ejercicio.")
        else:
            print("Enhorabuena, ¡habrías aprobado el ejercicio!")

        ## Calculation of transformed score
        #if direct_score < min_direct_score:
        #    transformed_score = max_transformed_score / 2 * direct_score / min_direct_score
        #else:
        #    transformed_score = max_transformed_score / 2 * (1 + (direct_score - min_direct_score) / (max_direct_score - min_direct_score)


def print_title():
    with open('quiz/quiz_cli/title.txt', 'r') as file:
        # Read the contents of the file
        print(file.read() + '\n')


def select_and_play_quizzes(question_pool):
    # quiz loop
    user_wants_another_quiz = True
    while user_wants_another_quiz:
        # Propose default configuration
        default_conf_input = input("¿Quieres comenzar con la configuración por defecto? [S/N] (defecto: S): ")

        if default_conf_input == 'S' or default_conf_input == '':
            pass
            # # Load default configuration
            # quiz.conf.body_id = 1166
            # quiz.conf.practice_type = 'E'
            # quiz.conf.exam_no = 1
        else:
            # Read all Spain's AGE bodies

            # Prompt body ID
            body_id = input("Introduza código de cuerpo: (defecto: 1166)")
            if quiz.conf.body_id == '':
                quiz.conf.body_id = 1166

            # Given the body path, loop all files containing .aiken extension

            # Read list topics from latest call

            # Prompt practice type
            practice_type = input("Indique si quiere practicar ejercicio [E] o tema [T]: (defecto: E)")
            if practice_type == '':
                practice_type = 'E'

            if practice_type == 'E':
                # List available exams

                # Prompt exam ordinal number
                exam_no = input("Introduzca número de exámen: (defecto: el primero): ")

            elif practice_type == 'T':
                # List topics

                # Prompt topic number
                pass
                topic_no = input("Introduzca tema: (defecto: 1): ")

            else:
                print("\nPráctica desconocida")

        another_exam_input = input("¿Quieres realizar otro exámen? [S/N] (defecto S): ").strip().upper()
        if another_exam_input == 'N':
            user_wants_another_quiz = False



def select():
    # Propose default configuration
    quiz = Quiz()

    default_conf_input = input("¿Quieres comenzar con la configuración por defecto? [S/N] (defecto: S): ")

    if default_conf_input == 'S' or default_conf_input == '':
        # Load default configuration
        quiz.conf.body_id = 1166
        quiz.conf.practice_type = 'E'
        quiz.conf.exam_no = 1
    else:
        # Read all Spain's AGE bodies

        # Prompt body ID
        body_id = input("Introduza código de cuerpo: (defecto: 1166)")
        if quiz.conf.body_id == '':
            quiz.conf.body_id = 1166

        # Given the body path, loop all files containing .aiken extension

        # Read list topics from latest call

        # Prompt practice type
        practice_type = input("Indique si quiere practicar ejercicio [E] o tema [T]: (defecto: E)")
        if practice_type == '':
            practice_type = 'E'

        if practice_type == 'E':
            # List available exams

            # Prompt exam ordinal number
            exam_no = input("Introduzca número de exámen: (defecto: el primero): ")

        elif practice_type == 'T':
            # List topics

            # Prompt topic number
            pass
            topic_no = input("Introduzca tema: (defecto: 1): ")

        else:
            print("\nPráctica desconocida")

def play():

    # Ask questions
    quiz.play()

def quiz_run():

    # Question pool load
    question_pool = QuizQuestionPool()

    #exam = question_pool.question_groups[0]
    #printt(exam.get_text())

    print_title()

    # Quiz selection


    # Quiz preparation

    body = "1166"

    call = "2022"
    mode = "l"
    date = "20231006"

    topic_no = 108

    block = "e"

    # quiz = question_pool.get_quiz_by_exam(body_id, call, mode, date)
    quiz = question_pool.get_quiz_by_topic(body, topic_no)
    # quiz = question_pool.get_quiz_by_block(body_id, block)

    printt(quiz.get_text_questions())

    # Call quiz
    quiz.play()

    #select_and_play_quizzes(question_pool)

    # Old functionality
    # Display title
    #print_title()

    #select()
    #play()

    # Ask if it wants to perform another test


def main():
    quiz_run()

if __name__ == "__main__":
    main()









