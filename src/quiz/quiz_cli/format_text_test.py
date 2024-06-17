from test_cli_text import *

text = "B) Sin consentimiento previo del afectado y exclusivamente para garantizar el ejercicio del derecho al sufragio."
width = 80
hanging_width = 3
formatted_text = format_text(text, width, hanging_width)
print(formatted_text)