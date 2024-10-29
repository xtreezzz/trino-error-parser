# Trino Error Parser

This project extracts error information from the Trino source code by parsing exception throws. It outputs the data in a unified JSON format for further analysis or integration with other tools.

## Table of Contents

- [Features](#features)
- [Unified JSON Schema](#unified-json-schema)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Parses Java source files in the Trino project.
- Extracts detailed error information including:
  - File path
  - Error code
  - Error class name
  - Error message template
  - Error message variables
  - Severity level
  - Original code line
- Outputs data in a unified JSON schema.

## Unified JSON Schema

```json
{
  "file_path": "string",
  "error_code": "string or number",
  "error_code_name": "string",
  "error_class_name": "string",
  "error_message_template": "string",
  "error_message_variables": ["array of strings"],
  "severity_level": "string",
  "original_text": "string"
}
```

## Prerequisites

- Python 3.6 or higher
- Trino source code available locally

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/trino-error-parser.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd trino-error-parser
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *Note: Currently, there are no external dependencies. If you add any, list them in `requirements.txt`.*

## Usage

Run the parser script using the following command:

```bash
python src/trino_parser.py -s /path/to/trino/source -o data/errors_trino.json
```

- `-s`, `--source_directory`: (Required) Path to the Trino source code directory.
- `-o`, `--output_file`: (Optional) Path to the output JSON file. Defaults to `errors_trino.json` in the current directory.

## Examples

**Example command:**

```bash
python src/trino_parser.py -s ~/projects/trino -o data/errors_trino.json
```

This command parses the Trino source code located at `~/projects/trino` and saves the extracted error information to `data/errors_trino.json`.

## Project Structure

```
trino-error-parser/
├── src/
│   └── trino_parser.py       # Main parsing script
├── data/
│   └── errors_trino.json     # Output JSON file
├── tests/
│   └── test_trino_parser.py  # Unit tests
├── README.md                 # Project documentation
├── LICENSE                   # Project license
└── requirements.txt          # Python dependencies
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
