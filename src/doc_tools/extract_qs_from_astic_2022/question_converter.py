import multichoice_question
import json

def convert_multichoice_questions_to_aiken(questions):
    output = ""

    for i, question in enumerate(questions):
        # Append question statement
        #output += question.statement + "\n"
        output += str(i+1) + ". " + question.statement + "\n"

        for j, option in enumerate(question.options):
            option_letter = number_to_letter(j + 1)
            # Append question option
            output += option_letter + ") " + option
            if j < len(question.options)-1:
                output += "\n"

        # Append answer
        if question.answer is not None:
            print("\nANSWER: " + question.answer)
            # Add a newline between questions, but not after the last question

        if i < len(questions) - 1:
            output += "\n\n"

    return output

def number_to_letter(number):
    return chr(number + 96)


def convert_multichoice_questions_to_json(questions):
    questions_list = [question.to_dict() for question in questions]
    return json.dumps(questions_list, indent=4)