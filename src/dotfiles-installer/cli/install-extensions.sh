#!/bin/bash

echo "Installing VS Code extensions for Python development..."
echo "========================================================="

# Check if code command is available
if ! command -v code &> /dev/null; then
    echo "❌ VS Code 'code' command not found."
    echo "Please install VS Code and add it to your PATH."
    echo "Or install extensions manually from VS Code marketplace:"
    echo ""
    echo "Required extensions:"
    echo "- Python (ms-python.python)"
    echo "- Black Formatter (ms-python.black-formatter)"
    echo "- isort (ms-python.isort)"
    echo "- Ruff (charliermarsh.ruff)"
    echo "- Mypy Type Checker (ms-python.mypy-type-checker)"
    exit 1
fi

# Array of extensions to install
extensions=(
    "ms-python.python"
    "ms-python.black-formatter"
    "ms-python.isort"
    "charliermarsh.ruff"
    "ms-python.mypy-type-checker"
)

# Install each extension
for ext in "${extensions[@]}"; do
    echo "Installing $ext..."
    if code --install-extension "$ext" --force; then
        echo "✅ $ext installed successfully"
    else
        echo "⚠️  Failed to install $ext (may already be installed)"
    fi
done

echo ""
echo "🎉 Extension installation complete!"
echo ""
echo "Next steps:"
echo "1. Restart VS Code"
echo "2. Open the project from the root directory"
echo "3. VS Code should automatically detect the Python interpreter at:"
echo "   ./src/dotfiles-installer/cli/.venv/bin/python"
echo ""
echo "If the interpreter is not detected automatically:"
echo "1. Press Ctrl+Shift+P"
echo "2. Type 'Python: Select Interpreter'"
echo "3. Choose the interpreter at ./src/dotfiles-installer/cli/.venv/bin/python"
