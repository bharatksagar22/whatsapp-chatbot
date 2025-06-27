import os
import sys
# DON'T CHANGE THIS PATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models.whatsapp import db
from routes.whatsapp import whatsapp_bp
from routes.automation import automation_bp
from services.automation_engine import automation_engine

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///whatsapp_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize extensions
db.init_app(app)
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(whatsapp_bp, url_prefix='/api')
app.register_blueprint(automation_bp, url_prefix='/api')

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Chatbot Backend</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #25D366; text-align: center; }
            .section { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 5px; }
            .endpoint { background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 3px; font-family: monospace; }
            .method { color: #007bff; font-weight: bold; }
            .status { padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
            .active { background: #28a745; }
            .inactive { background: #dc3545; }
            button { background: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #128C7E; }
            .response { background: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; margin: 10px 0; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 WhatsApp Chatbot Backend</h1>
            
            <div class="section">
                <h2>System Status</h2>
                <p>Automation Engine: <span class="status inactive" id="automation-status">Checking...</span></p>
                <button onclick="startAutomation()">Start Automation</button>
                <button onclick="stopAutomation()">Stop Automation</button>
                <button onclick="checkStatus()">Check Status</button>
            </div>
            
            <div class="section">
                <h2>API Endpoints</h2>
                
                <h3>WhatsApp Management</h3>
                <div class="endpoint"><span class="method">GET</span> /api/dashboard/stats - Get dashboard statistics</div>
                <div class="endpoint"><span class="method">GET</span> /api/numbers - Get WhatsApp numbers</div>
                <div class="endpoint"><span class="method">POST</span> /api/numbers - Add WhatsApp number</div>
                <div class="endpoint"><span class="method">GET</span> /api/doctors - Get doctors/leads</div>
                <div class="endpoint"><span class="method">POST</span> /api/doctors - Add doctor</div>
                <div class="endpoint"><span class="method">GET</span> /api/chat/{doctor_id}/messages - Get chat messages</div>
                <div class="endpoint"><span class="method">POST</span> /api/chat/{doctor_id}/send - Send message</div>
                
                <h3>Automation & AI</h3>
                <div class="endpoint"><span class="method">POST</span> /api/automation/start - Start automation engine</div>
                <div class="endpoint"><span class="method">POST</span> /api/automation/stop - Stop automation engine</div>
                <div class="endpoint"><span class="method">GET</span> /api/automation/status - Get automation status</div>
                <div class="endpoint"><span class="method">POST</span> /api/ai/smart-reply - Test smart reply</div>
                <div class="endpoint"><span class="method">POST</span> /api/ai/lead-score/{doctor_id} - Update lead score</div>
                <div class="endpoint"><span class="method">POST</span> /api/bulk/send-message - Send bulk messages</div>
                
                <h3>Analytics</h3>
                <div class="endpoint"><span class="method">GET</span> /api/analytics/automation - Get automation analytics</div>
                <div class="endpoint"><span class="method">GET</span> /api/analytics/ai-performance - Get AI performance</div>
            </div>
            
            <div class="section">
                <h2>Quick Actions</h2>
                <button onclick="initSampleData()">Initialize Sample Data</button>
                <button onclick="processAutoReplies()">Process Auto Replies</button>
                <button onclick="updateLeadScores()">Update Lead Scores</button>
                <button onclick="sendFollowUps()">Send Follow-ups</button>
                <div id="response" class="response" style="display: none;"></div>
            </div>
        </div>
        
        <script>
            function showResponse(data) {
                const responseDiv = document.getElementById('response');
                responseDiv.style.display = 'block';
                responseDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }
            
            function startAutomation() {
                fetch('/api/automation/start', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        showResponse(data);
                        checkStatus();
                    });
            }
            
            function stopAutomation() {
                fetch('/api/automation/stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        showResponse(data);
                        checkStatus();
                    });
            }
            
            function checkStatus() {
                fetch('/api/automation/status')
                    .then(response => response.json())
                    .then(data => {
                        const statusElement = document.getElementById('automation-status');
                        if (data.is_running) {
                            statusElement.textContent = 'Active';
                            statusElement.className = 'status active';
                        } else {
                            statusElement.textContent = 'Inactive';
                            statusElement.className = 'status inactive';
                        }
                        showResponse(data);
                    });
            }
            
            function initSampleData() {
                fetch('/api/init-sample-data', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => showResponse(data));
            }
            
            function processAutoReplies() {
                fetch('/api/manual/process-auto-replies', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => showResponse(data));
            }
            
            function updateLeadScores() {
                fetch('/api/manual/update-lead-scores', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => showResponse(data));
            }
            
            function sendFollowUps() {
                fetch('/api/manual/send-follow-ups', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => showResponse(data));
            }
            
            // Check status on page load
            checkStatus();
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    # Start automation engine
    automation_engine.start()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

