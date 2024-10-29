import unittest
from src.trino_parser import split_arguments, parse_error_message_argument

class TestTrinoParser(unittest.TestCase):

    def test_split_arguments(self):
        argument_string = 'INVALID_FUNCTION_ARGUMENT, "Error message"'
        expected = ['INVALID_FUNCTION_ARGUMENT', '"Error message"']
        result = split_arguments(argument_string)
        self.assertEqual(result, expected)

    def test_parse_error_message_argument(self):
        error_message_argument = '"\'" + unit.toStringUtf8() + "\' is not a valid TIMESTAMP field"'
        expected_template = "'{}' is not a valid TIMESTAMP field"
        expected_variables = ['unit.toStringUtf8()']
        template, variables = parse_error_message_argument(error_message_argument)
        self.assertEqual(template, expected_template)
        self.assertEqual(variables, expected_variables)

if __name__ == '__main__':
    unittest.main()
