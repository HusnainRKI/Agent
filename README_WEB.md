# AI Browser Agent - Web Interface

## Overview

This project has been transformed from a terminal-based AI browser agent into a modern web application with a ChatGPT-like interface. Users can now interact with the browser automation agent through a sleek web interface instead of terminal commands.

## Features

### 🌐 Modern Web Interface
- **ChatGPT-like Design**: Clean, modern interface similar to popular chat applications
- **Real-time Communication**: WebSocket-based real-time messaging between user and agent
- **Responsive Layout**: Works on desktop and mobile devices
- **Dark/Light Theme**: Professional sidebar with modern color scheme

### 🤖 Browser Automation
- **Natural Language Commands**: Give instructions in plain English
- **Live Browser Control**: Real-time browser automation with visual feedback
- **Screenshot Capture**: View live screenshots of the browser session
- **Session Management**: Multiple user sessions with isolated browser instances

### 💬 Chat Interface Features
- **Message Bubbles**: User and agent messages with timestamps
- **Typing Indicators**: Shows when the agent is processing requests
- **Status Updates**: Real-time status of browser automation tasks
- **Error Handling**: Graceful error messages and recovery

### 📸 Browser Session Features
- **Live URL Display**: Shows current browser URL and page title
- **Screenshot Modal**: View full-screen browser screenshots
- **Session Info**: Real-time browser session information
- **Action History**: Track all automation actions performed

## Installation & Setup

### Prerequisites
- Python 3.8+
- Chrome browser installed
- Required Python packages (see requirements.txt)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd Agent

# Install dependencies
pip install -r requirements.txt

# Run the web application
python web_app.py
```

### Alternative: Run with custom host/port
```bash
python web_app.py --host 0.0.0.0 --port 8080 --debug
```

## Usage

### Starting the Web Interface
1. Run `python web_app.py`
2. Open your browser and navigate to `http://localhost:5000`
3. Wait for the connection status to show "Ready"
4. Start giving commands to the AI agent

### Example Commands
- **Navigation**: "Navigate to Google" or "Go to GitHub"
- **Search**: "Search for AI news" (after navigating to Google)
- **Screenshots**: "Take a screenshot" or click the screenshot button
- **General**: Any browser automation task in natural language

### Interface Components

#### Sidebar
- **Connection Status**: Shows if the agent is connected and ready
- **Browser Info**: Current URL and page title
- **Action Buttons**: Screenshot and refresh browser info

#### Chat Area
- **Message History**: Conversation between user and agent
- **Input Field**: Type your commands here
- **Send Button**: Submit commands to the agent

#### Features
- **Screenshot Modal**: Click screenshot button to view browser content
- **Real-time Updates**: Browser info updates automatically
- **Error Messages**: Clear error feedback when issues occur

## Architecture

### Backend (Flask + SocketIO)
- **Web Server**: Flask application serving the web interface
- **WebSocket Server**: Flask-SocketIO for real-time communication
- **Session Management**: Isolated browser sessions per user
- **Agent Integration**: Connects to the existing MegaAdvancedBrowserAgent

### Frontend (HTML + JavaScript)
- **Modern HTML5**: Semantic markup with accessibility features
- **CSS3 Styling**: Modern design with animations and transitions
- **WebSocket Client**: Real-time bidirectional communication
- **Responsive Design**: Mobile-friendly interface

### Agent Integration
- **Browser Automation**: Uses existing Selenium-based agent
- **Command Processing**: Natural language command interpretation
- **Screenshot Capture**: Real-time browser screenshot functionality
- **Session Isolation**: Each user gets their own browser instance

## Development

### File Structure
```
Agent/
├── web_app.py              # Main web application
├── agent.py                # Original terminal-based agent
├── templates/
│   └── index.html          # Web interface template
├── static/
│   └── js/
│       └── socketio-demo.js # Demo client (for testing)
├── requirements.txt        # Python dependencies
└── README_WEB.md          # This file
```

### Key Components

#### WebAgentApp Class
Main Flask application class that handles:
- Web server setup and routing
- WebSocket event handling
- Session management
- Agent integration

#### SessionManager Class
Manages browser agent sessions:
- Session creation and cleanup
- User isolation
- Browser instance management
- Activity tracking

#### Socket Events
- `connect/disconnect`: Client connection handling
- `initialize_session`: Create new browser session
- `send_message`: Process user commands
- `get_browser_screenshot`: Capture browser screenshots
- `get_browser_info`: Get current browser state

## Browser Commands

The agent understands various natural language commands:

### Navigation Commands
- "Navigate to [website]" - Go to a specific website
- "Go to Google" - Navigate to Google.com
- "Visit GitHub" - Navigate to GitHub.com

### Search Commands
- "Search for [query]" - Search on the current page (if it's a search engine)
- "Find [information]" - Search for specific information

### Action Commands
- "Take a screenshot" - Capture current browser view
- "Click [element]" - Click on page elements
- "Fill [form]" - Fill out forms
- "Scroll down/up" - Scroll the page

### Information Commands
- "What's on this page?" - Get page information
- "Show me the current URL" - Display current page URL
- "Get page title" - Show the page title

## API Endpoints

### REST Endpoints
- `GET /` - Main web interface
- `GET /api/health` - Health check
- `GET /api/sessions` - List active sessions

### WebSocket Events
- `connect` - Client connection
- `disconnect` - Client disconnection
- `initialize_session` - Start new session
- `send_message` - Send command to agent
- `get_browser_screenshot` - Request screenshot
- `get_browser_info` - Get browser state

## Security Considerations

- **Session Isolation**: Each user gets isolated browser sessions
- **Input Sanitization**: User commands are validated
- **Error Handling**: Graceful error recovery
- **Resource Management**: Automatic session cleanup

## Troubleshooting

### Common Issues

1. **"Socket.IO connection failed"**
   - Check if the web server is running
   - Verify port 5000 is available
   - Try refreshing the page

2. **"Browser session not initialized"**
   - Send a navigation command first
   - Check Chrome browser is installed
   - Verify webdriver permissions

3. **"Screenshot failed"**
   - Ensure browser is navigated to a page
   - Check filesystem permissions
   - Try taking a screenshot via command

### Debug Mode
Run with debug flag for detailed logging:
```bash
python web_app.py --debug
```

## Future Enhancements

- **Multi-tab Support**: Handle multiple browser tabs
- **User Authentication**: User accounts and session persistence
- **Command History**: Save and replay command sequences
- **AI Integration**: Enhanced AI reasoning and planning
- **Mobile App**: Native mobile application
- **Collaborative Features**: Share sessions between users

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add license information here]

---

**Note**: This web interface provides a modern alternative to the terminal-based agent while preserving all the powerful browser automation capabilities of the original system.