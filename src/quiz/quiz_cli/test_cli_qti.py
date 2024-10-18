import xml.etree.ElementTree as ET
import random

from test_cli_text import *
import quiz_cli_shared as qcs

# Width of the terminal where text is going to be displayed
TERM_WIDTH = 80
# Path to the QTI question pool file
QUESTION_POOL_FILEPATH = '../../../data/processed/es_age_1166/test/age/2022/20230606/20230606_gen.qti'

def load_question_pool_qti():
    return read_qti(QUESTION_POOL_FILEPATH)

def read_qti(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the namespace
    namespace = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v3p0'}

    questions = []

    # Find all assessmentItem elements using fully qualified name
    assessment_items = root.findall('.//qti:assessmentItem', namespace)

    for item in assessment_items:
        # Get prompt
        prompt = item.find('.//qti:itemBody/qti:prompt', namespace).text

        # Get choices
        choices = item.findall('.//qti:itemBody/qti:choiceInteraction/qti:simpleChoice', namespace)
        options = [choice.text for choice in choices]

        # Get correct answer
        correct_response = item.find('.//qti:responseDeclaration/qti:correctResponse/qti:value', namespace).text

        question = {
            'Pregunta': prompt,
            'Opción 1': options[0] if len(options) > 0 else '',
            'Opción 2': options[1] if len(options) > 1 else '',
            'Opción 3': options[2] if len(options) > 2 else '',
            'Opción 4': options[3] if len(options) > 3 else '',
            'Opción correcta': correct_response,
            'Tema': '1'  # Placeholder for topic/theme, adjust if needed
        }

        questions.append(question)

    return questions

def configure_quiz():
    # Initialize quiz values
    global quiz_lesson, num_questions
    quiz_lesson = 0
    num_questions = 0

    # Ask whether default configuration is applied
    default_conf = input("¿Quieres hacer un 2022 rápido con la configuración por defecto? (S/N): ").upper()
    if default_conf != '' and default_conf != 'S':
        # Ask lesson to quiz
        lesson_input = input("Introduzca tema a evaluar (vacío significa todos): ")
        quiz_lesson = int(lesson_input) if lesson_input.isdigit() else 0

        # Ask number of questions
        num_questions_input = input("Introduzca número de preguntas (vacío significa todas): ")
        num_questions = int(num_questions_input) if num_questions_input.isdigit() else 0

def generate_quiz_questions(question_pool):
    quiz_questions = []

    for question_i, question in enumerate(question_pool, 1):
        question_lesson = question['Tema']

        # If the quiz is focused on a lesson, only process these questions
        if quiz_lesson > 0:
            if quiz_lesson != int(question_lesson):
                continue

        quiz_questions.append(question)

    # Sort questions in a random order
    random.shuffle(quiz_questions)

    # If the number of questions is limited, discard the rest
    if num_questions > 0:
        quiz_questions = quiz_questions[:num_questions]

    return quiz_questions

def start_quiz(quiz_questions):
    quiz_correct_answers = 0

    for question_i, question in enumerate(quiz_questions, 1):
        # Print question
        question_text_title = f"\nPregunta {question_i}"
        if quiz_lesson != 0:
            question_text_title += f", del tema {quiz_lesson} "
        print(question_text_title)

        print(f"\n{format_text(question['Pregunta'], TERM_WIDTH)}\n")

        # Print options
        options = [question['Opción 1'], question['Opción 2'], question['Opción 3'], question['Opción 4']]
        for i, option in enumerate(options, 1):
            option_text = number_to_letter(i).upper() + ") "
            indent_width = len(option_text)
            option_text = option_text + option
            print(format_text(option_text, TERM_WIDTH, indent_width))
        print()

        while True:
            try:
                user_input = input("Introduzca respuesta: ").strip()

                # User may enter a letter or number
                if user_input.isalpha() and len(user_input) == 1:
                    user_input = letter_to_number(user_input)

                answer_index = int(user_input)

                # Check answers
                if answer_index < 1 or answer_index > 4:
                    raise ValueError("La respuesta debe estar entre A-D / 1-4")
                break
            except ValueError as e:
                print(e)

        correct_answer_index = int(question['Opción correcta'])
        if answer_index == correct_answer_index:
            quiz_correct_answers += 1
            print("¡Correcto!")
        else:
            print(f"Incorrecto. La respuesta correcta es {number_to_letter(correct_answer_index).upper()}.")
        print()

    return quiz_correct_answers

def end_quiz(quiz_correct_answers, num_questions):
    # Display the final results
    print("\nRESULTADOS\n")
    print(f"Se acertaron {quiz_correct_answers} de {num_questions} preguntas.")
    print(f"{str(round(quiz_correct_answers / num_questions * 100, 2))} % de aciertos")

def main():
    print_title()
    question_pool = load_question_pool_qti()
    configure_quiz()
    quiz_questions = generate_quiz_questions(question_pool)
    quiz_correct_answers = start_quiz(quiz_questions)
    end_quiz(quiz_correct_answers, len(quiz_questions))

if __name__ == "__main__":
    main()
