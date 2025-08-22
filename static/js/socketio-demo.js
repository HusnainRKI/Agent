// Simplified Socket.IO client implementation for the demo
// This is a basic implementation to show the interface working
class SocketIOClient {
    constructor() {
        this.connected = false;
        this.callbacks = {};
        this.sessionInitialized = false;
    }
    
    on(event, callback) {
        if (!this.callbacks[event]) {
            this.callbacks[event] = [];
        }
        this.callbacks[event].push(callback);
    }
    
    emit(event, data) {
        console.log('Emitting event:', event, data);
        
        // Simulate real socket behavior for demo
        if (event === 'initialize_session') {
            setTimeout(() => {
                this.trigger('session_initialized', {
                    session_id: 'demo-session',
                    status: 'ready',
                    message: 'Demo session initialized'
                });
            }, 1000);
        } else if (event === 'send_message') {
            this.trigger('message_received', {
                content: data.message,
                timestamp: new Date().toISOString()
            });
            
            setTimeout(() => {
                this.trigger('typing_start', {});
            }, 500);
            
            setTimeout(() => {
                this.trigger('typing_stop', {});
                this.trigger('agent_response', {
                    content: `Demo response: I received your message "${data.message}". In a real implementation, I would process this request using the browser agent.`,
                    timestamp: new Date().toISOString(),
                    actions_taken: [
                        {action: 'parse_request', status: 'completed'},
                        {action: 'demo_response', status: 'completed'}
                    ]
                });
            }, 3000);
        } else if (event === 'get_browser_info') {
            setTimeout(() => {
                this.trigger('browser_info', {
                    url: 'https://example.com',
                    title: 'Demo Browser Session',
                    timestamp: new Date().toISOString()
                });
            }, 500);
        } else if (event === 'get_browser_screenshot') {
            setTimeout(() => {
                // Generate a simple demo screenshot (base64 encoded 1x1 pixel image)
                const canvas = document.createElement('canvas');
                canvas.width = 400;
                canvas.height = 300;
                const ctx = canvas.getContext('2d');
                
                // Create a simple demo image
                ctx.fillStyle = '#f0f0f0';
                ctx.fillRect(0, 0, 400, 300);
                ctx.fillStyle = '#333';
                ctx.font = '20px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Demo Browser Screenshot', 200, 150);
                ctx.fillText('Real implementation would show', 200, 180);
                ctx.fillText('actual browser content here', 200, 210);
                
                const imageData = canvas.toDataURL('image/png');
                
                this.trigger('browser_screenshot', {
                    image_data: imageData,
                    timestamp: new Date().toISOString()
                });
            }, 1000);
        }
    }
    
    trigger(event, data) {
        console.log('Triggering event:', event, data);
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => callback(data));
        }
    }
    
    connect() {
        setTimeout(() => {
            this.connected = true;
            this.trigger('connect');
        }, 500);
    }
}

// Create global io function to match Socket.IO API
window.io = function() {
    const client = new SocketIOClient();
    client.connect();
    return client;
};