import re
import xml.etree.ElementTree as ET


def parse_aiken(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    questions = []
    current_question = {}
    answer_pattern = re.compile(r'^ANSWER:\s*([A-Za-z])')
    # Match both '.' and ')'
    choice_pattern = re.compile(r'^[A-Za-z][\.\)]')

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(answer_pattern, line):
            current_question['answer'] = answer_pattern.match(line).group(1)
            questions.append(current_question)
            current_question = {}
        elif re.match(choice_pattern, line):
            if 'choices' not in current_question:
                current_question['choices'] = []
            current_question['choices'].append(line)
        else:
            current_question['question'] = line

    return questions


def generate_qti(questions):
    qti = ET.Element('assessmentItem',
                     attrib={'xmlns': 'http://www.imsglobal.org/xsd/imsqti_v3p0', 'identifier': 'sample',
                             'title': 'Sample Assessment', 'adaptive': 'false', 'timeDependent': 'false'})

    for i, q in enumerate(questions):
        item_body = ET.SubElement(qti, 'itemBody')
        prompt = ET.SubElement(item_body, 'prompt')
        prompt.text = q['question']

        choice_interaction = ET.SubElement(item_body, 'choiceInteraction',
                                           attrib={'responseIdentifier': f'response{i}', 'shuffle': 'false',
                                                   'maxChoices': '1'})

        for choice in q['choices']:
            choice_id = choice[0].upper()  # The letter (A, B, C, etc.)
            choice_text = choice[2:].strip()  # The text after the letter and separator
            simple_choice = ET.SubElement(choice_interaction, 'simpleChoice', attrib={'identifier': choice_id})
            simple_choice.text = choice_text

        response_declaration = ET.SubElement(qti, 'responseDeclaration',
                                             attrib={'identifier': f'response{i}', 'cardinality': 'single',
                                                     'baseType': 'identifier'})
        correct_response = ET.SubElement(response_declaration, 'correctResponse')
        value = ET.SubElement(correct_response, 'value')
        value.text = q['answer']

    return ET.ElementTree(qti)


# Main function to run the conversion
def convert_aiken_to_qti(aiken_file, qti_file):
    questions = parse_aiken(aiken_file)
    qti_tree = generate_qti(questions)
    # Use the built-in indent method
    ET.indent(qti_tree, space="  ")
    qti_tree.write(qti_file, encoding='utf-8', xml_declaration=True)

# Example usage:
input_file_path = "../../../data/processed/1166/test/2022/20230606/1166_2022_l_20230606_gen.aiken"
output_file_path = "../../../data/processed/1166/test/2022/20230606/20230606_gen.qti"

convert_aiken_to_qti(input_file_path, output_file_path)
