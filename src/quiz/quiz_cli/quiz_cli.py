import re
import glob
import os
import csv
from pathlib import Path

from utils.text_utils import number_to_letter
from utils.text_utils import letter_to_number
from utils.text_utils import dbgt
from utils.text_utils import printt
from utils.text_utils import count_instances

from src.quiz.quiz_cli.quiz_cli_shared import num_questions

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

class QuizQuestionPart:
    def __init__(self, questions, type):
        self.questions = questions
        # type example: general or specific questions
        self.type = type

    def get_text(self):
        text = ""
        if len(self.questions) > 0:
            for i, q in enumerate(self.questions):
                text += "Pregunta anulada = " + str(q.is_cancelled) + "\n"
                text += "Pregunta reserva = " + str(q.is_reserve) + "\n"
                text += "Tema = " + str(q.topic) + "\n"
                text += "#" + str(i+1) + " "
                text += q.statement + "\n"
                for j, option in enumerate(q.options):
                    text += number_to_letter(j+1) + ") " + option + "\n"
                if q.correct_answer_no != 0:
                    text += "Respuesta correcta: " + number_to_letter(q.correct_answer_no) + "\n"
                else:
                    text += "No hay respuesta para esta pregunta" + "\n"
                text += "\n"
            text += "\n"
        else:
            printt("Esta parte no tiene ninguna pregunta.")
        return text


class QuizQuestionGroup:
    def __init__(self, parts=None):
        if parts is None:
            self.parts = []
        else:
            self.parts = parts

        self.body = None
        self.source = None
        self.call = None
        self.mode = None
        self.date = None

    def append_part(self, part):
        self.parts.append(part)

    def get_text(self):
        text = ""
        if len(self.parts) > 0:
            for i, part in enumerate(self.parts):
                text += "PARTE " + str(i+1) + "\n"
                text += part.get_text()
        else:
            printt("ERROR: el exámen explorado no tiene partes.")
        return text

