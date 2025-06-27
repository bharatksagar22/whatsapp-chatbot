import re
import json
import random
from datetime import datetime, timedelta
from models.whatsapp import db, Doctor, ChatMessage, AIAgent

class SmartReplyAgent:
    """
    AI Agent for generating smart replies based on message content
    """
    
    def __init__(self):
        self.name = "Smart Reply Agent"
        self.patterns = {
            'greeting': [
                r'\b(hello|hi|hey|namaste|good morning|good afternoon|good evening)\b',
                ['Hello! Thank you for contacting SurgiAI. How can I help you today?',
                 'Hi there! Welcome to SurgiAI. What can I assist you with?',
                 'Namaste! Thank you for reaching out. How may I help you?']
            ],
            'pricing': [
                r'\b(price|cost|rate|pricing|expensive|cheap|budget)\b',
                ['I understand you\'re interested in our pricing. Let me connect you with our sales team for detailed pricing information.',
                 'For pricing details, I\'ll have our sales representative contact you shortly. Can you share your requirements?',
                 'Our pricing varies based on your specific needs. Would you like me to schedule a call with our sales team?']
            ],
            'catalogue': [
                r'\b(catalogue|catalog|brochure|products|instruments|equipment)\b',
                ['I can send you our latest surgical instruments catalogue. Would you like the PDF version?',
                 'Our comprehensive product catalogue is available. Shall I share it with you?',
                 'We have an extensive range of surgical instruments. Let me send you our catalogue.']
            ],
            'interest': [
                r'\b(interested|want|need|require|looking for)\b',
                ['That\'s great! I\'d love to help you find the right surgical instruments for your practice.',
                 'Wonderful! Can you tell me more about your specific requirements?',
                 'Perfect! Let me know what type of surgical instruments you\'re looking for.']
            ],
            'quality': [
                r'\b(quality|standard|certification|ISO|FDA)\b',
                ['All our surgical instruments meet international quality standards including ISO and FDA certifications.',
                 'Quality is our top priority. Our instruments are manufactured with the highest standards.',
                 'We maintain strict quality control and all products are certified to international standards.']
            ]
        }
    
    def generate_reply(self, message_text, doctor_context=None):
        """
        Generate smart reply based on message content and doctor context
        """
        try:
            message_lower = message_text.lower()
            
            # Check for patterns and generate appropriate response
            for category, (pattern, responses) in self.patterns.items():
                if re.search(pattern, message_lower, re.IGNORECASE):
                    response = random.choice(responses)
                    
                    # Personalize based on doctor context
                    if doctor_context and doctor_context.name:
                        response = f"Dr. {doctor_context.name.split()[-1]}, {response.lower()}"
                    
                    return {
                        'reply': response,
                        'category': category,
                        'confidence': 0.85
                    }
            
            # Default response for unmatched messages
            default_responses = [
                'Thank you for your message. Our team will get back to you shortly.',
                'I appreciate your inquiry. Let me connect you with the right person to assist you.',
                'Thanks for reaching out! How can we help you with your surgical instrument needs?'
            ]
            
            return {
                'reply': random.choice(default_responses),
                'category': 'general',
                'confidence': 0.6
            }
            
        except Exception as e:
            return {
                'reply': 'Thank you for your message. Our team will respond soon.',
                'category': 'error',
                'confidence': 0.3
            }

