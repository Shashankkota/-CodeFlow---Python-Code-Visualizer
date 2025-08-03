

# 🚀 CodeFlow - Python Code Visualizer

**CodeFlow** is a powerful, interactive Python code execution visualizer built using Pygame. It allows you to write, execute, and visualize Python code step by step — perfect for learning, debugging, or teaching how Python code flows.

---

## ✨ Features

* 🖋️ **Interactive Code Editor**: Write Python code directly in the GUI.
* 👁️ **Real-time Visualization**: Watch your code run line-by-line.
* 🧠 **AI-Powered Explanations**: Step-by-step line explanations using Groq API.
* 🧪 **Live Variable Tracking**: View variable values, types, and the lines where they were set.
* 🖱️ **Full Mouse & Keyboard Support**: Position cursor with mouse, type any special character.
* ⏱️ **Control Execution**: Step, pause, run, reset — all in your control.
* 🛠️ **Robust Parsing**: Understands loops, conditionals, assignments, and print statements.

---

## 🛠️ Installation

1. **Python 3.7+ is required**
2. Install dependencies:

   ```bash
   pip install pygame requests
   ```

---

## ▶️ How to Run

Run the visualizer with:

```bash
python main.py
```

---

## 🧭 Controls

### ✍️ In Input Mode:

* **Type**: Start typing to add code
* **Click**: Position the cursor
* **Tab**: Indent (adds 4 spaces)
* **Arrow Keys**: Move within the code
* **Backspace/Delete**: Remove characters
* **F5**: Start visualization

> Special Characters like `()[]{}` and operators `+ - * / =` fully supported via Shift.

### 🧩 In Visualization Mode:

* **Space**: Step through code
* **R**: Run remaining lines
* **P**: Pause execution
* **Backspace**: Reset execution
* **F5**: Return to edit mode
* **Up/Down Arrow**: Increase/Decrease execution speed

---

## 💡 Example Code

```python
x = 10
y = 20
z = x + y
print(f"Sum: {z}")

for i in range(3):
    print(f"Count: {i}")
    result = i * 2
    print(f"Double: {result}")
```

---

## 🧱 Architecture Overview

* **Frontend**: Built with Pygame — handles code input, cursor movement, and GUI rendering.
* **Execution Engine**: Parses code into structured lines and simulates execution with variable tracking.
* **AI Explanation Engine**: Integrates with [Groq API](https://groq.com/) to generate natural language explanations for each step.
* **State Management**: Maintains visual state (`is_current`, `is_executed`) and execution data (`variables`, `explanations`, etc.)

---

## 🔐 Security Note

This tool sends user-written code to the Groq API for explanation. Ensure your Groq API key is **kept private** and **not committed to version control**. You can set it via environment variable or configuration file instead of hardcoding it.

---

## 🙋 Contribution Guidelines

* Fork the repo and create a feature branch
* Write clear commits and ensure code passes linting (`flake8` or `black`)
* Avoid hardcoding credentials in the source
* Submit PRs with proper descriptions

---

## 🚪 Exit

To quit the application at any time:

```bash
Ctrl + C
```

---



This project is licensed under the MIT License.

---

Would you like me to refactor or modularize the Python code too? Let me know if you need it split into multiple files (like `editor.py`, `engine.py`, etc.) or cleaned up for distribution.
