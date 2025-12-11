# emba-tuition-model

A python model to determine the optimal tuition for a particular Executive MBA program.

## Prerequisites

- **uv**: The modern Python version, package, and environment manager.

## Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/zrisher/emba-tuition-model
    cd emba-tuition-model
    ```

2.  **Install dependencies**:
    Use uv to create the environment and install required packages:

    ```bash
    uv sync
    ```

3.  **Install pre-commit hooks** (optional):
    If you plan to contribute, install the pre-commit hooks:

    ```bash
    pre-commit install
    ```

## Usage

To run the main application:

```bash
uv run main.py
```

## Development

### Code Formatting

This project uses **Ruff** for Python linting/formatting and **Prettier** for other files (JSON, Markdown, and JavaScript):

- VSCode extensions [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) format on save.

- Pre-commit hooks automatically format code on commit.

- You can run them manually to debug formatting issues:

```bash
# Python
uv run ruff check --fix
uv run ruff format

# Other files
npx prettier --write "**/*.{json,md,yaml,yml,js}"
```
