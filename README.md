# Mega Advanced AI Browser Agent 🤖

Welcome to the Mega Advanced AI Browser Agent, a sophisticated autonomous agent designed to navigate and interact with the web to achieve complex objectives using the power of large language models.

This isn't just a simple automation script. It's a powerful framework that provides rich, real-time visual feedback directly within the browser, simulating a human-like interaction flow. The agent analyzes web pages, decides on the best course of action, and executes it, all while showing you its thought process through an elegant in-browser UI.


---

## ✨ Features

This project is packed with over 50 advanced features, making it a robust platform for web automation.

#### 🧠 **AI-Powered Core**
*   **Natural Language Control:** Give the agent complex objectives in plain English.
*   **AI Decision Making:** Utilizes a large language model to analyze the screen and decide the next best action.
*   **Streaming AI Responses:** The agent's thoughts and decisions are streamed in real-time for better observability.
*   **Confidence Scoring:** The AI provides a confidence score for each decision it makes.

#### 🎨 **Rich Visual Feedback & In-Browser UI**
*   **Human-like Cursor Movement:** A custom-rendered cursor moves smoothly between elements with realistic, multi-step animations.
*   **Clean Chat Interface:** A modern, minimal speech bubble UI displays AI thoughts, analysis, and status updates.
*   **AI Avatar & Typing Indicator:** An AI avatar and typing indicator create a more intuitive user experience.
*   **Live Element Annotation:** Screenshots are automatically annotated with numbered labels on all interactive elements.
*   **Dynamic Progress Indicators:** Professional progress rings and status bars show the agent's current state.

#### 🛠️ **Advanced Browser Automation**
*   **Comprehensive Action Library:** Supports over 20 actions, including `NAVIGATE`, `CLICK`, `TYPE`, `SCROLL`, `HOVER`, `EXECUTE_JS`, and more.
*   **Robust Element Detection:** Identifies all interactive elements on a page, including those within `iframes`.
*   **Multi-Strategy Interaction:** Uses a cascade of strategies (e.g., WebDriver click, JavaScript click) to ensure successful interactions.
*   **Auto-Detection:** Automatically finds the most relevant input field for a given task, like a search bar.
*   **Advanced Error Handling & Recovery:** The agent is designed to be resilient, with multiple retry mechanisms and failure detection.

#### 📊 **Reporting & Logging**
*   **SQLite Database Logging:** Every action and session detail is logged to a local SQLite database for analysis.
*   **Professional HTML Reports:** Automatically generate a comprehensive HTML report at the end of each session with stats, timelines, and screenshots.
*   **Action-Level Screenshots:** A screenshot is saved for every single action, whether it succeeds or fails, providing a complete visual audit trail.
*   **Email Notifications:** Can be configured to automatically email session reports.
*   **Detailed Session Analytics:** Tracks success rates, actions per minute, total duration, and other key performance indicators.

---

## 🚀 How It Works

The agent operates in a continuous loop, observing the screen, thinking, and acting.

1.  **User Objective:** You provide a high-level goal, like `"Go to Google, search for the latest AI news, and summarize the top result."`
2.  **Observe:** The agent captures the current state of the web page.
3.  **Analyze & Annotate:** It identifies all interactive elements (buttons, links, inputs) and generates a screenshot, drawing numbered labels over each element.
4.  **Think:** The annotated screenshot, the objective, and the history of past actions are sent to the AI model. The AI analyzes the visual information and returns a structured JSON response containing its `thought` process and the next `action` to take (e.g., `{"action": {"name": "TYPE", "parameters": {"id": 5, "text": "latest AI news"}}}`).
5.  **Act:** The agent parses the AI's decision and executes the specified action using Selenium WebDriver. The custom UI (cursor, bubbles) provides visual feedback on this action.
6.  **Log & Repeat:** The result of the action is logged to the database. The loop repeats until the objective is marked as complete by the AI.

---

## 📦 Installation & Setup

Follow these steps to get the agent up and running.

#### **1. Prerequisites**
*   Python 3.8+
*   Google Chrome browser installed

#### **2. Clone the Repository**
```bash
git clone https://github.com/Niansuh/Agent.git
cd Agent
```

#### **3. Create a Virtual Environment**
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### **4. Install Dependencies**
Create a `requirements.txt` file with the following contents:

```txt
selenium
webdriver-manager
requests
python-dotenv
Pillow
numpy
opencv-python
```

Then, install them using pip:
```bash
pip install -r requirements.txt
```

#### **5. Configure Environment Variables**
Create a file named `.env` in the root of the project and add your credentials. This is crucial for the AI and email functionality.

```env
# AI Model Configuration (compatible with OpenAI's API format)
API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
API_ENDPOINT_URL="https://your-ai-provider-api.com/v1/chat/completions"
MODEL_NAME="your-chosen-model-name"

# Email Configuration (Optional - for sending reports)
EMAIL_FROM="your-email@gmail.com"
EMAIL_USERNAME="your-email@gmail.com"
EMAIL_PASSWORD="your-gmail-app-password"
```
**Note:** For Gmail, you will need to generate an "App Password" to use here.

---

## 🏃‍♀️ Running the Agent

To start the agent, run the main script from your terminal:

```bash
python your_script_name.py
```

The script will initialize, open a Chrome browser window, and you will be prompted to enter an objective in the console.

#### **Example Objectives**
*   `go to wikipedia.org and search for "Quantum Computing"`
*   `open youtube.com, find a channel called "MKBHD", and click on the latest video`
*   `navigate to github.com and find trending python repositories`

#### **Special Commands**
You can also enter special commands at the prompt:
*   `exit`: Shuts down the agent and generates a final report.
*   `report`: Generates and saves an HTML report for the current session.
*   `stats`: Displays the latest session statistics in the console.
*   `history`: Shows a log of the most recent actions taken.
*   `screenshot`: Manually takes and saves an annotated screenshot.
*   `chat`: Runs a short demo of the in-browser chat UI features.
*   `help`: Displays a list of available commands and tips.

---

## 📁 Project Structure

```
.
├── data/                  # SQLite database files
├── downloads/             # Files downloaded by the agent
├── logs/                  # Detailed .log files for debugging
├── reports/               # Generated HTML session reports
├── screenshots/           # All screenshots taken by the agent
├── .env                   # Environment variables (API keys, etc.)
├── your_script_name.py    # The main Python script
└── README.md              # This file
```
