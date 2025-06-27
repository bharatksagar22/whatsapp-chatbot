from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.whatsapp import db, WhatsAppNumber, Doctor, ChatMessage, AIAgent
from services.whatsapp_manager import whatsapp_manager
import json

whatsapp_bp = Blueprint('whatsapp', __name__)

# Dashboard Stats
@whatsapp_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        # Count active numbers
        active_numbers = WhatsAppNumber.query.filter_by(status='active').count()
        total_numbers = WhatsAppNumber.query.count()
        
        # Count doctors
        total_doctors = Doctor.query.count()
        
        # Count messages today
        today = datetime.utcnow().date()
        messages_today = ChatMessage.query.filter(
            ChatMessage.timestamp >= today
        ).count()
        
        # Calculate AI performance (mock calculation)
        ai_performance = "92%"
        
        return jsonify({
            'active_numbers': f'{active_numbers}/{total_numbers}',
            'total_doctors': total_doctors,
            'messages_today': messages_today,
            'ai_performance': ai_performance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WhatsApp Numbers Management
@whatsapp_bp.route('/numbers', methods=['GET'])
def get_whatsapp_numbers():
    try:
        numbers = WhatsAppNumber.query.all()
        return jsonify([{
            'id': num.id,
            'number': num.number,
            'connection_type': num.connection_type,
            'status': num.status,
            'messages_count': num.messages_count,
            'last_active': num.last_active.isoformat() if num.last_active else None
        } for num in numbers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/numbers', methods=['POST'])
def add_whatsapp_number():
    try:
        data = request.get_json()
        
        new_number = WhatsAppNumber(
            number=data['number'],
            connection_type=data['connection_type'],
            status='standby'
        )
        
        db.session.add(new_number)
        db.session.commit()
        
        # Initialize connection
        if data['connection_type'] == 'API':
            whatsapp_manager._initialize_api_connection(new_number)
        else:
            whatsapp_manager._initialize_web_connection(new_number)
        
        return jsonify({
            'success': True,
            'message': 'WhatsApp number added successfully',
            'id': new_number.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/numbers/<int:number_id>/restart', methods=['POST'])
def restart_whatsapp_number(number_id):
    try:
        result = whatsapp_manager.restart_connection(number_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/numbers/<int:number_id>/qr', methods=['GET'])
def get_qr_code(number_id):
    try:
        result = whatsapp_manager.get_qr_code(number_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Doctors/Leads Management
@whatsapp_bp.route('/doctors', methods=['GET'])
def get_doctors():
    try:
        doctors = Doctor.query.all()
        return jsonify([{
            'id': doc.id,
            'name': doc.name,
            'phone': doc.phone,
            'city': doc.city,
            'tag': doc.tag,
            'score': doc.score,
            'avatar': doc.name[:2].upper() if doc.name else 'DR',
            'last_interaction': doc.last_interaction.isoformat() if doc.last_interaction else None
        } for doc in doctors])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/doctors', methods=['POST'])
def add_doctor():
    try:
        data = request.get_json()
        
        new_doctor = Doctor(
            name=data['name'],
            phone=data['phone'],
            city=data.get('city', ''),
            tag=data.get('tag', 'cold_lead'),
            score=data.get('score', 0)
        )
        
        db.session.add(new_doctor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor added successfully',
            'id': new_doctor.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Chat Messages
@whatsapp_bp.route('/chat/<int:doctor_id>/messages', methods=['GET'])
def get_chat_messages(doctor_id):
    try:
        messages = ChatMessage.query.filter_by(doctor_id=doctor_id).order_by(ChatMessage.timestamp).all()
        
        return jsonify([{
            'id': msg.id,
            'sender': msg.sender,
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%H:%M') if msg.timestamp else '',
            'status': msg.status,
            'via': msg.whatsapp_number.number if msg.whatsapp_number else 'Unknown'
        } for msg in messages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/chat/<int:doctor_id>/send', methods=['POST'])
def send_message(doctor_id):
    try:
        data = request.get_json()
        message_text = data['message']
        
        # Get doctor details
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        # Send message using WhatsApp manager
        result = whatsapp_manager.send_message(doctor.phone, message_text)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'via': result.get('via', 'Unknown')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI Agents
@whatsapp_bp.route('/agents', methods=['GET'])
def get_ai_agents():
    try:
        agents = AIAgent.query.all()
        return jsonify([{
            'id': agent.id,
            'name': agent.name,
            'status': agent.status,
            'performance': agent.performance,
            'last_crash': agent.last_crash.isoformat() if agent.last_crash else 'Never'
        } for agent in agents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/agents/<int:agent_id>/restart', methods=['POST'])
def restart_agent(agent_id):
    try:
        agent = AIAgent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404
        
        # Simulate agent restart
        agent.status = 'active'
        agent.last_crash = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Agent {agent.name} restarted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics
@whatsapp_bp.route('/analytics/messages', methods=['GET'])
def get_message_analytics():
    try:
        # Get message counts by day for the last 7 days
        analytics = []
        for i in range(7):
            date = datetime.utcnow().date() - timedelta(days=i)
            count = ChatMessage.query.filter(
                ChatMessage.timestamp >= date,
                ChatMessage.timestamp < date + timedelta(days=1)
            ).count()
            analytics.append({
                'date': date.isoformat(),
                'count': count
            })
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/analytics/leads', methods=['GET'])
def get_lead_analytics():
    try:
        # Get lead distribution by tag
        tags = ['hot_lead', 'warm_lead', 'cold_lead', 'registered']
        analytics = []
        
        for tag in tags:
            count = Doctor.query.filter_by(tag=tag).count()
            analytics.append({
                'tag': tag,
                'count': count
            })
        
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WhatsApp Business API Webhook
@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        result = whatsapp_manager.api_service.verify_webhook(mode, token, challenge)
        if result:
            return result, 200
        else:
            return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Process incoming webhook
        webhook_data = request.get_json()
        result = whatsapp_manager.api_service.process_webhook_message(webhook_data)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({'status': 'success'}), 200

# Initialize sample data
@whatsapp_bp.route('/init-sample-data', methods=['POST'])
def init_sample_data():
    try:
        # Clear existing data
        ChatMessage.query.delete()
        Doctor.query.delete()
        WhatsAppNumber.query.delete()
        AIAgent.query.delete()
        
        # Add sample WhatsApp numbers
        numbers = [
            WhatsAppNumber(number='+1234567890', connection_type='API', status='active', messages_count=45),
            WhatsAppNumber(number='+1234567891', connection_type='Web', status='active', messages_count=32),
            WhatsAppNumber(number='+1234567892', connection_type='API', status='standby', messages_count=0),
            WhatsAppNumber(number='+1234567893', connection_type='Web', status='blocked', messages_count=12),
            WhatsAppNumber(number='+1234567894', connection_type='API', status='standby', messages_count=0)
        ]
        
        for number in numbers:
            db.session.add(number)
        
        # Add sample doctors
        doctors = [
            Doctor(name='Dr. Sneha Kulkarni', phone='+919876543210', city='Bangalore', tag='cold_lead', score=3),
            Doctor(name='Dr. Amit Joshi', phone='+919876543211', city='Delhi', tag='registered', score=9),
            Doctor(name='Dr. Priya Patel', phone='+919876543212', city='Pune', tag='warm_lead', score=6),
            Doctor(name='Dr. Rajesh Sharma', phone='+919876543213', city='Mumbai', tag='hot_lead', score=8)
        ]
        
        for doctor in doctors:
            db.session.add(doctor)
        
        db.session.flush()  # Get IDs
        
        # Add sample AI agents
        agents = [
            AIAgent(name='Smart Reply Agent', status='active', performance=95),
            AIAgent(name='PDF Catalogue Reader', status='active', performance=88),
            AIAgent(name='Lead Scoring Agent', status='active', performance=92),
            AIAgent(name='Follow-Up Engine', status='standby', performance=0)
        ]
        
        for agent in agents:
            db.session.add(agent)
        
        # Add sample chat messages
        messages = [
            ChatMessage(doctor_id=1, whatsapp_number_id=1, sender='doctor', message='Hello, I am interested in your surgical instruments', status='received'),
            ChatMessage(doctor_id=1, whatsapp_number_id=1, sender='ai', message='Thank you for your interest! I can help you with our latest catalogue. Would you like me to send you our PDF brochure?', status='sent'),
            ChatMessage(doctor_id=2, whatsapp_number_id=2, sender='doctor', message='Can you tell me about the pricing?', status='received'),
            ChatMessage(doctor_id=2, whatsapp_number_id=2, sender='admin', message='I will connect you with our sales team for detailed pricing information.', status='sent'),
        ]
        
        for message in messages:
            db.session.add(message)
        
        db.session.commit()
        
        return jsonify({'message': 'Sample data initialized successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

