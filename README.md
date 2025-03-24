<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/65581c5b-b8f7-4efd-8856-9309602a37a5" width="400">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/fca44af5-8d62-402d-b1d7-5f465da3b5bb" width="400">
  <img alt="MPython logo." src="https://github.com/user-attachments/assets/fca44af5-8d62-402d-b1d7-5f465da3b5bb" width="400">
</picture>

# MPython Core

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mpython-core)
![PyPI - License](https://img.shields.io/pypi/l/mpython-core)
![PyPI - Version](https://img.shields.io/pypi/v/mpython-core)

MPython Core provides Python bindings for MATLAB projects, enabling seamless integration of MATLAB functionalities into Python workflows. This package is designed to facilitate the creation of bindings for MATLAB projects, allowing users to interact with MATLAB objects, functions, and arrays directly from Python.

## Features

- **MATLAB Integration**: Interact with MATLAB objects, functions, and arrays directly from Python.
- **Custom Data Types**: Includes Python representations of MATLAB data types such as `Cell`, `Struct`, `Array`, and `SparseArray`.
- **Delayed Arrays**: Support for delayed evaluation of MATLAB arrays.
- **Sparse Matrix Support**: Handles MATLAB sparse matrices using `scipy.sparse` (if available).
- **Object-Oriented Design**: Provides a clean and extensible API for working with MATLAB projects.

## Installation

To install MPython-Core, use pip:

```bash
pip install mpython-core
```

## Requirements

- Python 3.9 - 3.12
- MATLAB Runtime (if MATLAB is not installed)
- NumPy
- Optional: SciPy (for sparse matrix support)

## Usage

### Example: Working with MATLAB Data Types

```python
from mpython import Cell, Struct, Array

# Create a MATLAB cell array
cell = Cell.from_any([[1, 2], [3, 4]])

# Create a MATLAB struct
struct = Struct(a=Array([1, 2, 3]), b="example")

# Access struct fields
print(struct.a)
print(struct["b"])
```

## Development

### Setting Up the Development Environment

1. Clone the repository:
    ```bash
    git clone https://github.com/MPython-Package-Factory/mpython-core.git
    cd mpython-core
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running Tests

To run the test suite:

```bash
pytest
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the [GNU General Public License v2 (GPLv2)](LICENSE).

## Authors

- Johan Medrano ([johan.medrano@ucl.ac.uk](mailto:johan.medrano@ucl.ac.uk))
- Yael Balbastre ([y.balbastre@ucl.ac.uk](mailto:y.balbastre@ucl.ac.uk))

## Links

- [Repository](https://github.com/MPython-Package-Factory/mpython-core)
