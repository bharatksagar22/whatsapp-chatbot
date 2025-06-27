import threading
import time
from datetime import datetime
from models.whatsapp import db, WhatsAppNumber
from services.whatsapp_api import WhatsAppAPIService
from services.whatsapp_web import WhatsAppWebService

class WhatsAppManager:
    """
    Manager class to handle multiple WhatsApp connections (API and Web)
    """
    
    def __init__(self):
        self.api_service = WhatsAppAPIService()
        self.web_services = {}  # Dictionary to store web service instances
        self.active_connections = {}
        self.monitoring_threads = {}
        
    def initialize_connections(self):
        """
        Initialize all WhatsApp connections from database
        """
        try:
            whatsapp_numbers = WhatsAppNumber.query.all()
            
            for number in whatsapp_numbers:
                if number.connection_type == 'API':
                    self._initialize_api_connection(number)
                elif number.connection_type == 'Web':
                    self._initialize_web_connection(number)
            
            return True
            
        except Exception as e:
            print(f"Error initializing connections: {str(e)}")
            return False
    
    def _initialize_api_connection(self, whatsapp_number):
        """
        Initialize API connection (no special setup needed)
        """
        try:
            # API connections don't need initialization
            # Just mark as active if configured properly
            if self.api_service.access_token != 'YOUR_ACCESS_TOKEN':
                whatsapp_number.status = 'active'
            else:
                whatsapp_number.status = 'standby'
            
            db.session.commit()
            
            self.active_connections[whatsapp_number.id] = {
                'type': 'API',
                'service': self.api_service,
                'status': whatsapp_number.status
            }
            
            return True
            
        except Exception as e:
            print(f"Error initializing API connection: {str(e)}")
            return False
    
    def _initialize_web_connection(self, whatsapp_number):
        """
        Initialize Web WhatsApp connection
        """
        try:
            web_service = WhatsAppWebService(whatsapp_number.id, headless=True)
            
            if web_service.initialize_driver():
                self.web_services[whatsapp_number.id] = web_service
                
                # Check if already logged in
                if web_service.wait_for_login(timeout=10):
                    whatsapp_number.status = 'active'
                    web_service.is_logged_in = True
                    
                    # Start monitoring thread
                    self._start_monitoring_thread(whatsapp_number.id, web_service)
                else:
                    whatsapp_number.status = 'standby'
                
                self.active_connections[whatsapp_number.id] = {
                    'type': 'Web',
                    'service': web_service,
                    'status': whatsapp_number.status
                }
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error initializing Web connection: {str(e)}")
            return False
    
    def _start_monitoring_thread(self, number_id, web_service):
        """
        Start monitoring thread for Web WhatsApp
        """
        def monitor():
            web_service.monitor_messages(callback=self._handle_incoming_message)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.monitoring_threads[number_id] = thread
    
    def _handle_incoming_message(self, message_data):
        """
        Handle incoming messages from Web WhatsApp
        """
        print(f"Received message: {message_data}")
        # Additional processing can be added here
        # e.g., trigger AI response, update lead scoring, etc.
    
    def send_message(self, to_number, message_text, preferred_type=None):
        """
        Send message using the best available connection
        """
        try:
            # Get active connections
            active_numbers = [
                conn for conn in self.active_connections.values() 
                if conn['status'] == 'active'
            ]
            
            if not active_numbers:
                return {'error': 'No active WhatsApp connections available'}
            
            # Prefer API over Web if no preference specified
            if preferred_type:
                preferred_connections = [
                    conn for conn in active_numbers 
                    if conn['type'] == preferred_type
                ]
                if preferred_connections:
                    active_numbers = preferred_connections
            else:
                # Prefer API connections
                api_connections = [
                    conn for conn in active_numbers 
                    if conn['type'] == 'API'
                ]
                if api_connections:
                    active_numbers = api_connections
            
            # Use the first available connection
            connection = active_numbers[0]
            
            if connection['type'] == 'API':
                # Find the WhatsApp number ID for this connection
                number_id = None
                for num_id, conn in self.active_connections.items():
                    if conn == connection:
                        number_id = num_id
                        break
                
                return self.api_service.send_message(to_number, message_text, number_id)
            
            elif connection['type'] == 'Web':
                return connection['service'].send_message(to_number, message_text)
            
            return {'error': 'Unknown connection type'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_connection_status(self):
        """
        Get status of all connections
        """
        try:
            status = {}
            
            for number_id, connection in self.active_connections.items():
                whatsapp_number = WhatsAppNumber.query.get(number_id)
                
                status[number_id] = {
                    'number': whatsapp_number.number,
                    'type': connection['type'],
                    'status': connection['status'],
                    'messages_count': whatsapp_number.messages_count,
                    'last_active': whatsapp_number.last_active.isoformat() if whatsapp_number.last_active else None
                }
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def restart_connection(self, number_id):
        """
        Restart a specific connection
        """
        try:
            whatsapp_number = WhatsAppNumber.query.get(number_id)
            if not whatsapp_number:
                return {'error': 'WhatsApp number not found'}
            
            # Close existing connection if it exists
            if number_id in self.active_connections:
                connection = self.active_connections[number_id]
                if connection['type'] == 'Web' and number_id in self.web_services:
                    self.web_services[number_id].close()
                    del self.web_services[number_id]
                
                del self.active_connections[number_id]
            
            # Stop monitoring thread if it exists
            if number_id in self.monitoring_threads:
                # Note: We can't easily stop the thread, but it will stop when the service is closed
                del self.monitoring_threads[number_id]
            
            # Reinitialize connection
            if whatsapp_number.connection_type == 'API':
                success = self._initialize_api_connection(whatsapp_number)
            else:
                success = self._initialize_web_connection(whatsapp_number)
            
            if success:
                return {'success': True, 'message': 'Connection restarted successfully'}
            else:
                return {'error': 'Failed to restart connection'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def switch_to_backup_number(self, failed_number_id):
        """
        Switch to backup number when primary fails
        """
        try:
            # Mark failed number as blocked
            failed_number = WhatsAppNumber.query.get(failed_number_id)
            if failed_number:
                failed_number.status = 'blocked'
                db.session.commit()
            
            # Update connection status
            if failed_number_id in self.active_connections:
                self.active_connections[failed_number_id]['status'] = 'blocked'
            
            # Find next available number
            available_numbers = WhatsAppNumber.query.filter_by(status='standby').first()
            
            if available_numbers:
                # Activate backup number
                if available_numbers.connection_type == 'API':
                    self._initialize_api_connection(available_numbers)
                else:
                    self._initialize_web_connection(available_numbers)
                
                return {
                    'success': True, 
                    'message': f'Switched to backup number: {available_numbers.number}'
                }
            
            return {'error': 'No backup numbers available'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_qr_code(self, number_id):
        """
        Get QR code for Web WhatsApp login
        """
        try:
            if number_id not in self.web_services:
                return {'error': 'Web service not found for this number'}
            
            web_service = self.web_services[number_id]
            qr_code = web_service.get_qr_code()
            
            if qr_code:
                return {'success': True, 'qr_code': qr_code}
            else:
                return {'error': 'QR code not available or already logged in'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup(self):
        """
        Cleanup all connections
        """
        try:
            # Close all web services
            for web_service in self.web_services.values():
                web_service.close()
            
            self.web_services.clear()
            self.active_connections.clear()
            self.monitoring_threads.clear()
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

# Global instance
whatsapp_manager = WhatsAppManager()

