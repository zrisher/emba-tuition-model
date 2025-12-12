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

Run the simulation to find the optimal tuition price that maximizes final year net revenue:

```bash
uv run cli [years] [-c CONFIG]
```

### Arguments

| Argument         | Description                                            |
| ---------------- | ------------------------------------------------------ |
| `years`          | Number of years to simulate (default: 20)              |
| `-c`, `--config` | Path to a custom config file (uses default if omitted) |

### Examples

```bash
uv run cli              # Run 20-year simulation with default config
uv run cli 10           # Run 10-year simulation
uv run cli -c my.json   # Use custom config file
uv run cli 15 -c my.json  # 15 years with custom config
```

### Output

The CLI outputs:

- **Optimal tuition**: The per-credit tuition that maximizes final year revenue
- **Year-by-year results**: Awareness, preference, alumni count, enrollment, and net revenue for each year

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
