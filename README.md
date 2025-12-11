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
    We use `uv` for dependency management. Run the following command to sync the environment and install all required packages:
    ```bash
    uv sync
    ```
    This command will automatically create a virtual environment in `.venv` and install the locked dependencies.

## Usage

To run the main application:

```bash
uv run main.py
```

## Development

### Formatting

This project uses automated formatting and linting tools to maintain code quality:

- **Ruff**: For Python linting and formatting
- **Prettier**: For formatting JSON, Markdown, YAML, and JavaScript files

### Pre-commit Hooks

Pre-commit hooks are configured to automatically format and lint your code before each commit. The hooks will:

- Run `ruff check --fix` on Python files to lint and auto-fix issues
- Run `ruff format` on Python files to format code
- Run `prettier` on JSON, Markdown, YAML, and JavaScript files

**Installation**: The hooks are automatically installed when you run `pre-commit install`. If you need to reinstall them:

```bash
pre-commit install
```

**Testing**: You can manually run all hooks on all files:

```bash
pre-commit run --all-files
```

### VSCode Integration

The project includes VSCode settings for automatic formatting:

- **Python files**: Uses the Ruff extension (`charliermarsh.ruff`) with:

  - Format on save enabled
  - Auto-fix on save enabled
  - Import organization on save enabled

- **Other files** (JSON, Markdown, YAML, JavaScript): Uses Prettier with:
  - Format on save enabled
  - Requires a Prettier config file

Make sure you have the following VSCode extensions installed:

- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)

### Running Manually

You can also run the formatting and linting tools manually:

**Python (Ruff)**:

```bash
# Check for linting issues and auto-fix
uv run ruff check --fix

# Format Python code
uv run ruff format
```

**Other files (Prettier)**:

```bash
# Format all supported files
npx prettier --write "**/*.{json,md,yaml,yml,js}"
```
