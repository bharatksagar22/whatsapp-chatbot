from flask import Blueprint, request, jsonify
from services.automation_engine import automation_engine
from services.ai_agents import (
    smart_reply_agent,
    lead_scoring_agent,
    follow_up_engine,
    pdf_catalogue_reader,
    offer_engine
)
from models.whatsapp import Doctor

automation_bp = Blueprint('automation', __name__)

# Automation Engine Control
@automation_bp.route('/automation/start', methods=['POST'])
def start_automation():
    try:
        automation_engine.start()
        return jsonify({
            'success': True,
            'message': 'Automation engine started successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/automation/stop', methods=['POST'])
def stop_automation():
    try:
        automation_engine.stop()
        return jsonify({
            'success': True,
            'message': 'Automation engine stopped successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/automation/status', methods=['GET'])
def get_automation_status():
    try:
        analytics = automation_engine.get_analytics()
        return jsonify({
            'is_running': automation_engine.is_running,
            'auto_reply_enabled': automation_engine.auto_reply_enabled,
            'follow_up_enabled': automation_engine.follow_up_enabled,
            'lead_scoring_enabled': automation_engine.lead_scoring_enabled,
            'analytics': analytics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/automation/settings', methods=['POST'])
def update_automation_settings():
    try:
        data = request.get_json()
        
        if 'auto_reply_enabled' in data:
            automation_engine.auto_reply_enabled = data['auto_reply_enabled']
        
        if 'follow_up_enabled' in data:
            automation_engine.follow_up_enabled = data['follow_up_enabled']
        
        if 'lead_scoring_enabled' in data:
            automation_engine.lead_scoring_enabled = data['lead_scoring_enabled']
        
        return jsonify({
            'success': True,
            'message': 'Automation settings updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI Agents
@automation_bp.route('/ai/smart-reply', methods=['POST'])
def test_smart_reply():
    try:
        data = request.get_json()
        message_text = data.get('message', '')
        doctor_id = data.get('doctor_id')
        
        doctor_context = None
        if doctor_id:
            doctor_context = Doctor.query.get(doctor_id)
        
        reply = smart_reply_agent.generate_reply(message_text, doctor_context)
        return jsonify(reply)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/ai/lead-score/<int:doctor_id>', methods=['POST'])
def update_lead_score(doctor_id):
    try:
        score = lead_scoring_agent.calculate_lead_score(doctor_id)
        return jsonify({
            'success': True,
            'doctor_id': doctor_id,
            'new_score': score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/ai/follow-up-candidates', methods=['GET'])
def get_follow_up_candidates():
    try:
        candidates = follow_up_engine.get_follow_up_candidates()
        return jsonify([{
            'id': doctor.id,
            'name': doctor.name,
            'phone': doctor.phone,
            'tag': doctor.tag,
            'last_interaction': doctor.last_interaction.isoformat() if doctor.last_interaction else None
        } for doctor in candidates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/ai/follow-up/<int:doctor_id>', methods=['POST'])
def send_follow_up(doctor_id):
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        message = follow_up_engine.generate_follow_up_message(doctor)
        return jsonify({
            'success': True,
            'doctor_id': doctor_id,
            'follow_up_message': message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/ai/search-products', methods=['POST'])
def search_products():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        products = pdf_catalogue_reader.search_products(query)
        return jsonify({
            'success': True,
            'query': query,
            'products': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/ai/generate-offer/<int:doctor_id>', methods=['POST'])
def generate_offer(doctor_id):
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        offer_message = offer_engine.generate_offer(doctor)
        return jsonify({
            'success': True,
            'doctor_id': doctor_id,
            'offer_message': offer_message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bulk Operations
@automation_bp.route('/bulk/send-message', methods=['POST'])
def send_bulk_message():
    try:
        data = request.get_json()
        message_text = data.get('message', '')
        target_tags = data.get('target_tags', [])
        limit = data.get('limit')
        
        if not message_text:
            return jsonify({'error': 'Message text is required'}), 400
        
        result = automation_engine.send_bulk_message(message_text, target_tags, limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/bulk/send-offers', methods=['POST'])
def send_bulk_offers():
    try:
        data = request.get_json()
        target_tags = data.get('target_tags', ['warm_lead', 'hot_lead'])
        limit = data.get('limit', 50)
        
        # Get target doctors
        query = Doctor.query.filter(Doctor.tag.in_(target_tags))
        if limit:
            query = query.limit(limit)
        
        doctors = query.all()
        sent_count = 0
        
        for doctor in doctors:
            offer_message = offer_engine.generate_offer(doctor)
            result = automation_engine.send_bulk_message(offer_message, None, 1)
            
            if result.get('success'):
                sent_count += result.get('sent_count', 0)
        
        return jsonify({
            'success': True,
            'sent_count': sent_count,
            'total_targets': len(doctors)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics
@automation_bp.route('/analytics/automation', methods=['GET'])
def get_automation_analytics():
    try:
        analytics = automation_engine.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/analytics/ai-performance', methods=['GET'])
def get_ai_performance():
    try:
        # Mock AI performance data
        performance_data = {
            'smart_reply_agent': {
                'name': 'Smart Reply Agent',
                'status': 'active',
                'accuracy': 92,
                'responses_today': 45,
                'avg_response_time': 1.2
            },
            'lead_scoring_agent': {
                'name': 'Lead Scoring Agent',
                'status': 'active',
                'accuracy': 88,
                'scores_updated_today': 23,
                'avg_processing_time': 0.8
            },
            'follow_up_engine': {
                'name': 'Follow-Up Engine',
                'status': 'active',
                'success_rate': 76,
                'follow_ups_sent_today': 12,
                'response_rate': 34
            },
            'pdf_catalogue_reader': {
                'name': 'PDF Catalogue Reader',
                'status': 'active',
                'accuracy': 95,
                'queries_processed_today': 18,
                'avg_search_time': 0.5
            }
        }
        
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Manual Triggers
@automation_bp.route('/manual/process-auto-replies', methods=['POST'])
def manual_process_auto_replies():
    try:
        automation_engine.process_auto_replies()
        return jsonify({
            'success': True,
            'message': 'Auto-replies processed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/manual/update-lead-scores', methods=['POST'])
def manual_update_lead_scores():
    try:
        automation_engine.update_lead_scores()
        return jsonify({
            'success': True,
            'message': 'Lead scores updated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/manual/send-follow-ups', methods=['POST'])
def manual_send_follow_ups():
    try:
        automation_engine.send_follow_ups()
        return jsonify({
            'success': True,
            'message': 'Follow-ups sent successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@automation_bp.route('/manual/health-check', methods=['POST'])
def manual_health_check():
    try:
        automation_engine.daily_health_check()
        return jsonify({
            'success': True,
            'message': 'Health check completed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

