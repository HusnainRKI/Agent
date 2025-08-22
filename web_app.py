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
                'browser_title': 'New Tab'
            }
            
            self.sessions[session_id] = session_data
            logger.info(f"Created new session: {session_id}")
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
                
                # Take screenshot
                agent = session['agent']
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
                logger.error(f"Error capturing screenshot: {e}")
                emit('error', {'message': f'Screenshot error: {str(e)}'})
        
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
                    emit('browser_info', {
                        'url': 'about:blank',
                        'title': 'Browser not ready',
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
                'message': 'Agent is working on your request...'
            }, room=session_id)
            
            # Initialize the agent if needed
            if not hasattr(agent, 'driver') or agent.driver is None:
                agent._initialize_driver()
                agent._initialize_advanced_visual_elements()
            
            # Process the objective with the agent
            # This is a simplified version - you might want to integrate this more deeply
            # with the existing agent's process_objective method
            
            # For now, let's simulate agent processing and provide a response
            import time
            time.sleep(2)  # Simulate processing time
            
            # Create agent response
            agent_response = {
                'type': 'agent',
                'content': f'I received your message: "{message}". I\'m now processing this request using the browser automation system. This is a demonstration of the web interface integration.',
                'timestamp': datetime.now().isoformat(),
                'actions_taken': [
                    {'action': 'analyze_request', 'status': 'completed'},
                    {'action': 'prepare_browser', 'status': 'completed'},
                    {'action': 'ready_for_execution', 'status': 'pending'}
                ]
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