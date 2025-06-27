import threading
import time
import schedule
from datetime import datetime, timedelta
from models.whatsapp import db, Doctor, ChatMessage, WhatsAppNumber
from services.ai_agents import (
    smart_reply_agent, 
    lead_scoring_agent, 
    follow_up_engine, 
    pdf_catalogue_reader,
    offer_engine
)
from services.whatsapp_manager import whatsapp_manager

class AutomationEngine:
    """
    Main automation engine that coordinates all AI agents and automated tasks
    """
    
    def __init__(self):
        self.is_running = False
        self.auto_reply_enabled = True
        self.follow_up_enabled = True
        self.lead_scoring_enabled = True
        self.threads = []
    
    def start(self):
        """
        Start the automation engine
        """
        if self.is_running:
            return
        
        self.is_running = True
        
        # Schedule automated tasks
        schedule.every(5).minutes.do(self.process_auto_replies)
        schedule.every(1).hours.do(self.update_lead_scores)
        schedule.every(6).hours.do(self.send_follow_ups)
        schedule.every().day.at("09:00").do(self.daily_health_check)
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
        self.threads.append(scheduler_thread)
        
        print("Automation Engine started successfully")
    
    def stop(self):
        """
        Stop the automation engine
        """
        self.is_running = False
        schedule.clear()
        print("Automation Engine stopped")
    
    def _run_scheduler(self):
        """
        Run the scheduler in a separate thread
        """
        while self.is_running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    def process_auto_replies(self):
        """
        Process incoming messages and generate auto-replies
        """
        try:
            if not self.auto_reply_enabled:
                return
            
            # Get recent messages that need replies (last 5 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            
            recent_messages = ChatMessage.query.filter(
                ChatMessage.timestamp >= cutoff_time,
                ChatMessage.sender == 'doctor',
                ChatMessage.status == 'received'
            ).all()
            
            for message in recent_messages:
                # Check if we already replied to this message
                existing_reply = ChatMessage.query.filter(
                    ChatMessage.doctor_id == message.doctor_id,
                    ChatMessage.timestamp > message.timestamp,
                    ChatMessage.sender.in_(['ai', 'admin'])
                ).first()
                
                if existing_reply:
                    continue  # Already replied
                
                # Generate smart reply
                doctor = Doctor.query.get(message.doctor_id)
                reply_data = smart_reply_agent.generate_reply(message.message, doctor)
                
                if reply_data['confidence'] > 0.7:  # Only send high-confidence replies
                    # Send the reply
                    result = whatsapp_manager.send_message(doctor.phone, reply_data['reply'])
                    
                    if 'success' in result:
                        # Save the AI reply to database
                        ai_message = ChatMessage(
                            doctor_id=doctor.id,
                            whatsapp_number_id=message.whatsapp_number_id,
                            sender='ai',
                            message=reply_data['reply'],
                            status='sent'
                        )
                        db.session.add(ai_message)
                        db.session.commit()
                        
                        print(f"Auto-reply sent to {doctor.name}: {reply_data['reply'][:50]}...")
            
        except Exception as e:
            print(f"Error in process_auto_replies: {str(e)}")
    
    def update_lead_scores(self):
        """
        Update lead scores for all doctors
        """
        try:
            if not self.lead_scoring_enabled:
                return
            
            doctors = Doctor.query.all()
            
            for doctor in doctors:
                old_score = doctor.score
                new_score = lead_scoring_agent.calculate_lead_score(doctor.id)
                
                if new_score != old_score:
                    print(f"Updated lead score for {doctor.name}: {old_score} -> {new_score}")
            
        except Exception as e:
            print(f"Error in update_lead_scores: {str(e)}")
    
    def send_follow_ups(self):
        """
        Send automated follow-up messages
        """
        try:
            if not self.follow_up_enabled:
                return
            
            candidates = follow_up_engine.get_follow_up_candidates()
            
            for doctor in candidates:
                # Generate follow-up message
                follow_up_message = follow_up_engine.generate_follow_up_message(doctor)
                
                # Send the message
                result = whatsapp_manager.send_message(doctor.phone, follow_up_message)
                
                if 'success' in result:
                    # Save follow-up message to database
                    whatsapp_number = WhatsAppNumber.query.filter_by(status='active').first()
                    if whatsapp_number:
                        follow_up_msg = ChatMessage(
                            doctor_id=doctor.id,
                            whatsapp_number_id=whatsapp_number.id,
                            sender='ai',
                            message=follow_up_message,
                            status='sent'
                        )
                        db.session.add(follow_up_msg)
                        
                        # Update last interaction
                        doctor.last_interaction = datetime.utcnow()
                        db.session.commit()
                        
                        print(f"Follow-up sent to {doctor.name}")
                
                # Limit to 5 follow-ups per batch to avoid spam
                if len([d for d in candidates if d == doctor]) >= 5:
                    break
            
        except Exception as e:
            print(f"Error in send_follow_ups: {str(e)}")
    
    def daily_health_check(self):
        """
        Perform daily health check of the system
        """
        try:
            # Check WhatsApp connections
            connection_status = whatsapp_manager.get_connection_status()
            active_connections = sum(1 for conn in connection_status.values() if conn['status'] == 'active')
            
            # Check message volume
            today = datetime.utcnow().date()
            messages_today = ChatMessage.query.filter(
                ChatMessage.timestamp >= today
            ).count()
            
            # Check lead distribution
            hot_leads = Doctor.query.filter_by(tag='hot_lead').count()
            warm_leads = Doctor.query.filter_by(tag='warm_lead').count()
            
            health_report = f"""
Daily Health Check Report - {today}
=====================================
Active WhatsApp Connections: {active_connections}
Messages Today: {messages_today}
Hot Leads: {hot_leads}
Warm Leads: {warm_leads}
System Status: {'Healthy' if active_connections > 0 else 'Warning'}
            """.strip()
            
            print(health_report)
            
            # You could send this report via email or save to a file
            
        except Exception as e:
            print(f"Error in daily_health_check: {str(e)}")
    
    def handle_incoming_message(self, message_data):
        """
        Handle incoming message and trigger appropriate AI responses
        """
        try:
            doctor_id = message_data.get('doctor_id')
            message_text = message_data.get('message', '')
            
            if not doctor_id:
                return
            
            # Update lead score
            if self.lead_scoring_enabled:
                lead_scoring_agent.calculate_lead_score(doctor_id)
            
            # Check for product inquiries
            if any(keyword in message_text.lower() for keyword in ['catalogue', 'products', 'instruments', 'price']):
                # Search for relevant products
                products = pdf_catalogue_reader.search_products(message_text)
                
                if products:
                    product_info = f"Here are some products that might interest you:\n\n"
                    for product in products[:3]:  # Limit to 3 products
                        product_info += f"• {product['name']}: {product['description']} (Price: {product['price_range']})\n"
                    
                    product_info += "\nWould you like more details about any of these products?"
                    
                    # Send product information
                    doctor = Doctor.query.get(doctor_id)
                    if doctor:
                        whatsapp_manager.send_message(doctor.phone, product_info)
            
            # Check for high-intent keywords and send offers
            high_intent_keywords = ['buy', 'purchase', 'order', 'interested', 'price']
            if any(keyword in message_text.lower() for keyword in high_intent_keywords):
                doctor = Doctor.query.get(doctor_id)
                if doctor and doctor.tag in ['warm_lead', 'hot_lead']:
                    # Generate and send offer
                    offer_message = offer_engine.generate_offer(doctor)
                    
                    # Send after a delay to avoid immediate response
                    threading.Timer(60, lambda: whatsapp_manager.send_message(doctor.phone, offer_message)).start()
            
        except Exception as e:
            print(f"Error in handle_incoming_message: {str(e)}")
    
    def send_bulk_message(self, message_text, target_tags=None, limit=None):
        """
        Send bulk messages to doctors based on tags
        """
        try:
            query = Doctor.query
            
            if target_tags:
                query = query.filter(Doctor.tag.in_(target_tags))
            
            if limit:
                query = query.limit(limit)
            
            doctors = query.all()
            sent_count = 0
            
            for doctor in doctors:
                result = whatsapp_manager.send_message(doctor.phone, message_text)
                
                if 'success' in result:
                    sent_count += 1
                    
                    # Save bulk message to database
                    whatsapp_number = WhatsAppNumber.query.filter_by(status='active').first()
                    if whatsapp_number:
                        bulk_msg = ChatMessage(
                            doctor_id=doctor.id,
                            whatsapp_number_id=whatsapp_number.id,
                            sender='admin',
                            message=message_text,
                            status='sent'
                        )
                        db.session.add(bulk_msg)
                
                # Add delay between messages to avoid rate limiting
                time.sleep(2)
            
            db.session.commit()
            
            return {
                'success': True,
                'sent_count': sent_count,
                'total_targets': len(doctors)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_analytics(self):
        """
        Get automation analytics
        """
        try:
            # Message analytics
            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            
            messages_today = ChatMessage.query.filter(
                ChatMessage.timestamp >= today
            ).count()
            
            messages_yesterday = ChatMessage.query.filter(
                ChatMessage.timestamp >= yesterday,
                ChatMessage.timestamp < today
            ).count()
            
            # AI message analytics
            ai_messages_today = ChatMessage.query.filter(
                ChatMessage.timestamp >= today,
                ChatMessage.sender == 'ai'
            ).count()
            
            # Lead analytics
            lead_distribution = {
                'hot_lead': Doctor.query.filter_by(tag='hot_lead').count(),
                'warm_lead': Doctor.query.filter_by(tag='warm_lead').count(),
                'cold_lead': Doctor.query.filter_by(tag='cold_lead').count(),
                'registered': Doctor.query.filter_by(tag='registered').count()
            }
            
            return {
                'messages_today': messages_today,
                'messages_yesterday': messages_yesterday,
                'ai_messages_today': ai_messages_today,
                'automation_rate': round((ai_messages_today / max(messages_today, 1)) * 100, 2),
                'lead_distribution': lead_distribution,
                'system_status': 'active' if self.is_running else 'inactive'
            }
            
        except Exception as e:
            return {'error': str(e)}

# Global instance
automation_engine = AutomationEngine()

