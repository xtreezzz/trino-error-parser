import os
import re
import json
import argparse

# Regular expression to find exception throws with nested constructors support
exception_pattern = re.compile(
    r'throw\s+new\s+(\w+Exception)\s*\((.*)\);'
)

# Regular expression to find string literals in arguments
string_literal_pattern = re.compile(r'"(.*?)"')

def split_arguments(argument_string):
    arguments = []
    current_arg = ''
    paren_count = 0
    in_quote = False
    i = 0
    while i < len(argument_string):
        c = argument_string[i]
        if c == '"' and (i == 0 or argument_string[i - 1] != '\\'):
            in_quote = not in_quote
            current_arg += c
        elif in_quote:
            current_arg += c
        elif c == ',' and paren_count == 0:
            arguments.append(current_arg.strip())
            current_arg = ''
        else:
            if c == '(':
                paren_count += 1
            elif c == ')':
                paren_count -= 1
            current_arg += c
        i += 1
    if current_arg:
        arguments.append(current_arg.strip())
    return arguments

def parse_error_message_argument(error_message_argument):
    current_part = ''
    in_quote = False
    escaped = False
    variables = []
    template = ''
    i = 0
    while i < len(error_message_argument):
        c = error_message_argument[i]
        if c == '\\' and not escaped:
            escaped = True
            current_part += c
        elif c == '"' and not escaped:
            in_quote = not in_quote
            current_part += c
            if not in_quote:
                # End of string literal
                content = current_part[1:-1]
                template += content
                current_part = ''
        elif c == '+' and not in_quote:
            if current_part.strip():
                if not current_part.startswith('"'):
                    # Variable
                    template += '{}'
                    variables.append(current_part.strip())
                current_part = ''
        else:
            current_part += c
            escaped = False
        i += 1
    if current_part.strip():
        if current_part.startswith('"') and current_part.endswith('"'):
            # String literal
            content = current_part[1:-1]
            template += content
        else:
            # Variable
            template += '{}'
            variables.append(current_part.strip())
    return template, variables

def search_errors_in_source(source_directory):
    errors = []
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".java"):
                # Correct path handling for Windows and Unix
                file_path = os.path.join(root, file).replace("\\", "/")
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Search for exception throws
                        match = exception_pattern.search(line)
                        if match:
                            error_class_name = match.group(1)
                            error_message = match.group(2)

                            # Split the arguments
                            args = split_arguments(error_message)
                            if len(args) >= 2:
                                error_code = args[0]
                                error_message_argument = args[1]
                                # Parse error message
                                error_message_template, error_message_variables = parse_error_message_argument(error_message_argument)
                            else:
                                error_code = None
                                error_message_template = ''
                                error_message_variables = []

                            # Build the unified error entry
                            errors.append({
                                'file_path': file_path,
                                'error_code': error_code.strip('"') if error_code else None,
                                'error_code_name': None,  # Adjust if you have a mapping
                                'error_class_name': error_class_name,
                                'error_message_template': error_message_template,
                                'error_message_variables': error_message_variables,
                                'severity_level': "ERROR",
                                'original_text': line
                            })
    return errors

# Save results to a JSON file
def save_errors_to_json(errors, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(errors, f, indent=4, ensure_ascii=False)
    print(f"Results saved to {output_file}")

# Main logic
if __name__ == '__main__':
    # Unified input handling using argparse
    parser = argparse.ArgumentParser(description='Parse Trino source code for exceptions.')
    parser.add_argument('-s', '--source_directory', required=True, help='Path to the Trino source code directory.')
    parser.add_argument('-o', '--output_file', default='errors_trino.json', help='Output JSON file path.')
    args = parser.parse_args()

    source_directory = args.source_directory
    output_file = args.output_file

    errors_found = search_errors_in_source(source_directory)
    save_errors_to_json(errors_found, output_file)
