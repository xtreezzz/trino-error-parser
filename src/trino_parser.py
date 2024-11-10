import os
import re
import json
import argparse

# Regular expression to find exception throws with nested constructors support
exception_pattern = re.compile(
    r'throw\s+new\s+([\w<>, ]+Exception)\s*\((.*?)\);', re.DOTALL
)

def split_arguments(argument_string):
    arguments = []
    current_arg = ''
    paren_count = 0
    in_quote = False
    escaped = False
    i = 0
    while i < len(argument_string):
        c = argument_string[i]
        if c == '\\' and not escaped:
            escaped = True
            current_arg += c
        elif c == '"' and not escaped:
            in_quote = not in_quote
            current_arg += c
        elif c == ',' and not in_quote and paren_count == 0:
            arguments.append(current_arg.strip())
            current_arg = ''
        else:
            if c == '(' and not in_quote:
                paren_count += 1
            elif c == ')' and not in_quote:
                paren_count -= 1
            current_arg += c
        if escaped and c != '\\':
            escaped = False
        i += 1
    if current_arg.strip():
        arguments.append(current_arg.strip())
    return arguments

def parse_error_message_argument(error_message_argument):
    error_message_argument = error_message_argument.strip()
    # Check if it's a format call (String.format or statically imported format)
    format_match = re.match(r'(?:String\.)?format\((.*)\)', error_message_argument)
    formatted_match = re.match(r'"(.*)"\.formatted\((.*)\)', error_message_argument)
    if format_match:
        # Existing format(...) handling
        format_args_str = format_match.group(1)
        format_args = split_arguments(format_args_str)
        if format_args:
            format_string = format_args[0].strip('"')
            format_variables = format_args[1:]
            return format_string, format_variables
    elif formatted_match:
        # Handle "..." .formatted(...)
        format_string = formatted_match.group(1)
        format_args_str = formatted_match.group(2)
        format_variables = split_arguments(format_args_str)
        return format_string, format_variables
    else:
        # Existing parsing logic
        if error_message_argument.startswith("(") and error_message_argument.endswith(")"):
            error_message_argument = error_message_argument[1:-1].strip()

        template_parts = []
        variables = []
        tokens = re.split(r'(\+)', error_message_argument)
        in_quote = False
        current_string = ''
        for token in tokens:
            token = token.strip()
            if not token:
                continue
            if token == '+':
                continue
            if token.startswith('"') and token.endswith('"') and not in_quote:
                content = token[1:-1]
                template_parts.append(content)
            elif token.startswith('"') and not in_quote:
                in_quote = True
                current_string = token[1:]
            elif token.endswith('"') and in_quote:
                current_string += token[:-1]
                template_parts.append(current_string)
                current_string = ''
                in_quote = False
            elif in_quote:
                current_string += token
            else:
                template_parts.append('{}')
                variables.append(token)

        template = ''.join(template_parts)
        return template, variables

def search_errors_in_source(source_directory):
    errors = []
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".java"):
                # Compute the absolute path
                absolute_path = os.path.join(root, file)
                # Compute the relative path
                relative_path = os.path.relpath(absolute_path, source_directory).replace("\\", "/")
                with open(absolute_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                # Search for exception throws
                matches = exception_pattern.finditer(source_code)
                for match in matches:
                    error_class_name = match.group(1).strip()
                    error_message = match.group(2).strip()
                    # Split the arguments
                    args = split_arguments(error_message)
                    error_message_template = ''
                    error_message_variables = []
                    if args:
                        message_found = False
                        for arg in args:
                            arg = arg.strip()
                            if arg.startswith('"') and arg.endswith('"'):
                                # String literal
                                error_message_template = arg.strip('"')
                                message_found = True
                                break
                            elif 'format(' in arg or '.formatted(' in arg:
                                # Possibly a format call
                                error_message_template, error_message_variables = parse_error_message_argument(arg)
                                message_found = True
                                break
                            elif '+' in arg or '"' in arg:
                                # Concatenated string
                                error_message_template, error_message_variables = parse_error_message_argument(arg)
                                message_found = True
                                break
                        if not message_found:
                            # No message argument found, use exception class name as message
                            error_message_template = error_class_name
                    else:
                        # No arguments, use exception class name as message
                        error_message_template = error_class_name
                    # Find line number
                    start_index = match.start()
                    line_number = source_code.count('\n', 0, start_index) + 1
                    line_text = source_code.split('\n')[line_number - 1].strip()
                    # Build the unified error entry
                    errors.append({
                        'file_path': f"{relative_path}:{line_number}",
                        'error_code': None,  # Adjust if you have a mapping
                        'error_code_name': None,
                        'error_class_name': error_class_name,
                        'error_message_template': error_message_template,
                        'error_message_variables': error_message_variables,
                        'severity_level': "ERROR",
                        'original_text': line_text
                    })
    return errors

# Save results to a JSON file
def save_errors_to_json(errors, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'errors': errors}, f, indent=4, ensure_ascii=False)
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