class QuizQuestionPool:
    def __init__(self, assessment_id):
        # A quiz question group can be assimilated generally as an "exam".
        self.question_groups = []

        self.load_exams(assessment_id)

    def get_text(self):
        text = ""
        for i, part in enumerate(self.question_groups):
            text += "EXAMEN " + str(i+1) + "\n\n"
            text += part.get_text()
        return text

    def read_csv(self, path):
        with open(path, mode='r') as file:
            reader = csv.reader(file, delimiter=',')

            # Skip the first line (header)
            next(reader)

            # Read the remaining lines into a list
            return [line for line in reader]

    def load_exams(self, assessment_id):
        # This function could be separated into crawl_exams() and parse_exams

        # Read exam overview file (exam.csv)
        exam_lines = self.read_csv("../data/processed/" + assessment_id + "/test/exam.csv")

        # Obtain extra exam modality information (exam_mod.csv)
        if assessment_id == "es_age_1166":
            exam_mod_lines = self.read_csv("../data/processed/" + assessment_id + "/test/exam_mod.csv")

        for exam_line in exam_lines:
            body_id = exam_line[0]

            # Read basic data of exam
            source_id = exam_line[1]
            call_id = exam_line[2]
            exam_date = exam_line[3]
            mode = exam_line[4]

            # Generate exam folder path
            exam_folder_path = "../data/processed/"
            exam_folder_path += body_id + "/"
            exam_folder_path += "test/"
            exam_folder_path += source_id + "/"
            exam_folder_path += call_id + "/"
            if mode != "":
                exam_folder_path += mode + "/"
            exam_folder_path += exam_date + "/"


            # Identify exam files within exam folder
            # Get the full paths of all .aiken files in the directory
            exam_file_paths = glob.glob(os.path.join(exam_folder_path, "*.aiken"))
            # Sort the files alphanumerically (glob.glob() already returns sorted results)
            exam_file_paths = sorted(exam_file_paths)

            # Only if files are found, create and feed QuizGroup/QuizExam instance
            if exam_file_paths:
                # Create QuizGroup
                # A question group could be an exam or other group of questions
                question_group = QuizQuestionGroup()
                question_group.body = body_id
                question_group.call = call_id
                question_group.source = source_id
                question_group.mode = mode
                question_group.date = exam_date

                # PENDING Add extra exam modality information (like score), if available
                # exam_mod_lines

                # Read and parse each exam file
                for exam_file_path in exam_file_paths:

                    # Read exam and extract questions
                    file = open(exam_file_path, "r")
                    lines = file.readlines()
                    file.close()

                    # Parse exam file
                    questions = self.parse_aiken_exam(lines)

                    if questions:
                        for question in questions:
                            question.body = body_id
                            question.source = source_id
                            question.call = call_id
                            question.date = exam_date

                        # Create QuizPart and add question
                        part = QuizQuestionPart(questions, "")
                        # Add QuizPart to QuizGroup
                        question_group.append_part(part)

                # Add question groups to quiz pool
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
                        # Save previous item element, whether it is a statement or option
                        if question.has_statement():
                            question.append_option(cur_q_item)
                            dbgt(" > Append option: " + cur_q_item)
                        else:
                            dbgt(" > Full raw statement before parsing: " + cur_q_item)

                            # Parse statement
                            is_cancelled, is_reserve, topic_call, topic, statement = self.parse_aiken_statement(cur_q_item)
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

    def parse_aiken_statement(self, statement):
        new_statement = statement

        # Parse number
        new_statement = self.parse_number_in_statement_aiken(new_statement)
        # Parse cancelled
        isCancelled, new_statement = self.parse_cancelled_in_statement_aiken(new_statement)
        # Parse reserve
        isReserve, new_statement = self.parse_reserve_in_statement_aiken(new_statement)
        # Parse topic
        q_topic_call, q_topic, new_statement = self.parse_topic_in_statement_aiken(new_statement)

        return isCancelled, isReserve, q_topic_call, q_topic, new_statement

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

    def list_question_groups(self):
        text = ""
        for q_group in self.question_groups:
            text += f"{q_group.body} {q_group.call} {q_group.source} {q_group.date}\n"
        return text

    def get_quiz_by_exam(self, body, call, source, mode, date):
        # Browse all exams and see which one matches.
        for q_group in self.question_groups:
            if q_group.body is not None and q_group.call is not None and q_group.source is not None and q_group.date is not None:
                if mode == "":
                    if str(body) == str(q_group.body) and str(call) == str(q_group.call) and str(source) == str(q_group.source) and str(date) == str(q_group.date):
                        quiz_group = q_group

                        quiz = AGEQuiz(q_group, True)
                        return quiz
                else:
                    if str(body) == str(q_group.body) and str(call) == str(q_group.call) and str(source) == str(q_group.source) and str(mode) == str(q_group.mode) and str(date) == str(q_group.date):
                        quiz_group = q_group

                        quiz = AGEQuiz(q_group, True)
                        return quiz
        return

    def get_quiz_by_topic(self, body, topic_call, topic, take_non_official_exams):
        quiz_parts = []
        quiz_questions = []

        # Add questions of topics from pool that matches selection
        for q_group in self.question_groups:
            if body == q_group.body:
                # Check whether exam should be browsed
                browse_group = True
                if not take_non_official_exams:
                    if q_group.source != "age":
                        browse_group = False
                if browse_group:
                    for part in q_group.parts:
                        for k, q in enumerate(part.questions):
                            # Add question if topic matches
                            if q.topic is not None:
                                # Convert question call topic into ref call topic
                                tc = TopicConverter(body)
                                q_ref_topic = tc.find_eq_topic(int(q.topic_call), int(q.topic), int(topic_call))[0]

                                # If question topic and ref topic matches
                                if str(topic) == str(q_ref_topic):
                                    printt(f"El tema {str(topic)} se corresponde con el tema {str(q_ref_topic)}")
                                    quiz_questions.append(q)

        part = QuizQuestionPart(quiz_questions, None)
        quiz_parts.append(part)
        q_group = QuizQuestionGroup(quiz_parts)
        quiz = AGEQuiz(q_group, False)
        return quiz

    def get_quiz_by_block(self, body_id, block):
        quiz = AGEQuiz()
        quiz.is_simulation = False
        return quiz



    def format_topic_ocurrence_output(self, topic_id, num_oc, num_qs_with_topic, max_digits_oc, is_topic):
        max_digits_topic = 3

        formatted_topic_num = topic_id.rjust(max_digits_topic)
        formatted_topic_oc = str(num_oc).rjust(max_digits_oc)
        output =  f"#{formatted_topic_num}: {formatted_topic_oc}"

        if is_topic:
            if num_qs_with_topic == 0:
                perc_oc = 0
            else:
                perc_oc = int(num_oc) / num_qs_with_topic * 100
            formatted_perc_oc = str(f"{perc_oc:.2f}").rjust(6)
            output += f" | {formatted_perc_oc} %"
        output += "\n"

        return output

    def get_stats(self, ref_body, ref_call, unofficial_too):
        stats = ""

        all_topics_array = []
        # Read topic list
        all_topics_lines = self.read_csv("../data/processed/1166/programa/topic.csv")
        for all_topic_line in all_topics_lines:
            all_topic_line_body = all_topic_line[0]
            all_topic_line_call = all_topic_line[1]
            all_topic_line_topic = all_topic_line[5]
            all_topic_line_title = all_topic_line[6]
            if all_topic_line_body == str(ref_body) and all_topic_line_call == str(ref_call):
                single_topic_array = [all_topic_line_topic, all_topic_line_title]
                all_topics_array.append(single_topic_array)
        all_topics_num_array = [all_topic_i[0] for all_topic_i in all_topics_array]

        # Initialization
        num_questions = 0
        topic_oc_array = []

        # Calculate stats
        num_qs_with_topic = 0
        for q_group in self.question_groups:
            for q_part in q_group.parts:
                for q in q_part.questions:
                    should_count = True
                    # Check whether the exam is official
                    if not unofficial_too:
                        if q.source != "age":
                            should_count = False

                    if should_count:
                        # Count total questions
                        num_questions += 1
                        if q.topic is not None:
                            num_qs_with_topic += 1

                        # Feed topic array
                        topic_oc_array.append(q.topic)

        # Count the number of times that a topic within all topics appears in a question
        all_topics_oc_dict = count_instances(all_topics_num_array, topic_oc_array)

        # Format stats as text
        stats += "ESTADÍSTICAS DE LA BATERÍA DE PREGUNTAS\n\n"
        stats += "Número total de preguntas: " + str(num_questions) + "\n"

        # # Display topics occurrence in key order (topic order).
        # stats += "Ocurrencias de temas por orden de tema\n"
        # for x in all_topics_oc_dict:
        #     stats += f"#{x}: {all_topics_oc_dict[x]}\n"
        # stats += "\n"

        # Display topic occurrence in key order
        max_digits_oc = len(str(num_questions))
        stats += "Ocurrencia de temas por recurrencia descendente\n"
        topic_oc_by_desc_oc = sorted(all_topics_oc_dict.items(), key=lambda item: item[1], reverse=True)
        for key, value in topic_oc_by_desc_oc:
            stats += self.format_topic_ocurrence_output(key, value, num_qs_with_topic, max_digits_oc,True)
        # Display the number of questions without topic too
        num_qs_without_topic = num_questions - num_qs_with_topic
        stats += self.format_topic_ocurrence_output("N/A", num_qs_without_topic, num_qs_with_topic, max_digits_oc,False)

        # final separator
        stats += "\n"

        return stats

