# Gemini Robot 🤖

Gemini Robot is a Python-based intelligent assistant that uses Google's Gemini AI to help you find and organize files on your computer using natural language commands.

## Features

- **Natural Language Interface**: Chat with the robot to give commands.
- **Find Files**: Ask the robot to find files with specific extensions (e.g., "Find all PDF files").
- **Organize Files**: Command the robot to move files into specific folders (e.g., "Move all text files to a folder named 'Notes'").

## Prerequisites

- Python 3.8+
- A Google Cloud Project with the Gemini API enabled.
- A Gemini API Key.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rakeshkumar272/antigravity_work.git
    cd antigravity_work
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GEMINI_API_KEY=your_actual_api_key_here
    ```

## Usage

Run the robot script:

```bash
python gemini_robot.py
```

### Example Commands

- "Find all .pdf files in my Documents folder."
- "Organize all .jpg files in D:/Downloads into a folder named 'Images'."

## License

[MIT](https://choosealicense.com/licenses/mit/)
