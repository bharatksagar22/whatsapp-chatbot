from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class WhatsAppNumber(db.Model):
    __tablename__ = 'whatsapp_numbers'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    connection_type = db.Column(db.String(10), nullable=False)  # 'API' or 'Web'
    status = db.Column(db.String(20), default='standby')  # 'active', 'blocked', 'standby'
    messages_count = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='whatsapp_number', lazy=True)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    city = db.Column(db.String(50))
    tag = db.Column(db.String(20), default='cold_lead')  # 'hot_lead', 'warm_lead', 'cold_lead', 'registered'
    score = db.Column(db.Integer, default=0)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='doctor', lazy=True)
    orders = db.relationship('Order', backref='doctor', lazy=True)
    course_registrations = db.relationship('CourseRegistration', backref='doctor', lazy=True)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    whatsapp_number_id = db.Column(db.Integer, db.ForeignKey('whatsapp_numbers.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'doctor', 'ai', 'admin'
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # 'text', 'image', 'document', 'audio'
    status = db.Column(db.String(20), default='sent')  # 'sent', 'delivered', 'read'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class AIAgent(db.Model):
    __tablename__ = 'ai_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'standby', 'crashed'
    performance = db.Column(db.Float, default=0.0)
    last_crash = db.Column(db.DateTime)
    crash_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'dispatched', 'delivered'
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    ref_id = db.Column(db.String(50))

class CourseRegistration(db.Model):
    __tablename__ = 'course_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    course_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='registered')  # 'registered', 'confirmed', 'attended', 'cancelled'
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    ref_id = db.Column(db.String(50))

class LeadActivity(db.Model):
    __tablename__ = 'lead_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'message_sent', 'pdf_viewed', 'course_inquiry', etc.
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key relationship
    doctor_ref = db.relationship('Doctor', backref='activities')

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    module = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