class AGEQuiz:
    def __init__(self, q_group, is_simulation):
        self.q_group = q_group
        self.is_simulation = is_simulation

    # Displays questions and process answers
    def play(self):
        # init counters
        num_cancelled_qs = []
        num_reserve_qs = []
        num_correct_answers = []
        num_incorrect_answers = []

        if self.q_group.parts is not None:
            for i, part in enumerate(self.q_group.parts):
                # init counters
                num_cancelled_qs.append(0)
                num_reserve_qs.append(0)
                num_correct_answers.append(0)
                num_incorrect_answers.append(0)

                if len(self.q_group.parts) > 1:
                    printt("\n\nPARTE " + str(i + 1))

                if len(part.questions) > 0:
                    questions = part.questions

                    for j, question in enumerate(questions):
                        # Loop all questions
                            # Display statement
                            printt("\nPREGUNTA " + str(j + 1) + "/" + str(len(questions)))

                            # Check whether question is cancelled, has no answer os is reserve
                            if question.is_cancelled:
                                num_cancelled_qs[i] += 1
                                printt("! PREGUNTA ANULADA !")
                            else:
                                if not question.has_answer():
                                    num_cancelled_qs[i] += 1
                                    printt("PREGUNTA SIN RESPUESTA, SE CONSIDERA NULA")
                                elif question.is_reserve:
                                    num_reserve_qs[i] += 1

                            # Display options
                            printt(question.get_statement_and_options_text())

                            if question.has_answer():
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
                            else:
                                # Prompt answer
                                player_option = input("Introduzca respuesta [A-D]: ")
                                printt("La pregunta no tiene respuesta. Se contabiliza como nula.")
                else:
                    printt(f"ERROR: La parte {i+1} del exámen generado no tiene preguntas.")
        else:
            printt("ERROR: El exámen generado no tiene partes.")

            # values published after the correction of each test
            #min_direct_score = 39 # 2022 L ord
            #min_direct_score = 39 # 2022 L ext
            #min_direct_score = 37.2 # 2022 L ord
            #min_direct_score = 39 # 2022 L ext
            #min_direct_score = 9  # 2022 L ext ESP
            #min_direct_score = 30  # 2022 L ext GEN

        printt("\n¡Fin del exámen!\n\n")

        printt("\nRESULTADOS")

        # Display total result
        passed_parts = []
        for i, part in enumerate(self.q_group.parts):
            if len(self.q_group.parts) > 1:
                printt("\nRESULTADOS PARTE " + str(i + 1) + "\n")

            questions = part.questions
            if len(part.questions) > 0:
                # maximum direct score should remove cancelled answers
                num_total_qs = len(questions)
                num_used_reserved_qs = self.calc_num_used_reserve_qs(num_reserve_qs[i], num_cancelled_qs[i])
                num_valid_qs = self.calc_num_valid_qs(num_total_qs, num_reserve_qs[i], num_cancelled_qs[i])
                max_direct_score = num_valid_qs

                #prop_min_direct_score = min_direct_score / max_direct_score
                prop_min_direct_score = 0.30
                min_direct_score = prop_min_direct_score * max_direct_score
            else:
                num_total_qs = 0
                num_used_reserved_qs = 0
                num_valid_qs = 0
                max_direct_score = 0
                prop_min_direct_score = 0
                min_direct_score = 0

                printt(f"ERROR: la parte {i + 1} no contiene preguntas.")

            # Score calculation
            direct_score = num_correct_answers[i] - (num_incorrect_answers[i] / 3)
            if max_direct_score != 0:
                ## If direct score is positive or negative, it is converted to zero
                prop_direct_score = direct_score / max_direct_score
            else:
                prop_direct_score = 0
            direct_score_2dec = "{:.2f}".format(round(direct_score, 2))
            per_direct_score_2dec = "{:.2f}".format(round(prop_direct_score * 100, 2))
            per_min_direct_score_2dec = "{:.2f}".format(round(prop_min_direct_score * 100, 2))

            unanswered_questions = num_valid_qs - num_correct_answers[i] - num_incorrect_answers[i]

            # Displaying results
            printt(f"Preguntas totales: {num_total_qs}")
            printt(f"Preguntas anuladas: {num_cancelled_qs[i]}")
            printt(f"Preguntas de reserva (usadas y sin usar): {num_reserve_qs[i]}")
            printt(f"Preguntas de reserva usadas: {num_used_reserved_qs}")
            printt(f"Preguntas totales válidas: {num_valid_qs}")
            printt(f"Preguntas acertadas: {num_correct_answers[i]}")
            printt(f"Preguntas erradas: {num_incorrect_answers[i]}")
            printt(f"Preguntas sin contestar: {unanswered_questions}\n")

            printt(f"Tu puntuación directa: {direct_score_2dec}")
            printt(f"Has obtenido un {per_direct_score_2dec} % de la máxima puntuación posible.")

            if self.is_simulation:
                printt(f"El {per_min_direct_score_2dec} % mínimo requerido para superar el ejercicio.")

                if min_direct_score > 0:
                    if direct_score < min_direct_score:
                        printt("No habrías aprobado esta parte.")
                        passed_parts[i] = False
                    else:
                        printt("Habrías aprobado esta parte.")
                        passed_parts[i] = True

                    ## Calculation of transformed score
                    # if direct_score < min_direct_score:
                    #    transformed_score = max_transformed_score / 2 * direct_score / min_direct_score
                    # else:
                    #    transformed_score = max_transformed_score / 2 * (1 + (direct_score - min_direct_score) / (max_direct_score - min_direct_score)
            else:
                printt(f"El valor medio para aprobar fue 34.40% entre 2019 y 2022 .")

        if passed_parts:
            passed = True
            for passed_part in passed_parts:
                if passed_part == False:
                    passed = False

            if passed:
                printt("\n¡Enhorabuena! Habrías aprobado el ejercicio.\n")
            else:
                printt("\nLo siento, no habrías aprobado el ejercicio.\n")

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

