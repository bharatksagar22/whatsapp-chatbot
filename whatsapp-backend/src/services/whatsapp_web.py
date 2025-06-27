import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from models.whatsapp import db, WhatsAppNumber, ChatMessage, Doctor

class WhatsAppWebService:
    """
    Service for automating WhatsApp Web using Selenium
    """
    
    def __init__(self, whatsapp_number_id, headless=True):
        self.whatsapp_number_id = whatsapp_number_id
        self.driver = None
        self.headless = headless
        self.is_logged_in = False
        self.session_path = f"/tmp/whatsapp_session_{whatsapp_number_id}"
        
    def initialize_driver(self):
        """
        Initialize Chrome WebDriver with WhatsApp Web
        """
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-data-dir={self.session_path}")
            
            # Disable notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get("https://web.whatsapp.com")
            
            return True
            
        except Exception as e:
            print(f"Error initializing driver: {str(e)}")
            return False
    
    def wait_for_login(self, timeout=60):
        """
        Wait for user to scan QR code and login
        """
        try:
            # Wait for either QR code or chat list to appear
            WebDriverWait(self.driver, timeout).until(
                lambda driver: self._is_logged_in() or self._qr_code_present()
            )
            
            if self._is_logged_in():
                self.is_logged_in = True
                return True
            
            return False
            
        except TimeoutException:
            return False
    
    def _is_logged_in(self):
        """
        Check if user is logged in by looking for chat list
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, '[data-testid="chat-list"]')
            return True
        except NoSuchElementException:
            return False
    
    def _qr_code_present(self):
        """
        Check if QR code is present
        """
        try:
            self.driver.find_element(By.CSS_SELECTOR, '[data-testid="qr-code"]')
            return True
        except NoSuchElementException:
            return False
    
    def get_qr_code(self):
        """
        Get QR code for login (if present)
        """
        try:
            if self._qr_code_present():
                qr_element = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="qr-code"] img')
                return qr_element.get_attribute('src')
            return None
        except Exception as e:
            return None
    
    def send_message(self, phone_number, message_text):
        """
        Send a message to a specific phone number
        """
        try:
            if not self.is_logged_in:
                return {'error': 'Not logged in to WhatsApp Web'}
            
            # Format phone number (remove + and spaces)
            clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            
            # Navigate to chat using phone number
            chat_url = f"https://web.whatsapp.com/send?phone={clean_phone}"
            self.driver.get(chat_url)
            
            # Wait for chat to load
            time.sleep(3)
            
            # Check if chat loaded successfully
            try:
                # Look for the message input box
                message_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="conversation-compose-box-input"]'))
                )
                
                # Type the message
                message_box.click()
                message_box.send_keys(message_text)
                
                # Send the message
                send_button = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="send"]')
                send_button.click()
                
                # Wait a moment for message to be sent
                time.sleep(2)
                
                # Update database
                self._save_sent_message(phone_number, message_text)
                
                return {
                    'success': True,
                    'message': 'Message sent successfully',
                    'via': self._get_whatsapp_number().number
                }
                
            except TimeoutException:
                return {'error': 'Could not find message input box'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _save_sent_message(self, phone_number, message_text):
        """
        Save sent message to database
        """
        try:
            # Find or create doctor
            doctor = Doctor.query.filter_by(phone=phone_number).first()
            if not doctor:
                doctor = Doctor(
                    name=f"Dr. {phone_number[-4:]}",
                    phone=phone_number,
                    tag='cold_lead'
                )
                db.session.add(doctor)
                db.session.flush()
            
            # Get WhatsApp number
            whatsapp_number = self._get_whatsapp_number()
            
            # Save message
            chat_message = ChatMessage(
                doctor_id=doctor.id,
                whatsapp_number_id=whatsapp_number.id,
                sender='admin',
                message=message_text,
                status='sent'
            )
            db.session.add(chat_message)
            
            # Update stats
            doctor.last_interaction = datetime.utcnow()
            whatsapp_number.messages_count += 1
            whatsapp_number.last_active = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving message: {str(e)}")
    
    def _get_whatsapp_number(self):
        """
        Get WhatsApp number object from database
        """
        return WhatsAppNumber.query.get(self.whatsapp_number_id)
    
    def get_unread_messages(self):
        """
        Get unread messages from WhatsApp Web
        """
        try:
            if not self.is_logged_in:
                return []
            
            # Navigate to main chat list
            self.driver.get("https://web.whatsapp.com")
            time.sleep(3)
            
            unread_messages = []
            
            # Find chats with unread messages
            unread_chats = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="cell-frame-container"] [data-testid="unread-count"]')
            
            for chat_element in unread_chats:
                try:
                    # Click on the chat
                    chat_container = chat_element.find_element(By.XPATH, './ancestor::div[@data-testid="cell-frame-container"]')
                    chat_container.click()
                    time.sleep(2)
                    
                    # Get messages
                    messages = self._extract_messages_from_chat()
                    unread_messages.extend(messages)
                    
                except Exception as e:
                    continue
            
            return unread_messages
            
        except Exception as e:
            return []
    
    def _extract_messages_from_chat(self):
        """
        Extract messages from current chat
        """
        try:
            messages = []
            
            # Get chat title (contact name or number)
            chat_title = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="conversation-header"] span[title]').get_attribute('title')
            
            # Get message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="msg-container"]')
            
            for msg_element in message_elements[-10:]:  # Get last 10 messages
                try:
                    # Check if message is incoming (from contact)
                    is_incoming = 'message-in' in msg_element.get_attribute('class')
                    
                    if is_incoming:
                        # Extract message text
                        text_element = msg_element.find_element(By.CSS_SELECTOR, '[data-testid="conversation-text"]')
                        message_text = text_element.text
                        
                        # Extract timestamp
                        time_element = msg_element.find_element(By.CSS_SELECTOR, '[data-testid="msg-meta"] span')
                        timestamp = time_element.text
                        
                        messages.append({
                            'from': chat_title,
                            'message': message_text,
                            'timestamp': timestamp,
                            'type': 'incoming'
                        })
                        
                except Exception as e:
                    continue
            
            return messages
            
        except Exception as e:
            return []
    
    def monitor_messages(self, callback=None):
        """
        Monitor for new incoming messages
        """
        try:
            if not self.is_logged_in:
                return False
            
            last_message_count = 0
            
            while True:
                try:
                    # Check for new messages
                    unread_messages = self.get_unread_messages()
                    
                    if len(unread_messages) > last_message_count:
                        new_messages = unread_messages[last_message_count:]
                        
                        for message in new_messages:
                            # Save to database
                            self._save_incoming_message(message)
                            
                            # Call callback if provided
                            if callback:
                                callback(message)
                        
                        last_message_count = len(unread_messages)
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    print(f"Error monitoring messages: {str(e)}")
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("Stopping message monitoring")
            return True
    
    def _save_incoming_message(self, message_data):
        """
        Save incoming message to database
        """
        try:
            phone_number = message_data.get('from', '')
            message_text = message_data.get('message', '')
            
            # Find or create doctor
            doctor = Doctor.query.filter_by(phone=phone_number).first()
            if not doctor:
                doctor = Doctor(
                    name=f"Dr. {phone_number[-4:]}",
                    phone=phone_number,
                    tag='cold_lead'
                )
                db.session.add(doctor)
                db.session.flush()
            
            # Get WhatsApp number
            whatsapp_number = self._get_whatsapp_number()
            
            # Save message
            chat_message = ChatMessage(
                doctor_id=doctor.id,
                whatsapp_number_id=whatsapp_number.id,
                sender='doctor',
                message=message_text,
                status='received'
            )
            db.session.add(chat_message)
            
            # Update stats
            doctor.last_interaction = datetime.utcnow()
            whatsapp_number.messages_count += 1
            whatsapp_number.last_active = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving incoming message: {str(e)}")
    
    def close(self):
        """
        Close the WebDriver
        """
        if self.driver:
            self.driver.quit()
    
    def __del__(self):
        """
        Cleanup when object is destroyed
        """
        self.close()

