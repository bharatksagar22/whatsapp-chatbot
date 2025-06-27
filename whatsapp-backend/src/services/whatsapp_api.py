import requests
import json
import os
from datetime import datetime
from models.whatsapp import db, WhatsAppNumber, ChatMessage, Doctor

class WhatsAppAPIService:
    """
    Service for integrating with WhatsApp Business API (Meta API)
    """
    
    def __init__(self):
        # These would normally come from environment variables or config
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', 'YOUR_PHONE_NUMBER_ID')
        self.verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'YOUR_VERIFY_TOKEN')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def send_message(self, to_number, message_text, whatsapp_number_id):
        """
        Send a text message via WhatsApp Business API
        """
        try:
            # Get WhatsApp number details
            whatsapp_number = WhatsAppNumber.query.get(whatsapp_number_id)
            if not whatsapp_number or whatsapp_number.connection_type != 'API':
                return {'error': 'Invalid WhatsApp API number'}
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'text',
                'text': {
                    'body': message_text
                }
            }
            
            response = requests.post(
                f'{self.base_url}/{self.phone_number_id}/messages',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                # Update number stats
                whatsapp_number.messages_count += 1
                whatsapp_number.last_active = datetime.utcnow()
                db.session.commit()
                
                return {
                    'success': True,
                    'message_id': response.json().get('messages', [{}])[0].get('id'),
                    'via': whatsapp_number.number
                }
            else:
                return {
                    'error': f'API Error: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def send_template_message(self, to_number, template_name, language_code='en_US'):
        """
        Send a template message (for initial contact)
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'template',
                'template': {
                    'name': template_name,
                    'language': {
                        'code': language_code
                    }
                }
            }
            
            response = requests.post(
                f'{self.base_url}/{self.phone_number_id}/messages',
                headers=headers,
                json=payload
            )
            
            return response.json()
            
        except Exception as e:
            return {'error': str(e)}
    
    def verify_webhook(self, mode, token, challenge):
        """
        Verify webhook for WhatsApp Business API
        """
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def process_webhook_message(self, webhook_data):
        """
        Process incoming webhook message from WhatsApp Business API
        """
        try:
            if 'entry' not in webhook_data:
                return {'error': 'Invalid webhook data'}
            
            for entry in webhook_data['entry']:
                if 'changes' not in entry:
                    continue
                    
                for change in entry['changes']:
                    if change.get('field') != 'messages':
                        continue
                    
                    value = change.get('value', {})
                    
                    # Process incoming messages
                    if 'messages' in value:
                        for message in value['messages']:
                            self._process_incoming_message(message, value)
                    
                    # Process message status updates
                    if 'statuses' in value:
                        for status in value['statuses']:
                            self._process_message_status(status)
            
            return {'success': True}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _process_incoming_message(self, message, value):
        """
        Process a single incoming message
        """
        try:
            # Extract message details
            from_number = message.get('from')
            message_id = message.get('id')
            timestamp = message.get('timestamp')
            message_type = message.get('type', 'text')
            
            # Extract message content based on type
            message_text = ''
            if message_type == 'text':
                message_text = message.get('text', {}).get('body', '')
            elif message_type == 'image':
                message_text = '[Image]'
            elif message_type == 'document':
                message_text = '[Document]'
            elif message_type == 'audio':
                message_text = '[Audio]'
            else:
                message_text = f'[{message_type.title()}]'
            
            # Find or create doctor
            doctor = Doctor.query.filter_by(phone=from_number).first()
            if not doctor:
                doctor = Doctor(
                    name=f"Dr. {from_number[-4:]}",  # Temporary name
                    phone=from_number,
                    tag='cold_lead'
                )
                db.session.add(doctor)
                db.session.flush()
            
            # Find active WhatsApp number (API type)
            whatsapp_number = WhatsAppNumber.query.filter_by(
                status='active', 
                connection_type='API'
            ).first()
            
            if not whatsapp_number:
                return {'error': 'No active API numbers available'}
            
            # Save incoming message
            chat_message = ChatMessage(
                doctor_id=doctor.id,
                whatsapp_number_id=whatsapp_number.id,
                sender='doctor',
                message=message_text,
                message_type=message_type,
                status='received',
                timestamp=datetime.fromtimestamp(int(timestamp))
            )
            db.session.add(chat_message)
            
            # Update doctor's last interaction
            doctor.last_interaction = datetime.utcnow()
            
            # Update number stats
            whatsapp_number.messages_count += 1
            whatsapp_number.last_active = datetime.utcnow()
            
            db.session.commit()
            
            # Here you would trigger AI response logic
            # For now, we'll just log the message
            print(f"Received message from {from_number}: {message_text}")
            
            return {'success': True, 'message_id': message_id}
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    def _process_message_status(self, status):
        """
        Process message status updates (sent, delivered, read)
        """
        try:
            message_id = status.get('id')
            status_type = status.get('status')  # sent, delivered, read
            timestamp = status.get('timestamp')
            
            # Update message status in database
            chat_message = ChatMessage.query.filter_by(id=message_id).first()
            if chat_message:
                chat_message.status = status_type
                db.session.commit()
            
            return {'success': True}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_media_url(self, media_id):
        """
        Get media URL from media ID
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(
                f'{self.base_url}/{media_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json().get('url')
            
            return None
            
        except Exception as e:
            return None
    
    def download_media(self, media_url):
        """
        Download media from WhatsApp servers
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(media_url, headers=headers)
            
            if response.status_code == 200:
                return response.content
            
            return None
            
        except Exception as e:
            return None