class Quiz:
    def __init__(self):
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
            printt(text)

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

class TopicConverter:
    def __init__(self, body_id):
        topic_conv_lines = self.read_csv('../data/processed/' + body_id + '/programa/topic_eq.csv')
        if not self.check_topic_lines(topic_conv_lines):
            # It should raise an error
            self.topic_conv_lines = None

        # Declare attributes
        self.topic_conv_lines = topic_conv_lines

    def read_csv(self, path):
        with open(path, mode='r') as file:
            reader = csv.reader(file, delimiter=',')

            # Skip the first line (header)
            next(reader)

            # Read the remaining lines into a list
            return [line for line in reader]

    def check_topic_lines(self, topic_eq_lines):
        for topic_eq_line in topic_eq_lines:

            prev_call = int(topic_eq_line[1])
            prev_topic = int(topic_eq_line[2])
            next_call = int(topic_eq_line[3])
            next_topic = int(topic_eq_line[4])

            if prev_call == next_call:
                print("Error in topic conversion file: Prev and next call are equal.")
                print(f"Rule: {prev_call}.{prev_topic} - {next_call}.{next_topic}")
                return False
        return True

    def split_topic_id(self, topic_id):
        # Split the string at the dot
        numbers = topic_id.split('.')

        # Convert the split parts into integers
        call_num = int(numbers[0])
        topic_num = int(numbers[1])

        return call_num, topic_num

    def find_next_call(self, call_num, call_lines):
        take_next = False
        next_call = None
        for call_line in call_lines:
            if take_next:
                next_call = call_line[0]
            if call_line[0] == call_num:
                take_next = True
        return next_call

    def int_or_space(self, number):
        if number == '':
            return ''
        else:
            int(number)

    def find_eq_topic(self, call, topic, ref_call):
        # identify the call after the topic ID call
        # next_call = find_next_call(call_num, call_lines)
        # call_lines = self.call_lines
        topic_conv_lines = self.topic_conv_lines

        topic_results = []

        if ref_call > call:
            going_forward = True
        else:
            going_forward = False

        # loop conversion table
        for topic_conv_line in topic_conv_lines:
            if going_forward:
                line_cur_call = int(topic_conv_line[1])
                line_cur_topic = int(topic_conv_line[2])
            else:
                line_cur_call = int(topic_conv_line[3])
                line_cur_topic = int(topic_conv_line[4])

            if line_cur_call == call and line_cur_topic == topic:
                if going_forward:
                    eq_call = int(topic_conv_line[3])
                    eq_topic = int(topic_conv_line[4])
                else:
                    eq_call = int(topic_conv_line[1])
                    eq_topic = int(topic_conv_line[2])

                if eq_call == ref_call:
                    topic_results.append(eq_topic)
                else:
                    topic_lookup_results = self.find_eq_topic(eq_call, eq_topic, ref_call)
                    if topic_lookup_results:
                        topic_results += topic_lookup_results

        # Remove possible duplicates, respecting original order
        topic_results_no_dupl = [i for n, i in enumerate(topic_results) if i not in topic_results[:n]]

        return topic_results_no_dupl


