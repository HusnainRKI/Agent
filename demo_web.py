#!/usr/bin/env python3
"""
Simple Demo Web App - Shows the interface working without complex dependencies
This demonstrates the ChatGPT-like interface with simulated agent responses.
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# Simple HTML template with inline demo functionality
DEMO_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Browser Agent - Web Interface Demo</title>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }
        
        .app-container {
            display: flex;
            height: 100vh;
            background: #f8f9fa;
        }
        
        /* Sidebar */
        .sidebar {
            width: 300px;
            background: #2c3e50;
            color: white;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #34495e;
        }
        
        .sidebar-header {
            padding: 20px;
            background: #34495e;
            border-bottom: 1px solid #4a5f7a;
        }
        
        .sidebar-header h1 {
            font-size: 1.4rem;
            margin-bottom: 5px;
            color: #ecf0f1;
        }
        
        .sidebar-header p {
            color: #bdc3c7;
            font-size: 0.9rem;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 15px;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #27ae60;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .status-text {
            font-size: 0.85rem;
            color: #bdc3c7;
        }
        
        .browser-info {
            padding: 20px;
            border-bottom: 1px solid #34495e;
        }
        
        .browser-info h3 {
            font-size: 1rem;
            margin-bottom: 10px;
            color: #ecf0f1;
        }
        
        .browser-url {
            background: rgba(0,0,0,0.2);
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #bdc3c7;
            word-break: break-all;
            margin-bottom: 8px;
        }
        
        .browser-title {
            font-size: 0.85rem;
            color: #ecf0f1;
            margin-bottom: 15px;
        }
        
        .action-buttons {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .btn-small {
            padding: 6px 12px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .btn-small:hover {
            background: #2980b9;
        }
        
        /* Main Chat Area */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
        }
        
        .chat-header {
            padding: 15px 20px;
            background: white;
            border-bottom: 1px solid #e1e5e9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chat-header h2 {
            color: #2c3e50;
            font-size: 1.3rem;
            margin-bottom: 5px;
        }
        
        .chat-subtitle {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            position: relative;
            animation: messageSlideIn 0.3s ease-out;
        }
        
        @keyframes messageSlideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            align-self: flex-end;
            background: #007AFF;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.agent {
            align-self: flex-start;
            background: #f1f3f5;
            color: #2c3e50;
            border-bottom-left-radius: 4px;
            border: 1px solid #e1e5e9;
        }
        
        .message-content {
            margin: 0;
            line-height: 1.4;
        }
        
        .message-time {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 5px;
        }
        
        .typing-indicator {
            align-self: flex-start;
            background: #f1f3f5;
            border: 1px solid #e1e5e9;
            padding: 16px;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            display: none;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
            align-items: center;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background: #7f8c8d;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .typing-dot:nth-child(2) { animation-delay: -0.16s; }
        .typing-dot:nth-child(3) { animation-delay: 0s; }
        
        @keyframes typingBounce {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .typing-text {
            margin-left: 10px;
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        
        /* Input Area */
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e1e5e9;
        }
        
        .input-wrapper {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }
        
        .message-input {
            flex: 1;
            min-height: 44px;
            max-height: 120px;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 22px;
            resize: none;
            font-family: inherit;
            font-size: 0.95rem;
            line-height: 1.4;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .message-input:focus {
            border-color: #007AFF;
        }
        
        .message-input::placeholder {
            color: #7f8c8d;
        }
        
        .send-button {
            width: 44px;
            height: 44px;
            background: #007AFF;
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s, transform 0.1s;
            font-size: 1.1rem;
        }
        
        .send-button:hover {
            background: #0056b3;
            transform: scale(1.05);
        }
        
        .welcome-message {
            text-align: center;
            color: #7f8c8d;
            margin: 40px 20px;
        }
        
        .welcome-message h3 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .demo-note {
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin: 20px;
            text-align: center;
        }
        
        .demo-note strong {
            color: #0a3d42;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h1>🤖 AI Browser Agent</h1>
                <p>Web Interface v1.0</p>
                
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span class="status-text">Ready</span>
                </div>
            </div>
            
            <div class="browser-info">
                <h3>🌐 Browser Session</h3>
                <div class="browser-url">https://www.google.com</div>
                <div class="browser-title">Google</div>
                
                <div class="action-buttons">
                    <button class="btn-small" onclick="showDemo()">📸 Screenshot</button>
                    <button class="btn-small" onclick="updateInfo()">🔄 Refresh Info</button>
                </div>
            </div>
        </div>
        
        <!-- Main Chat Area -->
        <div class="chat-container">
            <div class="chat-header">
                <h2>Browser Automation Chat</h2>
                <p class="chat-subtitle">Give me instructions and I'll automate your browser tasks</p>
            </div>
            
            <div class="demo-note">
                <strong>🎯 Demo Interface:</strong> This shows the complete ChatGPT-like web interface for the AI Browser Agent. 
                The real implementation includes live browser automation, WebSocket communication, and screenshot capture.
            </div>
            
            <div class="messages-container" id="messagesContainer">
                <div class="welcome-message">
                    <h3>👋 Welcome to AI Browser Agent Web Interface!</h3>
                    <p>This modern web interface replaces the terminal-based agent with a ChatGPT-like experience.</p>
                    <p>Try the demo by typing commands like "Navigate to Google" or "Search for AI news"</p>
                </div>
                
                <div class="message agent">
                    <p class="message-content">Hi! I'm your AI Browser Agent. I can help you automate web tasks through this modern interface.</p>
                    <div class="message-time">9:30:00 PM</div>
                </div>
                
                <div class="typing-indicator" id="typingIndicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                    <span class="typing-text">Agent is thinking...</span>
                </div>
            </div>
            
            <div class="input-container">
                <div class="input-wrapper">
                    <textarea 
                        id="messageInput" 
                        class="message-input" 
                        placeholder="Type your browser automation request here..."
                        rows="1"
                        onkeydown="handleKeyPress(event)"
                    ></textarea>
                    <button id="sendButton" class="send-button" onclick="sendMessage()">
                        ➤
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let messageCount = 0;
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            showTyping();
            
            // Simulate agent response
            setTimeout(() => {
                hideTyping();
                
                let response = '';
                if (message.toLowerCase().includes('navigate') || message.toLowerCase().includes('go to')) {
                    response = `I'll navigate to the requested page. In the real implementation, I would use Selenium WebDriver to control the browser and navigate to the specified URL.`;
                } else if (message.toLowerCase().includes('search')) {
                    response = `I'll search for "${message.replace(/search for|search/gi, '').trim()}". The real implementation would locate the search box and enter your query.`;
                } else if (message.toLowerCase().includes('screenshot')) {
                    response = `I'll take a screenshot of the current browser page. The real implementation would capture and display the actual browser content.`;
                } else {
                    response = `I understand you want to: "${message}". In the full implementation, I would process this request using the browser automation system and perform the appropriate actions.`;
                }
                
                addMessage(response, 'agent');
                addMessage('Actions completed: analyze_request ✓, execute_action ✓, update_status ✓', 'agent', true);
            }, 2000);
        }
        
        function addMessage(text, type, isSubtle = false) {
            const container = document.getElementById('messagesContainer');
            const typingIndicator = document.getElementById('typingIndicator');
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            if (isSubtle) messageDiv.style.opacity = '0.8';
            
            const contentP = document.createElement('p');
            contentP.className = 'message-content';
            contentP.textContent = text;
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.textContent = new Date().toLocaleTimeString();
            
            messageDiv.appendChild(contentP);
            messageDiv.appendChild(timeDiv);
            
            container.insertBefore(messageDiv, typingIndicator);
            container.scrollTop = container.scrollHeight;
        }
        
        function showTyping() {
            document.getElementById('typingIndicator').style.display = 'block';
            document.getElementById('messagesContainer').scrollTop = document.getElementById('messagesContainer').scrollHeight;
        }
        
        function hideTyping() {
            document.getElementById('typingIndicator').style.display = 'none';
        }
        
        function showDemo() {
            alert('Screenshot feature: In the real implementation, this would display a live screenshot of the browser session in a modal window.');
        }
        
        function updateInfo() {
            document.querySelector('.browser-url').textContent = 'https://example.com/updated-page';
            document.querySelector('.browser-title').textContent = 'Updated Page Title';
            addMessage('Browser info refreshed successfully!', 'agent', true);
        }
        
        // Auto-resize textarea
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        console.log('🚀 AI Browser Agent Web Interface Demo Loaded');
        console.log('📱 Modern ChatGPT-like interface for browser automation');
        console.log('🌐 Real implementation includes live WebSocket communication');
    </script>
</body>
</html>
"""

@app.route('/')
def demo():
    return render_template_string(DEMO_TEMPLATE)

if __name__ == '__main__':
    print("🌐 AI Browser Agent - Demo Web Interface")
    print("🚀 Starting demo server on http://localhost:8080")
    print("📱 This demonstrates the ChatGPT-like interface design")
    print("💡 The real implementation (web_app.py) includes live browser automation")
    
    app.run(host='0.0.0.0', port=8080, debug=True)