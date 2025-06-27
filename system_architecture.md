
## System Architecture Outline

Based on the requirements outlined in `WHATSAPP_summary.md`, the system architecture for the WhatsApp chatbot interface will be designed as a modular, scalable, and resilient system, adhering to the 'SurgiAI' concept of a Master Agent controlling various Sub-Agents and Standby Agents for high availability.

### 1. High-Level Architecture:

*   **Frontend (Dashboard & Chat Interface):** A web-based application providing the user interface for admins to manage WhatsApp numbers, view chats, monitor AI performance, and access reports.
*   **Backend (Core Logic & APIs):** The central processing unit, handling all business logic, AI agent orchestration, WhatsApp integrations, database interactions, and communication with the frontend.
*   **Database:** For persistent storage of chat history, doctor profiles, lead scores, order details, course registrations, AI learning data, and system configurations.
*   **WhatsApp Integration Layer:** Responsible for connecting to WhatsApp via Meta API and Web WhatsApp, managing multiple numbers, and handling message sending/receiving.
*   **AI Agents Layer:** A collection of specialized AI modules (Sub-Agents) managed by a Master Agent, with Standby Agents for failover.

### 2. Detailed Component Breakdown:

#### 2.1. Frontend:
*   **Technology:** React.js (or similar modern JavaScript framework like Vue.js/Angular) for a dynamic and responsive user interface.
*   **Key Modules:**
    *   **Dashboard:** Overview of system status, AI agent health, lead trends, and quick access to key features.
    *   **WhatsApp Number Management:** Interface to add/remove WhatsApp numbers, configure API/Web WhatsApp connections, and monitor their status.
    *   **Chat Interface:** Real-time display of conversations, including sender identification (Admin/AI), message status (sent, delivered, read), and typing indicators. Ability to send messages.
    *   **Reports & Analytics:** Visualizations and downloadable reports on doctor activity, lead scoring, offer performance, and AI learning.
    *   **Admin Controls:** User management, role-based access, system configuration, and manual message preview/sending.

#### 2.2. Backend:
*   **Technology:** Python with Flask or FastAPI for RESTful APIs and efficient handling of AI logic. Asynchronous capabilities will be crucial for real-time chat and bulk messaging.
*   **Key Modules:**
    *   **API Gateway/Controller:** Manages all incoming requests from the frontend and outgoing responses.
    *   **WhatsApp Webhook Handler:** Receives incoming messages and status updates from WhatsApp (Meta API) and Web WhatsApp instances.
    *   **Message Router:** Directs incoming messages to the appropriate AI Agent or Admin for processing.
    *   **SurgiAI Master Agent (Orchestrator):**
        *   Manages the lifecycle of all Sub-Agents.
        *   Monitors agent health and triggers failover to Standby Agents.
        *   Assigns tasks to Sub-Agents based on message content and context.
        *   Handles admin commands and system-wide configurations.
    *   **Sub-Agents (as defined in WHATSAPP.txt):** Each will be a distinct module/service.
        *   Smart Reply Agent
        *   PDF Catalogue Reader / Smart FAQ from PDF
        *   Lead Scoring & Tagging
        *   Follow-Up Engine
        *   Course Funnel Automation
        *   Product Order Engine
        *   Manual Message Preview Handler
        *   AI Learning Engine
        *   Offer Engine
        *   Bulk Broadcast Engine
        *   Voice Reminder System Integration
        *   Reports Generation Logic
        *   Lead Re-engagement Engine
        *   Voice Command Interface (Speech-to-Text integration)
        *   AI Health Monitoring & Crash Recovery
        *   Admin-Approved FAQ Engine
        *   Bulk Messaging for 1000+ Doctors (Load Balancer)
    *   **Standby Agents:** Mirroring critical Sub-Agents for high availability.
    *   **Database Service Layer:** Abstraction for database interactions.
    *   **Authentication & Authorization:** Secure access control for admin users.
    *   **Task Queue/Message Broker:** (e.g., Celery with Redis/RabbitMQ) for asynchronous tasks like bulk messaging, follow-ups, and AI processing to prevent blocking the main application.

#### 2.3. Database:
*   **Technology:** PostgreSQL (Relational Database) for structured data like user profiles, WhatsApp numbers, chat metadata, lead scores, orders, courses, and system configurations. MongoDB (NoSQL Database) could be considered for chat message storage due to its flexible schema, but PostgreSQL with JSONB fields can also handle this effectively.
*   **Key Data Models:**
    *   Users (Admins)
    *   Doctors (Leads)
    *   WhatsApp Numbers (with connection type and status)
    *   Chat Messages (history, sender, timestamp, status)
    *   Lead Tags & Scores
    *   Courses & Registrations
    *   Products & Orders
    *   Offers
    *   AI Learning Data (templates, performance metrics)
    *   System Logs & Crash Reports

#### 2.4. WhatsApp Integration Layer:
*   **Meta API Integration:** Using official Meta Business API for stable and scalable messaging. This will involve setting up webhooks and using their SDK/APIs.
*   **Web WhatsApp Integration:** For numbers not on Meta API, a headless browser automation library (e.g., `whatsapp-web.js` via Node.js or `pywhatkit` via Python, though `whatsapp-web.js` is more robust for this purpose) will be used. This will require careful management of browser instances and session data.
*   **Number Switching Logic:** A robust mechanism to detect blocked numbers and automatically switch to available ones for outgoing messages.

### 3. Technology Stack Summary:
*   **Frontend:** React.js, HTML5, CSS3, JavaScript
*   **Backend:** Python (Flask/FastAPI), Celery (for task queue), Redis/RabbitMQ (message broker)
*   **Database:** PostgreSQL
*   **WhatsApp Integration:** Meta API, `whatsapp-web.js` (Node.js) for Web WhatsApp automation
*   **AI/ML:** Python libraries like NLTK, spaCy, scikit-learn, or custom models for NLP and learning components.
*   **Deployment:** Docker for containerization, Kubernetes for orchestration (optional for initial deployment, but good for scalability), Cloud platform (AWS/GCP/Azure) for hosting.

This architecture provides a solid foundation for building the comprehensive WhatsApp chatbot interface with all the specified features, ensuring scalability, reliability, and maintainability.