def print_title():
    with open('quiz/quiz_cli/title.txt', 'r') as file:
        # Read the contents of the file
        print(file.read() + '\n')

def read_csv(path):
    with open(path, mode='r') as file:
        reader = csv.reader(file, delimiter=',')

        # Skip the first line (header)
        next(reader)

        # Read the remaining lines into a list
        return [line for line in reader]

def quiz_select():
    # Display title
    print_title()

    # default values
    default_assessment_id = "1166"
    # It may happen that the most recent call's topic set is different to the preparation material's, because the
    # latter uses an outdated one. Because students spend much time with the preparation material, it may happen that
    # they are more familiar with this set, though outdated. Considering this situation, two different call values
    # are provided.
    # most_recent_call = "2023"
    most_recent_call = "2022"
    default_prep_call = "2020"
    # l = ingreso libre, p = promoción interna
    default_mode = "l"

    # quiz loop
    user_wants_another_quiz = True
    while user_wants_another_quiz:
        # Propose default configuration
        # default_conf_input = input("¿Quieres comenzar con la configuración por defecto? [S/N] (defecto: S): ")
        default_conf_input = "N"

        if default_conf_input == 'S' or default_conf_input == '':
            pass
            # Load default configuration
            assessment_id = default_assessment_id

        else:
            # Read all Spain's AGE bodies
            # Prompt body ID
            printt("")
            # printt("LISTADO DE CUERPOS DE LA AGE")
            printt("PROCESOS DE EVALUACIÓN")

            # Read assessment file
            path = Path("../data/processed/")
            filename = "assessments.csv"
            assessments = read_csv(path / filename)

            # List assessments
            num_assessments = len(assessments)
            assessments_options = []
            for i, assessment in enumerate(assessments):

                aid = assessment[0]
                asname = assessment[1]
                alname = assessment[2]
                abodysname = assessment[3]
                abodylname = assessment[4]
                assessments_options.append(assessment)

                printt(f"[{i+1}] {abodysname} - {asname}")

            printt("")
            assessment_num_input = input("Seleccione un proceso de evaluación [defecto: CSSTIAE]: ")

            if assessment_num_input == "":
                ch_assessment_ind = 0
            else:
                ch_assessment_ind = int(assessment_num_input) - 1

                # printt("[1166] CSSTIAE - Cuerpo Superior de Sistemas y Tecnologías de la Información")
            # printt("")
            # body_id = input(f"Introduza código de cuerpo (defecto: {default_body_id}): ")
            assessment_id = assessments[ch_assessment_ind][0]

            # Initialize question pool
            question_pool = QuizQuestionPool(assessment_id)

            # Prompt call
            # ref_call = input(f"Introduza año de convocatoria de referencia (defecto: {default_ref_call}): ")
            # ref_call = default_ref_call

            mode = default_mode

            # Prompt practice type
            printt("")
            printt("MENÚ PRINCIPAL")
            printt("[E] Practicar por exámen")
            printt("[T] Practicar por tema")
            printt("[S] Ver estadísticas de batería de preguntas")
            printt("[Q] Salir")
            printt("")
            practice_type = input("Introduzca una opción (defecto: E): ").upper()

            if practice_type == '':
                practice_type = 'E'

            if practice_type == 'E':
                select_exam(assessment_id, most_recent_call, mode, question_pool)
            elif practice_type == 'T':
                select_topic(assessment_id, default_prep_call, mode, question_pool)
            elif practice_type == 'B':
                select_block(assessment_id, most_recent_call, mode, question_pool)
            elif practice_type == 'S':
                select_stats(assessment_id, default_prep_call, question_pool)
            elif practice_type == 'Q':
                user_wants_another_quiz = False
            else:
                print("\nOpción no reconocida. Introduzca otra opción.")