class LeadScoringAgent:
    """
    AI Agent for scoring and tagging leads based on their interactions
    """
    
    def __init__(self):
        self.name = "Lead Scoring Agent"
        self.scoring_rules = {
            'keywords': {
                'high_intent': ['buy', 'purchase', 'order', 'urgent', 'immediately', 'asap'],
                'medium_intent': ['interested', 'want', 'need', 'looking for', 'require'],
                'low_intent': ['maybe', 'thinking', 'considering', 'future']
            },
            'engagement': {
                'high': 5,  # 5+ messages
                'medium': 3,  # 3-4 messages
                'low': 1  # 1-2 messages
            }
        }
    
    def calculate_lead_score(self, doctor_id):
        """
        Calculate lead score based on message history and engagement
        """
        try:
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return 0
            
            messages = ChatMessage.query.filter_by(doctor_id=doctor_id).all()
            
            score = 0
            
            # Base score
            score += 1
            
            # Message count scoring
            message_count = len(messages)
            if message_count >= 5:
                score += 3
            elif message_count >= 3:
                score += 2
            elif message_count >= 1:
                score += 1
            
            # Keyword analysis
            all_text = ' '.join([msg.message.lower() for msg in messages if msg.sender == 'doctor'])
            
            for keyword in self.scoring_rules['keywords']['high_intent']:
                if keyword in all_text:
                    score += 3
            
            for keyword in self.scoring_rules['keywords']['medium_intent']:
                if keyword in all_text:
                    score += 2
            
            for keyword in self.scoring_rules['keywords']['low_intent']:
                if keyword in all_text:
                    score += 1
            
            # Recency scoring
            if messages:
                last_message = max(messages, key=lambda x: x.timestamp)
                days_since_last = (datetime.utcnow() - last_message.timestamp).days
                
                if days_since_last <= 1:
                    score += 2
                elif days_since_last <= 7:
                    score += 1
            
            # Cap the score at 10
            score = min(score, 10)
            
            # Update doctor score
            doctor.score = score
            
            # Update tag based on score
            if score >= 8:
                doctor.tag = 'hot_lead'
            elif score >= 5:
                doctor.tag = 'warm_lead'
            elif score >= 3:
                doctor.tag = 'cold_lead'
            else:
                doctor.tag = 'cold_lead'
            
            db.session.commit()
            
            return score
            
        except Exception as e:
            return 0
    
    def tag_lead(self, doctor_id, custom_tag=None):
        """
        Tag a lead with custom or calculated tag
        """
        try:
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return False
            
            if custom_tag:
                doctor.tag = custom_tag
            else:
                # Calculate and assign tag based on score
                score = self.calculate_lead_score(doctor_id)
                # Tag is already updated in calculate_lead_score
            
            db.session.commit()
            return True
            
        except Exception as e:
            return False

class FollowUpEngine:
    """
    AI Agent for automated follow-up messages
    """
    
    def __init__(self):
        self.name = "Follow-Up Engine"
        self.follow_up_templates = {
            'initial': [
                "Hi Dr. {name}, I hope you had a chance to review our surgical instruments catalogue. Do you have any questions?",
                "Hello Dr. {name}, following up on our conversation about surgical instruments. How can we assist you further?",
                "Hi Dr. {name}, just checking if you need any additional information about our products."
            ],
            'interested': [
                "Dr. {name}, I noticed you were interested in our surgical instruments. Would you like to schedule a demo?",
                "Hello Dr. {name}, our team is ready to provide you with a detailed quote. When would be a good time to connect?",
                "Hi Dr. {name}, we have some special offers on surgical instruments this month. Would you like to know more?"
            ],
            'inactive': [
                "Dr. {name}, we haven't heard from you in a while. Is there anything we can help you with?",
                "Hello Dr. {name}, we have some new surgical instruments that might interest you. Would you like to see them?",
                "Hi Dr. {name}, hope you're doing well. Any updates on your surgical instrument requirements?"
            ]
        }
    
    def get_follow_up_candidates(self):
        """
        Get doctors who need follow-up messages
        """
        try:
            # Get doctors who haven't been contacted in the last 3 days
            cutoff_date = datetime.utcnow() - timedelta(days=3)
            
            candidates = Doctor.query.filter(
                Doctor.last_interaction < cutoff_date,
                Doctor.tag.in_(['warm_lead', 'hot_lead'])
            ).all()
            
            return candidates
            
        except Exception as e:
            return []
    
    def generate_follow_up_message(self, doctor):
        """
        Generate follow-up message for a specific doctor
        """
        try:
            # Determine follow-up type based on doctor's tag and history
            if doctor.tag == 'hot_lead':
                template_type = 'interested'
            elif doctor.tag == 'warm_lead':
                template_type = 'interested'
            else:
                template_type = 'inactive'
            
            templates = self.follow_up_templates[template_type]
            template = random.choice(templates)
            
            # Format with doctor's name
            doctor_name = doctor.name.replace('Dr. ', '') if doctor.name else 'Doctor'
            message = template.format(name=doctor_name)
            
            return message
            
        except Exception as e:
            return "Hello, hope you're doing well. Any updates on your requirements?"

