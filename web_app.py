#!/usr/bin/env python3
"""
Web Application for AI Browser Agent
Transforms the terminal-based agent into a modern web application with ChatGPT-like interface.
"""

import os
import json
import time
import threading
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# Import the existing agent
from agent import MegaAdvancedBrowserAgent
# Import Selenium components needed for web actions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SessionManager:
    """Manages browser agent sessions for multiple users."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def create_session(self, session_id: str, user_data: Dict = None) -> Dict:
        """Create a new browser agent session."""
        with self.lock:
            if session_id in self.sessions:
                return self.sessions[session_id]
            
            # Create new agent instance for this session
            try:
                agent = MegaAdvancedBrowserAgent(
                    headless=False,  # Set to True for production
                    window_size=(1920, 1080),
                    enable_extensions=True,
                    enable_ai=True,
                    multi_browser=False,
                    browser_count=1
                )
                
                session_data = {
                    'id': session_id,
                    'agent': agent,
                    'created_at': datetime.now(),
                    'last_activity': datetime.now(),
                    'status': 'initialized',
                    'user_data': user_data or {},
                    'message_history': [],
                    'browser_url': 'about:blank',
                    'browser_title': 'New Tab',
                    'browser_initialized': False
                }
                
                self.sessions[session_id] = session_data
                logger.info(f"Created new session: {session_id}")
                return session_data
                
            except Exception as e:
                logger.error(f"Error creating session {session_id}: {e}")
                # Create a minimal session even if agent creation fails
                session_data = {
                    'id': session_id,
                    'agent': None,
                    'created_at': datetime.now(),
                    'last_activity': datetime.now(),
                    'status': 'error',
                    'user_data': user_data or {},
                    'message_history': [],
                    'browser_url': 'Error',
                    'browser_title': 'Failed to initialize',
                    'browser_initialized': False,
                    'error': str(e)
                }
                self.sessions[session_id] = session_data
                return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def update_activity(self, session_id: str):
        """Update last activity timestamp."""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['last_activity'] = datetime.now()
    
    def cleanup_session(self, session_id: str):
        """Clean up and remove session."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                try:
                    if 'agent' in session and session['agent']:
                        session['agent'].cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up session {session_id}: {e}")
                finally:
                    del self.sessions[session_id]
                    logger.info(f"Cleaned up session: {session_id}")