def select_exam(body_id, def_call, mode, question_pool):
    print("")
    ref_call_input = input(
        f"Introduzca convocatoria del temario a emplear [S/N] (defecto: {def_call}): ").upper()
    if ref_call_input == '':
        ref_call = def_call
    else:
        ref_call = ref_call_input

    printt("")
    add_non_official_exams_input = input(
        "¿Quieres que se propongan exámenes no oficiales? [S/N] (defecto: S): ").upper()
    if add_non_official_exams_input == '' or add_non_official_exams_input == 'S':
        add_non_official_exams = True
    else:
        add_non_official_exams = False

    # Read exam file
    path = Path("../data/processed/" + str(body_id) + "/test/")
    filename = "exam.csv"
    exams = read_csv(path / filename)

    # List exams
    num_exams = len(exams)
    exam_options = []
    for i, exam in enumerate(exams):
        ebody = exam[0]
        esource = exam[1]
        ecall = exam[2]
        edate = exam[3]
        emode = exam[4]

        add_exam = True
        if str(body_id) == ebody:
            # Check whether the exam is unofficial
            if not add_non_official_exams and esource != "age":
                add_exam = False
            if add_exam:
                option_num = str(len(exam_options) + 1).rjust(len(str(num_exams)))
                exam_options.append([ebody, esource, ecall, emode, edate])

                if emode == "":
                    printt(f"[{option_num}] - {ebody}.{esource}.{ecall}.{edate}")
                else:
                    printt(f"[{option_num}] - {ebody}.{esource}.{ecall}.{emode}.{edate}")

    # Prompt exam number
    if len(exam_options) > 0:
        printt("")
        exam_num_input = input("Introduzca exámen (defecto 1): ")
        if exam_num_input == "":
            ch_exam_ind = 0
        else:
            ch_exam_ind = int(exam_num_input)-1

        ch_exam = exam_options[ch_exam_ind]
        ch_body = ch_exam[0]
        ch_source = ch_exam[1]
        ch_call = ch_exam[2]
        ch_mode = ch_exam[3]
        ch_date = ch_exam[4]

        # Create
        quiz = question_pool.get_quiz_by_exam(ch_body, ch_call, ch_source, ch_mode, ch_date)
        # quiz.shuffle()

        # Play quiz
        quiz.play()
    else:
        printt("No se encontraron preguntas para ese tema")