class PDFCatalogueReader:
    """
    AI Agent for reading and extracting information from PDF catalogues
    """
    
    def __init__(self):
        self.name = "PDF Catalogue Reader"
        # Mock product database (in real implementation, this would be extracted from PDFs)
        self.products = {
            'surgical_scissors': {
                'name': 'Surgical Scissors',
                'description': 'High-quality stainless steel surgical scissors',
                'price_range': '₹500-₹2000',
                'categories': ['general surgery', 'scissors']
            },
            'forceps': {
                'name': 'Surgical Forceps',
                'description': 'Precision surgical forceps for various procedures',
                'price_range': '₹300-₹1500',
                'categories': ['general surgery', 'forceps']
            },
            'scalpel': {
                'name': 'Surgical Scalpel',
                'description': 'Sharp and precise surgical scalpels',
                'price_range': '₹100-₹500',
                'categories': ['general surgery', 'cutting']
            }
        }
    
    def search_products(self, query):
        """
        Search products based on query
        """
        try:
            query_lower = query.lower()
            results = []
            
            for product_id, product in self.products.items():
                # Check if query matches product name, description, or categories
                if (query_lower in product['name'].lower() or 
                    query_lower in product['description'].lower() or
                    any(query_lower in cat for cat in product['categories'])):
                    results.append(product)
            
            return results
            
        except Exception as e:
            return []
    
    def get_product_info(self, product_name):
        """
        Get detailed information about a specific product
        """
        try:
            for product_id, product in self.products.items():
                if product_name.lower() in product['name'].lower():
                    return product
            
            return None
            
        except Exception as e:
            return None

class OfferEngine:
    """
    AI Agent for generating personalized offers
    """
    
    def __init__(self):
        self.name = "Offer Engine"
        self.offers = {
            'new_customer': {
                'discount': 15,
                'description': 'Welcome offer for new customers',
                'validity': 30
            },
            'bulk_order': {
                'discount': 20,
                'description': 'Bulk order discount (minimum 10 pieces)',
                'validity': 15
            },
            'seasonal': {
                'discount': 10,
                'description': 'Seasonal discount offer',
                'validity': 7
            }
        }
    
    def generate_offer(self, doctor):
        """
        Generate personalized offer for a doctor
        """
        try:
            # Determine offer type based on doctor's history
            message_count = ChatMessage.query.filter_by(doctor_id=doctor.id).count()
            
            if message_count == 0:
                offer_type = 'new_customer'
            elif doctor.tag == 'hot_lead':
                offer_type = 'bulk_order'
            else:
                offer_type = 'seasonal'
            
            offer = self.offers[offer_type]
            
            offer_message = f"""
🎉 Special Offer for Dr. {doctor.name.replace('Dr. ', '') if doctor.name else 'Doctor'}!

Get {offer['discount']}% OFF on all surgical instruments!
{offer['description']}

✅ Valid for {offer['validity']} days
✅ Free shipping on orders above ₹5000
✅ Quality guaranteed

Reply 'INTERESTED' to claim this offer!
            """.strip()
            
            return offer_message
            
        except Exception as e:
            return "Special offer available! Contact us for details."

# Global instances
smart_reply_agent = SmartReplyAgent()
lead_scoring_agent = LeadScoringAgent()
follow_up_engine = FollowUpEngine()
pdf_catalogue_reader = PDFCatalogueReader()
offer_engine = OfferEngine()