class WebAgentApp:
    """Main web application class."""
    
    def __init__(self, host='0.0.0.0', port=5000, debug=False):
        self.app = Flask(__name__, static_folder='static', static_url_path='/static')
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        
        # Configure CORS
        CORS(self.app, cors_allowed_origins="*")
        
        # Initialize SocketIO
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='eventlet',
            logger=False,
            engineio_logger=False
        )
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
        # Setup routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()
        
        self.host = host
        self.port = port
        self.debug = debug
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main chat interface."""
            return render_template('index.html')
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'active_sessions': len(self.session_manager.sessions)
            })
        
        @self.app.route('/api/sessions')
        def list_sessions():
            """List active sessions."""
            sessions = []
            for session_id, session_data in self.session_manager.sessions.items():
                sessions.append({
                    'id': session_id,
                    'created_at': session_data['created_at'].isoformat(),
                    'last_activity': session_data['last_activity'].isoformat(),
                    'status': session_data['status'],
                    'browser_url': session_data['browser_url'],
                    'browser_title': session_data['browser_title']
                })
            return jsonify({'sessions': sessions})
    
    def _setup_socket_handlers(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'status': 'connected', 'session_id': request.sid})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info(f"Client disconnected: {request.sid}")
            # Clean up session if it exists
            self.session_manager.cleanup_session(request.sid)
        
        @self.socketio.on('initialize_session')
        def handle_initialize_session(data):
            """Initialize a new browser agent session."""
            try:
                session_id = request.sid
                user_data = data.get('user_data', {})
                
                # Create session
                session = self.session_manager.create_session(session_id, user_data)
                
                # Join room for this session
                join_room(session_id)
                
                emit('session_initialized', {
                    'session_id': session_id,
                    'status': 'ready',
                    'message': 'Browser agent session initialized successfully!'
                })
                
                logger.info(f"Session initialized: {session_id}")
                
            except Exception as e:
                logger.error(f"Error initializing session: {e}")
                emit('error', {'message': f'Failed to initialize session: {str(e)}'})
        
        @self.socketio.on('send_message')
        def handle_message(data):
            """Handle user message and process with agent."""
            try:
                session_id = request.sid
                message = data.get('message', '').strip()
                
                if not message:
                    emit('error', {'message': 'Empty message received'})
                    return
                
                session = self.session_manager.get_session(session_id)
                if not session:
                    emit('error', {'message': 'Session not found. Please refresh the page.'})
                    return
                
                # Update activity
                self.session_manager.update_activity(session_id)
                
                # Add user message to history
                user_msg = {
                    'type': 'user',
                    'content': message,
                    'timestamp': datetime.now().isoformat()
                }
                session['message_history'].append(user_msg)
                
                # Emit user message confirmation
                emit('message_received', user_msg)
                
                # Show typing indicator
                emit('typing_start', {'type': 'agent'})
                
                # Process message with agent in a separate thread
                threading.Thread(
                    target=self._process_agent_message,
                    args=(session_id, message),
                    daemon=True
                ).start()
                
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                emit('error', {'message': f'Error processing message: {str(e)}'})
        
        @self.socketio.on('get_browser_screenshot')
        def handle_screenshot_request():
            """Get current browser screenshot."""
            try:
                session_id = request.sid
                session = self.session_manager.get_session(session_id)
                
                if not session or not session.get('agent'):
                    emit('error', {'message': 'No active session found'})
                    return
                
                agent = session['agent']
                
                # Check if browser is initialized
                if not hasattr(agent, 'driver') or agent.driver is None:
                    emit('error', {'message': 'Browser session not initialized. Please send a command first.'})
                    return
                
                # Take screenshot
                try:
                    screenshot_path = agent.save_advanced_screenshot()
                    
                    if screenshot_path and os.path.exists(screenshot_path):
                        # Convert to base64
                        with open(screenshot_path, 'rb') as f:
                            screenshot_data = base64.b64encode(f.read()).decode()
                        
                        emit('browser_screenshot', {
                            'image_data': f"data:image/png;base64,{screenshot_data}",
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        emit('error', {'message': 'Failed to capture screenshot'})
                except Exception as e:
                    logger.error(f"Screenshot capture error: {e}")
                    emit('error', {'message': f'Screenshot error: {str(e)}'})
                    
            except Exception as e:
                logger.error(f"Error handling screenshot request: {e}")
                emit('error', {'message': f'Screenshot request error: {str(e)}'})
        
        @self.socketio.on('get_browser_info')
        def handle_browser_info_request():
            """Get current browser information."""
            try:
                session_id = request.sid
                session = self.session_manager.get_session(session_id)
                
                if not session or not session.get('agent'):
                    emit('error', {'message': 'No active session found'})
                    return
                
                agent = session['agent']
                
                # Check if browser is initialized
                if not hasattr(agent, 'driver') or agent.driver is None:
                    emit('browser_info', {
                        'url': 'about:blank',
                        'title': 'Browser not initialized',
                        'timestamp': datetime.now().isoformat()
                    })
                    return
                
                # Get browser info
                try:
                    current_url = agent.driver.current_url
                    page_title = agent.driver.title
                    
                    # Update session data
                    session['browser_url'] = current_url
                    session['browser_title'] = page_title
                    
                    emit('browser_info', {
                        'url': current_url,
                        'title': page_title,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Browser info error: {e}")
                    emit('browser_info', {
                        'url': 'Error getting URL',
                        'title': 'Error getting title',
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"Error getting browser info: {e}")
                emit('error', {'message': f'Browser info error: {str(e)}'})
    
    def _process_agent_message(self, session_id: str, message: str):
        """Process message with the agent in a separate thread."""
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                return
            
            agent = session['agent']
            
            # Update session status
            session['status'] = 'processing'
            
            # Emit status update
            self.socketio.emit('status_update', {
                'status': 'processing',
                'message': 'Agent is analyzing your request...'
            }, room=session_id)
            
            # Initialize the agent if needed
            if not hasattr(agent, 'driver') or agent.driver is None:
                try:
                    agent._initialize_driver()
                    agent._initialize_advanced_visual_elements()
                    
                    # Navigate to a blank page initially
                    agent.driver.get("about:blank")
                    
                    self.socketio.emit('status_update', {
                        'status': 'processing',
                        'message': 'Browser session initialized. Processing your request...'
                    }, room=session_id)
                    
                except Exception as e:
                    logger.error(f"Error initializing agent driver: {e}")
                    self.socketio.emit('error', {
                        'message': f'Failed to initialize browser session: {str(e)}'
                    }, room=session_id)
                    return
            
            # Process the objective with a simplified approach
            # For demo purposes, we'll perform basic navigation based on the message
            response_content = ""
            actions_taken = []
            
            try:
                # Simple command parsing
                message_lower = message.lower()
                
                if "navigate" in message_lower or "go to" in message_lower:
                    # Extract URL or domain
                    if "google" in message_lower:
                        agent.driver.get("https://www.google.com")
                        response_content = "I navigated to Google.com as requested."
                        actions_taken.append({'action': 'navigate_to_google', 'status': 'completed'})
                    elif "github" in message_lower:
                        agent.driver.get("https://github.com")
                        response_content = "I navigated to GitHub.com as requested."
                        actions_taken.append({'action': 'navigate_to_github', 'status': 'completed'})
                    elif "example" in message_lower:
                        agent.driver.get("https://example.com")
                        response_content = "I navigated to Example.com as requested."
                        actions_taken.append({'action': 'navigate_to_example', 'status': 'completed'})
                    else:
                        response_content = "I understand you want to navigate somewhere. Please specify a clear URL or website name (e.g., 'go to Google', 'navigate to GitHub')."
                        actions_taken.append({'action': 'parse_navigation_request', 'status': 'completed'})
                
                elif "search" in message_lower:
                    if hasattr(agent, 'driver') and agent.driver.current_url:
                        current_url = agent.driver.current_url
                        if "google.com" in current_url:
                            # Try to find and use search box
                            try:
                                search_box = agent.driver.find_element(By.NAME, "q")
                                search_terms = message.replace("search for", "").replace("search", "").strip()
                                search_box.send_keys(search_terms)
                                search_box.send_keys(Keys.RETURN)
                                response_content = f"I searched for '{search_terms}' on Google."
                                actions_taken.extend([
                                    {'action': 'find_search_box', 'status': 'completed'},
                                    {'action': 'enter_search_terms', 'status': 'completed'},
                                    {'action': 'submit_search', 'status': 'completed'}
                                ])
                            except Exception as e:
                                response_content = "I tried to search but couldn't find the search box. Please try navigating to Google first."
                                actions_taken.append({'action': 'search_attempt', 'status': 'failed'})
                        else:
                            response_content = "To search, please first navigate to a search engine like Google."
                            actions_taken.append({'action': 'search_validation', 'status': 'completed'})
                    else:
                        response_content = "Please navigate to a search engine first, then I can help you search."
                        actions_taken.append({'action': 'search_prerequisite_check', 'status': 'completed'})
                
                elif "screenshot" in message_lower or "capture" in message_lower:
                    # Take a screenshot using the agent
                    try:
                        screenshot_path = agent.save_advanced_screenshot()
                        if screenshot_path and os.path.exists(screenshot_path):
                            response_content = "I took a screenshot of the current page."
                            actions_taken.append({'action': 'capture_screenshot', 'status': 'completed'})
                            
                            # Send the screenshot via WebSocket
                            with open(screenshot_path, 'rb') as f:
                                screenshot_data = base64.b64encode(f.read()).decode()
                            
                            self.socketio.emit('browser_screenshot', {
                                'image_data': f"data:image/png;base64,{screenshot_data}",
                                'timestamp': datetime.now().isoformat()
                            }, room=session_id)
                        else:
                            response_content = "I attempted to take a screenshot but encountered an issue."
                            actions_taken.append({'action': 'capture_screenshot', 'status': 'failed'})
                    except Exception as e:
                        response_content = f"Screenshot failed: {str(e)}"
                        actions_taken.append({'action': 'capture_screenshot', 'status': 'failed'})
                
                else:
                    # General response for unrecognized commands
                    response_content = f'I received your message: "{message}". I can help you with browser automation tasks like:\n\n• "Navigate to Google" or "Go to GitHub"\n• "Search for AI news" (after navigating to Google)\n• "Take a screenshot"\n\nPlease give me a specific command to execute.'
                    actions_taken.append({'action': 'analyze_request', 'status': 'completed'})
                
                # Update browser info in session
                try:
                    if hasattr(agent, 'driver') and agent.driver:
                        session['browser_url'] = agent.driver.current_url
                        session['browser_title'] = agent.driver.title
                        
                        # Send updated browser info
                        self.socketio.emit('browser_info', {
                            'url': session['browser_url'],
                            'title': session['browser_title'],
                            'timestamp': datetime.now().isoformat()
                        }, room=session_id)
                except:
                    pass  # Ignore browser info errors
                
            except Exception as e:
                logger.error(f"Error processing agent command: {e}")
                response_content = f"I encountered an error while processing your request: {str(e)}"
                actions_taken.append({'action': 'error_handling', 'status': 'failed'})
            
            # Create agent response
            agent_response = {
                'type': 'agent',
                'content': response_content,
                'timestamp': datetime.now().isoformat(),
                'actions_taken': actions_taken
            }
            
            # Add response to history
            session['message_history'].append(agent_response)
            
            # Update session status
            session['status'] = 'ready'
            
            # Stop typing indicator and send response
            self.socketio.emit('typing_stop', room=session_id)
            self.socketio.emit('agent_response', agent_response, room=session_id)
            self.socketio.emit('status_update', {
                'status': 'ready',
                'message': 'Agent is ready for next command'
            }, room=session_id)
            
        except Exception as e:
            logger.error(f"Error processing agent message: {e}")
            
            # Stop typing and send error
            self.socketio.emit('typing_stop', room=session_id)
            self.socketio.emit('error', {
                'message': f'Agent processing error: {str(e)}'
            }, room=session_id)
            
            # Update session status
            if session:
                session['status'] = 'error'
    
    def run(self):
        """Run the web application."""
        logger.info(f"Starting Web Agent App on {self.host}:{self.port}")
        print(f"\n🌐 AI Browser Agent Web Interface")
        print(f"🚀 Server starting on http://{self.host}:{self.port}")
        print(f"📱 Open your browser and navigate to the URL above")
        print(f"💬 Enjoy the ChatGPT-like interface for browser automation!")
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=self.debug,
            use_reloader=False  # Disable reloader to prevent issues with threading
        )

def main():
    """Main entry point for web application."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Browser Agent Web Interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create and run the web app
    web_app = WebAgentApp(host=args.host, port=args.port, debug=args.debug)
    
    try:
        web_app.run()
    except KeyboardInterrupt:
        print("\n⏹️ Shutting down web server...")
        logger.info("Web server shutdown requested")
    except Exception as e:
        logger.error(f"Web server error: {e}")
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()