def select_topic(body_id, def_call, mode, question_pool):
    print("")
    ref_call_input = input(
        f"Introduzca convocatoria del temario a emplear [S/N]: (defecto: {def_call}): ").upper()
    if ref_call_input == '':
        ref_call = def_call
    else:
        ref_call = ref_call_input

    # Read topic file
    dirpath = "../data/processed/" + body_id + "/programa/"
    filename = "topic.csv"
    fullpath = os.path.join(dirpath, filename)
    #topics = read_csv(fullpath)
    topics = read_csv(dirpath + filename)

    # List topics
    num_topics = len(topics)
    topic_options = []
    for i, topic in enumerate(topics):
        tbody = topic[0]
        tcall = topic[1]
        ttopic_num = topic[5]
        ttopic_title = topic[6]

        if str(body_id) == tbody and str(ref_call) == tcall:
            # The option number would be the next available number
            option_num = str(len(topic_options)+1).rjust(len(str(num_topics)))
            topic_options.append([tbody, tcall, ttopic_num])
            print(f"[{option_num}] - {tbody}.{tcall}.{ttopic_num} - {ttopic_title[:50]}")

    # Prompt topic number
    if len(topic_options) > 0:
        printt("")
        topic_num_input = input("Introduzca tema (defecto: 1): ")
        if topic_num_input == "":
            ch_topic_ind = 0
        else:
            ch_topic_ind = int(topic_num_input)-1

        ch_topic = topic_options[ch_topic_ind]
        ch_body = ch_topic[0]
        ch_topic_num = ch_topic[2]

        # Preguntar si se quieres preguntas solo oficiales
        printt("")
        add_non_official_exams_input = input(
            "¿Quieres añadir preguntas fuera de los exámenes oficiales? [S/N]: (defecto: S): ").upper()
        if add_non_official_exams_input == 'S':
            consider_non_official_exams = True
        else:
            consider_non_official_exams = False

        # Create
        quiz = question_pool.get_quiz_by_topic(ch_body, ref_call, ch_topic_num, consider_non_official_exams)

        # Play quiz
        quiz.play()
    else:
        printt("No se encontraron preguntas para ese tema")

