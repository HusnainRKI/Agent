// Simple Socket.IO Client stub for offline testing
// This creates a minimal Socket.IO-compatible interface for development

(function() {
    'use strict';
    
    // Simple event emitter
    function EventEmitter() {
        this.events = {};
    }
    
    EventEmitter.prototype.on = function(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(callback);
    };
    
    EventEmitter.prototype.emit = function(event, data) {
        if (this.events[event]) {
            this.events[event].forEach(callback => {
                try {
                    callback(data);
                } catch(e) {
                    console.error('Socket event error:', e);
                }
            });
        }
        
        // Also log the event for debugging
        console.log('Socket emit:', event, data);
    };
    
    // Simple Socket implementation
    function Socket() {
        EventEmitter.call(this);
        this.connected = false;
        this.id = 'socket_' + Math.random().toString(36).substr(2, 9);
        
        // Simulate connection after a short delay
        setTimeout(() => {
            this.connected = true;
            this.emit('connect');
        }, 100);
    }
    
    // Inherit from EventEmitter
    Socket.prototype = Object.create(EventEmitter.prototype);
    Socket.prototype.constructor = Socket;
    
    Socket.prototype.emit = function(event, data) {
        console.log('Socket send:', event, data);
        
        // For demo purposes, simulate some responses
        if (event === 'initialize_session') {
            setTimeout(() => {
                this.events['session_initialized'] && this.events['session_initialized'].forEach(cb => {
                    cb({
                        session_id: this.id,
                        status: 'ready',
                        message: 'Browser agent session initialized successfully!'
                    });
                });
            }, 500);
        }
        
        if (event === 'send_message') {
            setTimeout(() => {
                this.events['message_received'] && this.events['message_received'].forEach(cb => {
                    cb({
                        type: 'user',
                        content: data.message,
                        timestamp: new Date().toISOString()
                    });
                });
            }, 100);
            
            setTimeout(() => {
                this.events['agent_response'] && this.events['agent_response'].forEach(cb => {
                    cb({
                        type: 'agent',
                        content: `Demo response: I received your message "${data.message}". In a real setup with API keys, I would process this browser automation request.`,
                        timestamp: new Date().toISOString(),
                        actions_taken: [
                            { action: 'ANALYZE', status: 'completed' }
                        ]
                    });
                });
            }, 1500);
        }
        
        if (event === 'get_browser_info') {
            setTimeout(() => {
                this.events['browser_info'] && this.events['browser_info'].forEach(cb => {
                    cb({
                        url: 'about:blank',
                        title: 'Demo Browser Session',
                        timestamp: new Date().toISOString()
                    });
                });
            }, 200);
        }
        
        if (event === 'get_browser_screenshot') {
            setTimeout(() => {
                this.events['browser_screenshot'] && this.events['browser_screenshot'].forEach(cb => {
                    cb({
                        image_data: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
                        timestamp: new Date().toISOString()
                    });
                });
            }, 300);
        }
        
        // Call parent emit for events
        EventEmitter.prototype.emit.call(this, event, data);
    };
    
    // Create io function
    window.io = function() {
        return new Socket();
    };
    
    console.log('Socket.IO stub loaded for demo purposes');
})();