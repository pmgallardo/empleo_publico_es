import csv
import os

INPUT_FILENAME = '20230606_esp.txt'


def read_file(filepath):
    with open(filepath, "r", encoding='utf-8') as file:
        return file.read()


def parse_questions(input_text):
    questions = []
    lines = input_text.split('\n')
    current_question = None
    current_options = []
    question_number = 1

    for line in lines:
        line = line.strip()
        if line.startswith(f'{question_number}.'):
            if current_question is not None:
                current_question['content'] = ' '.join(current_question['content']).strip()
                questions.append(current_question)
            print(line)
            current_question = {'content': [line[line.index(" ") + 1:]], 'options': []}
            current_options = []
            question_number += 1
        elif line.startswith(('a)', 'b)', 'c)', 'd)')):
            if current_question is not None:
                current_options.append(line[3:].strip())
                if line.startswith('d)'):
                    current_question['options'] = current_options
        else:
            if current_question is not None:
                if current_options:
                    current_options[-1] += ' ' + line
                else:
                    current_question['content'].append(line)

    if current_question is not None:
        current_question['content'] = ' '.join(current_question['content']).strip()
        questions.append(current_question)

    return questions


def write_csv(questions, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Question number', 'Content of question', 'Option A', 'Option B', 'Option C', 'Option D'])
        for i, question in enumerate(questions, 1):
            row = [i, question['content']] + question['options']
            # Ensure the row has exactly 6 elements (4 options), pad with empty strings if necessary
            row.extend([''] * (6 - len(row)))
            writer.writerow(row)


# Example usage
input_text = """
1. En desarrollo de proyectos, el registro de impactos de la adaptación a un proceso es una
actividad incluída en la fase de procesos de:
a) Información.
b) Cierre.
c) Monitorización y Control.
d) Ejecución.
2. El histograma de recursos refleja la cantidad de técnicos que intervienen en un proyecto.
Indique la respuesta VERDADERA en relación a esta afirmación:
a) En el histograma de recursos se representan los recursos materiales necesarios para la
realización de un proyecto, no recursos humanos.
b) Para que un diagrama de Gantt sea realista y fiable debe ir acompañado de un histograma de
recursos.
c) El histograma de recursos también se denomina Patrón de límites.
d) El histograma de recursos, usando redes, permite establecer dependencias entre los recursos
humanos que participan en el proyecto.
3. En la asignación de tiempos de un proyecto el tiempo Early del suceso inicial del proyecto
es:
a) Igual a la duración mínima del proyecto.
b) La duración mínima esperada para la primera actividad.
c) Igual a cero.
d) Igual a 1.
4. En el caso de que a una licitación se presente una Unión Temporal de Empresas (UTE):
a) Es necesario que esté constituida previamente a la adjudicación del contrato.
b) Es necesario que esté constituida en el momento de la valoración de las ofertas.
c) No es necesario que esté constituida previamente hasta la finalización del contrato, momento
en que será obligatoria su constitución.
d) No es necesario que esté constituida previamente a la adjudicación del contrato, solo un
compromiso de que lo estará si resulta adjudicataria.
"""

# Get the directory of the current script
script_dir = os.path.dirname(__file__)

# Construct the full path to the input file
input_filepath = os.path.join(script_dir, INPUT_FILENAME)
input_text = read_file(input_filepath)

questions = parse_questions(input_text)

# Get the base name of the file (e.g., "input.csv")
base_name = os.path.basename(input_filepath)
# Split the base name into name and extension (e.g., "input" and ".csv")
name, ext = os.path.splitext(base_name)

write_csv(questions, name + ".csv")