def select_block(body_id, def_call, mode, question_pool):
    # List blocks


    # Prompt block


    # Get quiz questions
    quiz = question_pool.get_quiz_by_block(body_id, block)

def select_stats(body_id, def_call, question_pool):
    printt("")
    ref_call_input = input(
        f"Introduzca convocatoria del temario a emplear [S/N]: (defecto: {def_call}): ").upper()
    if ref_call_input == '':
        ref_call = def_call
    else:
        ref_call = ref_call_input

    printt("")
    consider_non_official_exams_input = input(
        "¿Quieres considerar preguntas fuera de los exámenes oficiales? [S/N]: (defecto: S): ").upper()
    if consider_non_official_exams_input == 'S':
        consider_non_official_exams = True
    else:
        consider_non_official_exams = False

    printt("")
    print(question_pool.get_stats(body_id, ref_call, consider_non_official_exams))

def quiz_quickrun():
    print_title()

    printt("CARGANDO LA BATERÍA DE PREGUNTAS...")

    # Load question pool
    question_pool = QuizQuestionPool()

    printt("[CARGADO]\n")

    #exam = question_pool.question_groups[0]
    #printt(exam.get_text())

    print(question_pool.list_question_groups())

    # Options menu

    # Quiz preparation

    # Enter reference body and call
    body = "1166"
    call = "2022"
    source = "age"

    # Print question pool stats
    # print(question_pool.get_stats(body, call))

    mode = "l"
    date = "20231006"

    topic_no = 34

    block = "e"

    printt("EL EXÁMEN DA COMIENZO\n")

    quiz = question_pool.get_quiz_by_exam(body, call, source, date, mode)
    # quiz = question_pool.get_quiz_by_topic(body, topic_no)
    # quiz = question_pool.get_quiz_by_block(body, block)

    # Call quiz
    quiz.play()

    #select_and_play_quizzes(question_pool)

    # Old functionality
    #select()
    #play()

    # Ask if it wants to perform another test

def quiz_test_topic_converter():
    default_call = 2020
    default_topic = "2022.1"

    body = 1166

    tc = TopicConverter(str(body))

    ref_call = input(f"Enter reference call [default {default_call}]:")
    if ref_call == '':
        ref_call = default_call
    else:
        ref_call = int(ref_call)

    topic_id = input(f"Enter topic ID [default {default_topic}]:")
    if topic_id == '':
        topic_id = default_topic

    call_num, topic_num = tc.split_topic_id(topic_id)

    if ref_call == call_num:
        print("Source call and goal call are equivalent = " + str(ref_call))
    else:
        print("")
        print("Parameters: ")
        print(f"call_num: {call_num}")
        print(f"topic_num: {topic_num}")
        print(f"ref_call: {ref_call}")
        print("")
        ref_topics = tc.find_eq_topic(call_num, topic_num, ref_call)

        if ref_topics:
            # display results
            for ref_topic in ref_topics:
                print(f"{topic_id} -> {ref_call}.{ref_topic}")
        else:
            print(f"Cannot find equivalence {topic_id} in call {ref_call}.")

def main():
    quiz_quickrun()

if __name__ == "__main__":
    main()
