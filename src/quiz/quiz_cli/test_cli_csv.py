import csv
import random

from test_cli_text import *
import quiz_cli_shared as qcs

# Width of the terminal where text is going to be displayed
TERM_WIDTH = 80
# Path to the question pool file
QUESTION_POOL_FILEPATH = 'preg-test.csv'

def load_question_pool_csv():
    qcs.question_pool = read_csv(QUESTION_POOL_FILEPATH)

def read_csv(file_path):
    questions = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            questions.append(row)
    return questions


def configure_quiz():
    quiz_lesson = qcs.quiz_lesson

    # Ask whether default configuration is applied
    qcs.quiz_lesson = 0
    qcs.num_questions = 0

    default_conf = input("¿Quieres hacer un 2022 rápido con la configuración por defecto? (S/N): ").upper()
    if default_conf != '' and default_conf != 'S':
        # Ask lesson to quiz
        qcs.quiz_lesson = input("Introduzca tema a evaluar (vacío significa todos): ")
        if qcs.quiz_lesson == "":
            qcs.quiz_lesson = 0
        else:
            qcs.quiz_lesson = int(quiz_lesson)

        # Ask number of questions
        qcs.num_questions = input("Introduzca número de preguntas (vacío significa todas): ")
        if qcs.num_questions == "":
            qcs.num_questions = 0
        else:
            qcs.num_questions = int(qcs.num_questions)

    # Initialize quiz values
    qcs.quiz_questions = []
    qcs.quiz_correct_answers = 0

def generate_quiz_questions():
    for question_i, question in enumerate(qcs.question_pool, 1):
        question_lesson = question['Tema']

        #If the quiz is focused on a corps, only process these questions

        # If the quiz is focused on a lesson, only process these questions
        if qcs.quiz_lesson > 0:
            if qcs.quiz_lesson != question_lesson:
                continue

        qcs.quiz_questions.append(question)

    # Sort questions in a random order
    random.shuffle(qcs.quiz_questions)

    # If the number of questions is limited, discard the rest
    if qcs.num_questions > 0:
        qcs.quiz_questions = qcs.quiz_questions[:qcs.num_questions]

def start_quiz():
    for question_i, question in enumerate(qcs.quiz_questions, 1):

        # Print question
        question_text_title = "\nPregunta " + str(question_i)
        if qcs.quiz_lesson != 0:
            question_text_title += f", del tema {qcs.quiz_lesson} "
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
            qcs.quiz_correct_answers += 1
            print("¡Correcto!")
        else:
            print(f"Incorrecto. La respuesta correcta es {number_to_letter(correct_answer_index).upper()}.")
        print()

def end_quiz():
    # Display the final results
    print("\nRESULTADOS\n")
    num_questions = len(qcs.quiz_questions)
    print(f"Se acertaron {qcs.quiz_correct_answers} de {num_questions} preguntas.")
    print(f"{str(round(qcs.quiz_correct_answers / num_questions*100, 2))} % de aciertos")

    # Reinitialize the variables
    qcs.quiz_questions = []
    qcs.quiz_lesson = 0
    qcs.quiz_correct_answers = 0


def main():
    print_title()
    load_question_pool_csv()
    configure_quiz()
    generate_quiz_questions ()
    start_quiz()
    end_quiz()

if __name__ == "__main__":
    main()
