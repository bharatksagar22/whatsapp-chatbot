
## Key Requirements for WhatsApp Chatbot Interface

Based on the provided document, the key requirements for the WhatsApp chatbot interface are:

### Core Functionality:
1.  **Dashboard for 10 WhatsApp Numbers:** A central dashboard to manage and monitor up to 10 different WhatsApp numbers.
2.  **Dual Connection Support:** Ability to connect numbers via both WhatsApp API (Meta API) for stability and scalability, and Web WhatsApp for cost-effectiveness. The system should automatically switch to another number if one gets blocked.
3.  **Real-time Chat Interface:** A real-time chat view showing which number replied and whether the reply was from an Admin or AI. It should also include typing animations and delivery ticks.
4.  **Smart Reply Agent:** An AI agent that understands doctor's questions and provides intelligent, context-aware replies.
5.  **PDF Catalogue Reader/Smart FAQ:** Ability to extract information from PDF catalogues and provide accurate answers to technical questions.
6.  **Lead Scoring & Tagging:** Tagging doctors based on their interest and activity (e.g., cold_lead, warm_lead, hot_lead, registered) and maintaining a score.
7.  **Follow-Up Engine:** Automated smart follow-up messages for inactive doctors.
8.  **Course Funnel Automation:** Guiding doctors through course registration, including sending information, QR/payment links, collecting Ref IDs, and sending reminders.
9.  **Product Order Engine:** Processing product orders, creating carts, handling payments, confirming orders, and sending dispatch notifications.
10. **Manual Message Preview:** Allowing admins to type messages, preview them, and send after confirmation.
11. **AI Learning Engine:** Analyzing replies daily to identify best reply templates and improve low-performing ones.
12. **AI Learning Graph Panel:** Visual tracking of top replies, doctor activity time, and lead trends on the dashboard.
13. **Offer Engine:** AI suggesting smart offers, with admin approval, sent to specific doctors.
14. **Bulk Broadcast Engine:** Sending messages to large groups of doctors (100/500+) with tag/city filters and multi-number splitting.
15. **Voice Reminder System:** Sending audio reminders for courses.
16. **Reports + Export Tools:** Admin access to filters, reports, and downloadable Excel/PDF files (e.g., Dr. Khan – 4 replies, warm_lead, 1 order placed).
17. **Lead Re-engagement:** Smart messages to re-engage cold leads after a period (e.g., 3 months).
18. **Voice Command Interface:** Admin giving commands to AI via voice.
19. **AI Health Monitoring:** Monitoring AI status (Active/Standby Active) and automatically switching to backup AI if the main AI crashes, with crash alerts to admin.
20. **Typing Animation + Delivery Info:** Enhancing user experience with typing animations and delivery information.
21. **Admin-Approved FAQ Engine:** Only answering questions approved by admin, with a fallback for unapproved questions.
22. **Bulk Messaging for 1000+ Doctors:** Load balancing messages across 10+ numbers for large-scale messaging, with retry, rotation, and number shift logic.

### Advanced Features/Marketing Ideas:
1.  **Lead Magnet Automation:** Offering free resources (e.g., Ebook, PDF) in exchange for verified leads.
2.  **Automated Webinar Funnel:** Guiding doctors to webinars, auto-booking links, and sending reminders.
3.  **Retargeting WhatsApp Campaigns:** Re-engaging cold leads with targeted messages.
4.  **Offer Personalization Engine:** Delivering personalized offers based on doctor's activity.
5.  **AI Blog Post Generator + Newsletter:** Generating weekly dental marketing content and sending it via WhatsApp.
6.  **Instant Quotation Generator:** Auto-generating and sending PDF quotations via WhatsApp.
7.  **Referral Booster:** Encouraging referrals with incentives.
8.  **Social Proof Automation:** Displaying testimonials and success stories.
9.  **Video Snippet Bot:** Providing short video links in response to queries.
10. **Geo-Targeted Messages:** Sending location-specific event/course offers.

### System Architecture (SurgiAI Concept):
-   **Multi-Agent Smart AI System:** The system is envisioned as a hierarchical AI agent system.
-   **SurgiAI Master Agent:** A super controller managing all sub-AI agents, handling agent assignment, crash detection, fallback logic, admin commands, analytics, and performance optimizations.
-   **Sub-Agents:** Dedicated agents for specific functions (e.g., Catalogue Reply Agent, WhatsApp Smart Chat Agent, Course Booking Agent, Order & Dispatch Agent, Follow-Up + Tag Agent, Offer Reply Agent, Voice Command Listener, AI Learning Optimizer, Report Generator Agent, FAQ Filter Agent).
-   **Standby Backup AI Agents:** Agents that take over in real-time if a main agent crashes, ensuring no downtime and seamless conversation continuation. These include StandbyAgent1 (Catalogue Replies), StandbyAgent2 (WhatsApp Replies), StandbyAgent3 (Course/Order Module), StandbyAgent4 (Learning/Optimizer).
-   **Crash Recovery AI:** Checks the last state and continues the conversation without restart.
-   **Dashboard View:** A dashboard to monitor the status of AI agents (Live/Down), assigned tasks, last crash time, and recovery status.
-   **Admin Control:** Admin controls permissions and overrides logic.

### Technology Stack (Inferred/Suggested):
-   **Backend:** Likely Python (Flask/FastAPI) for AI agents and API integrations.
-   **Frontend:** Web-based (React/Angular/Vue.js) for the dashboard and chat interface.
-   **Database:** For storing doctor data, chat history, lead scores, order details, etc. (e.g., PostgreSQL, MongoDB).
-   **WhatsApp Integration:** Meta API for official WhatsApp Business API and potentially a library for Web WhatsApp automation (e.g., `whatsapp-web.js` for Node.js or `pywhatkit` for Python, though official API is preferred for stability).
-   **PDF Processing:** Libraries for extracting text from PDFs.
-   **AI/ML:** For smart replies, learning engine, lead scoring, offer personalization (e.g., NLTK, spaCy, scikit-learn, or custom models).
-   **Messaging Queue:** For handling bulk messages and ensuring delivery (e.g., RabbitMQ, Kafka).
-   **Deployment:** Cloud platform (AWS, GCP, Azure) for scalability and reliability.

This comprehensive system aims for 90% automation, real AI replies, a full dashboard, and scalability for 10 to 1000+ doctors.

