"""
╔══════════════════════════════════════════════════════════════════════╗
║       MediBot — Hospital Information Agent  (Streamlit Edition)      ║
║       GlitchCon 2.0  |  GKM_2                                        ║
║                                                                      ║
║  Run:  streamlit run hospital_agent_app.py                           ║
║  Deps: pip install streamlit anthropic twilio google-generativeai    ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st
import json
import difflib
import random
import string
from ai_engine import call_medibot
from datetime import datetime, timedelta
from twilio.rest import Client

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediBot — Hospital Information Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
/* ── Background ── */
.stApp { background: #0a0f1e; color: #e8eaf0; }
/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1427 !important;
    border-right: 1px solid #1e2a45;
}
section[data-testid="stSidebar"] * { color: #e8eaf0 !important; }
/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
/* ── Headings ── */
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; color: #e8eaf0 !important; }
/* ── Chat bubbles ── */
.user-bubble {
    background: linear-gradient(135deg, #0ea5e9, #2dd4bf);
    color: #0a0f1e !important;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 6px 0 6px 60px;
    font-size: 14px;
    line-height: 1.7;
    box-shadow: 0 4px 15px rgba(14,165,233,.25);
}
.bot-bubble {
    background: #111827;
    border: 1px solid #1e2a45;
    color: #e8eaf0 !important;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 6px 60px 6px 0;
    font-size: 14px;
    line-height: 1.7;
}
.bot-bubble strong { color: #2dd4bf; }
/* ── Cards ── */
.info-card {
    background: #111827;
    border: 1px solid #1e2a45;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}
.info-card h4 { color: #2dd4bf !important; margin-bottom: 8px; font-size: 15px; }
.info-card p { color: #8892b0; font-size: 13px; margin: 3px 0; line-height: 1.6; }
/* ── Tags ── */
.tag {
    display: inline-block;
    background: #1e2a45;
    color: #2dd4bf;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}
.tag-green { background: #052e16 !important; color: #22c55e !important; }
.tag-red   { background: #2a0a0a !important; color: #f87171  !important; }
.tag-yellow{ background: #2a1a00 !important; color: #f59e0b  !important; }
/* ── Metric boxes ── */
.metric-box {
    background: #111827;
    border: 1px solid #1e2a45;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    margin-bottom: 12px;
}
.metric-box .value { font-size: 36px; font-weight: 700; color: #2dd4bf; }
.metric-box .label { font-size: 13px; color: #8892b0; margin-top: 4px; }
/* ── Button overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #2dd4bf, #0ea5e9) !important;
    color: #0a0f1e !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: transform .15s !important;
}
.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 16px rgba(45,212,191,.4) !important; }
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: #0d1427; border-bottom: 1px solid #1e2a45; gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4a5580 !important;
    border-radius: 10px 10px 0 0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: #111827 !important;
    color: #2dd4bf !important;
    border-bottom: 2px solid #2dd4bf !important;
}
.stTabs [data-baseweb="tab-panel"] { background: #0a0f1e; padding: 20px 0; }
/* ── Selectbox / text area ── */
.stSelectbox > div > div, .stTextArea textarea {
    background: #111827 !important;
    border: 1px solid #1e2a45 !important;
    color: #e8eaf0 !important;
    border-radius: 12px !important;
}
/* ── Divider ── */
hr { border-color: #1e2a45 !important; }
/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #052e16;
    border: 1px solid #22c55e33;
    color: #22c55e;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
}
.pulse { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.3;} }
/* ── Ticket card ── */
.ticket-card {
    background: #111827;
    border: 1px solid #f59e0b44;
    border-left: 4px solid #f59e0b;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.ticket-id { font-family: monospace; color: #f59e0b; font-size: 13px; }
/* ── Log card ── */
.log-card {
    background: #111827;
    border: 1px solid #f8717144;
    border-left: 4px solid #f87171;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# ──────────────────────────────────────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "hospital": {
        "name": "MediCore General Hospital",
        "hours": "24/7 Emergency | OPD: 8AM–8PM",
        "address": "14, Healthcare Avenue, Bandra West, Mumbai – 400050",
        "phone": "022-4455-1000",
        "email": "info@medicore.in",
    },
    "departments": [
        {"id": "ORTHO",  "name": "Orthopaedics",  "floor": "3rd Floor, Wing B", "head": "DR001", "phone": "022-4455-1001"},
        {"id": "CARDIO", "name": "Cardiology",     "floor": "4th Floor, Wing A", "head": "DR004", "phone": "022-4455-1002"},
        {"id": "NEURO",  "name": "Neurology",      "floor": "5th Floor, Wing C", "head": "DR007", "phone": "022-4455-1003"},
        {"id": "PEDS",   "name": "Paediatrics",    "floor": "2nd Floor, Wing D", "head": "DR009", "phone": "022-4455-1004"},
        {"id": "ONCO",   "name": "Oncology",       "floor": "6th Floor, Wing E", "head": "DR006", "phone": "022-4455-1005"},
    ],
    "doctors": [
        {"id": "DR001", "name": "Dr. Anita Mehta",      "specialty": "Orthopaedics", "dept": "ORTHO",  "fee": 1200, "available": ["Mon","Wed","Fri","Sat"], "slots": ["10:00","11:00","14:00","15:00"], "procedures": ["knee-consult","hip-replacement","fracture-care"]},
        {"id": "DR002", "name": "Dr. Rohan Sharma",     "specialty": "Orthopaedics", "dept": "ORTHO",  "fee": 1000, "available": ["Tue","Thu","Sat"],        "slots": ["09:00","10:00","16:00"],           "procedures": ["knee-consult","sports-injury"]},
        {"id": "DR003", "name": "Dr. Priya Nair",       "specialty": "Orthopaedics", "dept": "ORTHO",  "fee": 900,  "available": ["Mon","Tue","Wed","Thu","Fri"], "slots": ["11:00","12:00","15:00","17:00"], "procedures": ["fracture-care","physiotherapy-ref"]},
        {"id": "DR004", "name": "Dr. Vikram Rao",       "specialty": "Cardiology",   "dept": "CARDIO", "fee": 1500, "available": ["Mon","Wed","Thu","Fri"],    "slots": ["09:00","10:30","14:00"],           "procedures": ["ecg","angiography","cardiac-consult"]},
        {"id": "DR005", "name": "Dr. Sunita Joshi",     "specialty": "Cardiology",   "dept": "CARDIO", "fee": 1400, "available": ["Tue","Thu","Sat"],          "slots": ["10:00","12:00","15:00"],           "procedures": ["ecg","cardiac-consult","stress-test"]},
        {"id": "DR006", "name": "Dr. Amit Desai",       "specialty": "Oncology",     "dept": "ONCO",   "fee": 2000, "available": ["Mon","Tue","Wed","Thu","Fri"], "slots": ["09:00","11:00","14:00","16:00"], "procedures": ["chemo-consult","biopsy","radiation-consult"]},
        {"id": "DR007", "name": "Dr. Kavitha Iyer",     "specialty": "Neurology",    "dept": "NEURO",  "fee": 1800, "available": ["Mon","Wed","Fri"],           "slots": ["10:00","13:00","15:00"],           "procedures": ["mri-consult","eeg","neuro-consult"]},
        {"id": "DR008", "name": "Dr. Suresh Patel",     "specialty": "Neurology",    "dept": "NEURO",  "fee": 1600, "available": ["Tue","Thu","Sat"],           "slots": ["09:30","11:30","14:30"],           "procedures": ["neuro-consult","stroke-consult"]},
        {"id": "DR009", "name": "Dr. Meena Krishnan",   "specialty": "Paediatrics",  "dept": "PEDS",   "fee": 800,  "available": ["Mon","Tue","Wed","Thu","Fri","Sat"], "slots": ["09:00","10:00","11:00","15:00","16:00"], "procedures": ["child-consult","vaccination","growth-assessment"]},
        {"id": "DR010", "name": "Dr. Rahul Gupta",      "specialty": "Paediatrics",  "dept": "PEDS",   "fee": 700,  "available": ["Mon","Wed","Fri","Sat"],     "slots": ["10:00","12:00","16:00"],           "procedures": ["child-consult","neonatal-care"]},
    ],
    "insurance": [
        {"name": "ICICI Lombard",         "code": "ICICI", "covers": ["knee-consult","ecg","cardiac-consult","fracture-care","chemo-consult","neuro-consult","child-consult","angiography"], "cashless": True,  "tpa": "Medi Assist"},
        {"name": "Star Health",           "code": "STAR",  "covers": ["knee-consult","hip-replacement","ecg","cardiac-consult","fracture-care","mri-consult","neuro-consult"],              "cashless": True,  "tpa": "In-house"},
        {"name": "HDFC ERGO",             "code": "HDFC",  "covers": ["cardiac-consult","stress-test","chemo-consult","biopsy","neuro-consult","child-consult"],                            "cashless": True,  "tpa": "Health India TPA"},
        {"name": "Bajaj Allianz",         "code": "BAJAJ", "covers": ["ecg","knee-consult","fracture-care","cardiac-consult","vaccination"],                                                "cashless": False, "tpa": "Paramount TPA"},
        {"name": "New India Assurance",   "code": "NIA",   "covers": ["all-procedures"],                                                                                                  "cashless": True,  "tpa": "Raksha TPA"},
        {"name": "United India Insurance","code": "UII",   "covers": ["cardiac-consult","neuro-consult","fracture-care","child-consult"],                                                  "cashless": False, "tpa": "Family Health Plan"},
        {"name": "Max Bupa",               "code": "MAXB",  "covers": ["all-procedures"],                                                                                                  "cashless": True,  "tpa": "In-house"},
        {"name": "Aditya Birla Health",   "code": "ABH",   "covers": ["chemo-consult","biopsy","radiation-consult","neuro-consult","mri-consult"],                                         "cashless": True,  "tpa": "In-house"},
    ],
    "visiting": {
        "hours": "10AM–12PM and 5PM–7PM",
        "max_visitors": 2,
        "icu": "10AM–11AM only (1 visitor)",
        "pediatric_ward": "Parents allowed 24/7",
        "note": "Sundays: family only, 6PM–7PM",
    },
    "services": [
        "24/7 Emergency & Trauma", "Pharmacy (Round the Clock)",
        "Diagnostic Lab", "Radiology & Imaging (MRI, CT, X-Ray)",
        "Physiotherapy", "Canteen (7AM–10PM)", "Ambulance (Dial 108)",
        "Blood Bank", "ICU & NICU", "Day-Care Surgery",
    ],
    
}

# END OF KNOWLEDGE BASE


def find_closest_doctor(query):
    doctor_names = [d["name"] for d in KNOWLEDGE_BASE["doctors"]]

    match = difflib.get_close_matches(query, doctor_names, n=1, cutoff=0.5)

    if match:
        return match[0]

    return None

# ──────────────────────────────────────────────────────────────────────────────
# SIMULATED TOOLS
# ──────────────────────────────────────────────────────────────────────────────
def query_knowledge_graph(query_text: str) -> dict:
    lq = query_text.lower()
    results = []
    if any(w in lq for w in ["visit", "hour", "time"]):
        results.append({"type": "visiting", "data": KNOWLEDGE_BASE["visiting"]})
    if any(w in lq for w in ["service", "facilit", "lab", "pharmacy"]):
        results.append({"type": "services", "data": KNOWLEDGE_BASE["services"]})
    for doc in KNOWLEDGE_BASE["doctors"]:
        last = doc["name"].lower().split()[-1]
        if last in lq:
            results.append({"type": "doctor", "data": doc})
    for dept in KNOWLEDGE_BASE["departments"]:
        if dept["name"].lower() in lq or dept["id"].lower() in lq:
            results.append({"type": "department", "data": dept})
    if not results:
        results.append({"type": "general", "data": KNOWLEDGE_BASE["hospital"]})
    return {"results": results, "count": len(results)}

def get_doctor_schedule(doctor_id: str, date: str) -> dict:
    doc = next((d for d in KNOWLEDGE_BASE["doctors"] if d["id"] == doctor_id), None)
    if not doc:
        return {"error": f"Doctor {doctor_id} not found"}
    day_map = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
        day_name = day_map[d.weekday()]
    except ValueError:
        day_name = date  
    available = day_name in doc["available"]
    return {
        "doctor": doc["name"], "specialty": doc["specialty"],
        "date": date, "day": day_name, "available": available,
        "slots": doc["slots"] if available else [],
        "fee": doc["fee"],
        "message": f"Dr. {'is' if available else 'is NOT'} available on {day_name}.",
    }

def check_insurance_coverage(insurer_name: str, procedure_code: str) -> dict:
    ins = next(
        (i for i in KNOWLEDGE_BASE["insurance"] 
         if i["name"].lower().replace(" ", "") == insurer_name.lower().replace(" ", "") 
         or i["code"].lower() == insurer_name.lower()),
        None,
    )
    if not ins:
        return {"found": False, "message": f"Insurer '{insurer_name}' not in our partner list."}
    covered = "all-procedures" in ins["covers"] or procedure_code in ins["covers"]
    return {
        "found": True, "insurer": ins["name"],
        "procedure": procedure_code, "covered": covered,
        "cashless": ins["cashless"], "tpa": ins["tpa"],
        "message": (
            f"✅ {ins['name']} {'covers' if covered else 'does NOT cover'} '{procedure_code}'. "
            f"{'Cashless facility available.' if ins['cashless'] else 'Reimbursement only.'} TPA: {ins['tpa']}."
        ),
    }

def trigger_knowledge_refresh(topic: str) -> dict:
    return {
        "refreshed": True, "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "message": f"Knowledge base refreshed for: {topic}. Data is now up to date.",
        "webhook_status": 200,
    }

def create_callback_ticket(patient_details: dict, query_summary: str, department: str) -> dict:
    ticket_id = "CB-" + "".join(random.choices(string.digits, k=5))
    ticket = {
        "ticket_id": ticket_id,
        "status": "Open",
        "patient_details": patient_details,
        "query_summary": query_summary,
        "department": department,
        "eta": "Within 1 hour",
        "created_at": datetime.now().isoformat(),
        "priority": "High" if "emergency" in query_summary.lower() else "Normal",
    }
    if "callback_tickets" not in st.session_state:
        st.session_state.callback_tickets = []
    st.session_state.callback_tickets.append(ticket)
    return ticket

def log_unanswered_query(query_text: str, reason: str) -> dict:
    log = {
        "log_id": "LOG-" + "".join(random.choices(string.digits, k=4)),
        "query": query_text,
        "reason": reason,
        "logged_at": datetime.now().isoformat(),
    }
    if "query_logs" not in st.session_state:
        st.session_state.query_logs = []
    st.session_state.query_logs.append(log)
    return log

# ──────────────────────────────────────────────────────────────────────────────
# REAL OUTBOUND PUSH (SMS & WhatsApp)
# ──────────────────────────────────────────────────────────────────────────────
def push_real_messages(patient_phone, doctor_name, date_str, parking, prep):
    TWILIO_SID = st.secrets["TWILIO_SID"] 
    TWILIO_TOKEN = st.secrets["TWILIO_TOKEN"]
    TWILIO_SMS_NUMBER = "+18705213553" 
    TWILIO_WA_SANDBOX = "whatsapp:+14155238886"

    client = Client(TWILIO_SID, TWILIO_TOKEN)
    msg_body = f"🏥 MediCore Confirmed: Your visit with {doctor_name} on {date_str} is set. 🚗 Parking: {parking} | 📋 Prep: {prep}"

    try:
        sms = client.messages.create(
            body=msg_body,
            from_=TWILIO_SMS_NUMBER,
            to=patient_phone
        )
        wa = client.messages.create(
            body=msg_body,
            from_=TWILIO_WA_SANDBOX,
            to=f"whatsapp:{patient_phone}"
        )
        return True, sms.sid, wa.sid
    except Exception as e:
        return False, str(e), None

# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT & AI ENGINE
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""
You are MediBot, a hospital assistant.

Rules:
- Use simple plain text
- Do NOT use markdown like ** or ***
- Use bullet points with •
- You are warm, empathetic, professional, and highly efficient

HOSPITAL KNOWLEDGE BASE:
{json.dumps(KNOWLEDGE_BASE, indent=2)}

CAPABILITIES & RULES:
1. Answer multi-part queries by reasoning across all knowledge domains in one response.
2. Cross-reference doctor availability + insurance coverage + department info.
3. For billing disputes, collect name & phone, then say a callback ticket is created.
4. Always mention consultation fees when discussing appointments.
5. Use bold for section headers, bullet points for lists. Be concise.

CRITICAL BOOKING PROTOCOL (DO NOT IGNORE):
- IF the user wants to book an appointment, YOU MUST ask for their phone number (must include +91).
- ONCE the user gives you their phone number to confirm the booking, YOU MUST output a secret trigger code at the VERY END of your message.
- The format MUST be exactly: $$BOOKING|Doctor Name|Date|PhoneNumber$$
- Example: $$BOOKING|Dr. Anita Mehta|Thursday|+919876543210$$
- DO NOT put any text after the $$BOOKING$$ string. THIS IS MANDATORY FOR SYSTEM INTEGRATION.

Today is {datetime.now().strftime('%A, %d %B %Y')}.
"""
# ──────────────────────────────────────────────────────────────────────────────
# AI ENGINE
# ──────────────────────────────────────────────────────────────────────────────
from groq import Groq

client = client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def call_medibot(messages):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages
    )

    return response.choices[0].message.content
# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          
if "api_messages" not in st.session_state:
    st.session_state.api_messages = []          
if "callback_tickets" not in st.session_state:
    st.session_state.callback_tickets = []
if "query_logs" not in st.session_state:
    st.session_state.query_logs = []

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <div style='font-size:48px;'>\U0001F3E5</div>
        <div style='font-family:"DM Serif Display",serif; font-size:20px; color:#e8eaf0; margin-top:8px;'>MediBot</div>
        <div style='font-size:12px; color:#4a5580; margin-top:4px;'>Hospital Information Agent</div>
        <div style='margin-top:10px;'>
            <span class="status-badge">
                <span class="pulse"></span> Online 24/7
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="value">{len(st.session_state.chat_history) // 2}</div>
            <div class="label">Queries</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="value">{len(st.session_state.callback_tickets)}</div>
            <div class="label">Tickets</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div style='font-size:12px; color:#4a5580; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Quick Actions</div>", unsafe_allow_html=True)
    if st.button("🔄  Refresh Knowledge Base", use_container_width=True):
        result = trigger_knowledge_refresh("all-departments")
        st.success(f"✅ {result['message']}")
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.api_messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<div style='font-size:12px; color:#4a5580; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Simulated Webhook Payload</div>", unsafe_allow_html=True)
    webhook_payload = {
        "event": "schedule_update",
        "doctor_id": "DR001",
        "doctor_name": "Dr. Anita Mehta",
        "update": {"added_slot": "16:00", "date": "Saturday"},
        "timestamp": datetime.now().isoformat(),
    }
    st.json(webhook_payload)

    st.markdown("---")
    st.markdown("<div style='font-size:11px; color:#3a4560; text-align:center;'>GlitchCon 2.0 · GKM_2</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN AREA — TABS
# ──────────────────────────────────────────────────────────────────────────────
tab_chat, tab_kb, tab_tools, tab_tickets, tab_logs = st.tabs([
    "💬  Chat",
    "🗄️  Knowledge Base",
    "🔧  Tools Demo",
    "🎫  Callback Tickets",
    "📋  Query Logs",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — CHAT 
# ──────────────────────────────────────────────────────────────────────────────
with tab_chat:
    st.markdown("""
    <h2 style='margin-bottom:4px;'>🤖 MediBot Chat</h2>
    <p style='color:#4a5580; font-size:14px; margin-bottom:20px;'>
        Ask anything about doctors, insurance, or book an appointment.
    </p>
    """, unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown("""
        <div class="bot-bubble">
            👋 Hello! I'm <strong>MediBot</strong>, your 24/7 Hospital Information Agent for
            <strong>MediCore General Hospital</strong>.<br><br>
            I can help you with:<br>
            • 🗓️ Doctor schedules &amp; availability<br>
            • 🏥 Department locations &amp; services<br>
            • 💳 Insurance coverage verification<br>
            • ⏰ Visiting hours &amp; policies<br>
            • 📋 Appointment booking guidance<br><br>
            How can I assist you today?
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style='text-align:right; margin-bottom:4px;'>
                <span style='font-size:11px; color:#3a4560;'>You · {msg['time']}</span>
            </div>
            <div class="user-bubble">{msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='margin-bottom:4px;'>
                <span style='font-size:11px; color:#3a4560;'>🤖 MediBot · {msg['time']}</span>
            </div>
            <div class="bot-bubble">{msg['content'].replace(chr(10), '<br>')}</div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:12px; color:#4a5580; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>Sample Queries</div>", unsafe_allow_html=True)
    sample_queries = [
        "Is Dr. Mehta available on Saturday for knee consult?",
        "What are visiting hours and ICU rules?",
        "Where is Oncology and what services does it offer?",
    ]
    cols = st.columns(3)
    for i, q in enumerate(sample_queries):
        if cols[i % 3].button(q, key=f"sample_{i}", use_container_width=True):
            st.session_state._pending_query = q

    st.markdown("---")

    query = None
    if hasattr(st.session_state, "_pending_query"):
        query = st.session_state._pending_query
        del st.session_state._pending_query
    elif chat_val := st.chat_input("Type your message here and press Enter..."):
        query = chat_val

        corrected_doc = find_closest_doctor(query)

        if corrected_doc:
            query = f"{query} (User may mean: {corrected_doc})"
    if query:
        now = datetime.now().strftime("%I:%M %p")

        st.session_state.chat_history.append({"role": "user", "content": query, "time": now})
        st.session_state.api_messages.append({"role": "user", "content": query})

        if any(w in query.lower() for w in ["billing", "dispute", "invoice", "bill"]):
            create_callback_ticket(
                patient_details={"query": query, "source": "chat"},
                query_summary=query,
                department="Billing Department",
            )

        with st.spinner("MediBot is thinking…"):
            try:
                reply = call_medibot(st.session_state.api_messages)
                
                # --- AGENT ACTION: INTERCEPT BOOKING TRIGGER ---
                if "$$BOOKING|" in reply:
                    try:
                        trigger_data = reply.split("$$BOOKING|")[1].split("$$")[0].strip()
                        parts = trigger_data.split("|")
                        doc_name = parts[0].strip()
                        date_str = parts[1].strip()
                        phone_num = parts[2].strip().replace(" ", "").replace("-", "")
                        
                        reply = reply.split("$$BOOKING|")[0].strip()
                        
                        doc_info = next((d for d in KNOWLEDGE_BASE["doctors"] if d["name"] == doc_name), None)
                        fee = doc_info["fee"] if doc_info else 1400
                        half_fee = fee / 2
                        parking = "Zone B (Hospital Main)"
                        prep = "Please bring ID and arrive 15 mins early."
                        
                        st.session_state.pending_payment = {
                            "phone_num": phone_num,
                            "doc_name": doc_name,
                            "date_str": date_str,
                            "amount": half_fee,
                            "parking": parking,
                            "prep": prep
                        }
                        
                        st.warning(f"💳 Booking reserved. Please complete the 50% advance payment (₹{half_fee:g}) to confirm the slot.")
                        
                    except Exception as parse_err:
                        print("Trigger parsing failed:", parse_err)
                # ────────────────────────────────────────────────

            except Exception as e:
                reply = f"⚠️ I'm experiencing a technical issue: {str(e)}. Please try again."
                log_unanswered_query(query, f"API error: {str(e)}")

        st.session_state.chat_history.append({"role": "assistant", "content": reply, "time": now})
        st.session_state.api_messages.append({"role": "assistant", "content": reply})

        if any(w in reply.lower() for w in ["i don't have", "unable to find", "not in my knowledge"]):
            log_unanswered_query(query, "No matching knowledge base entry")
            
        st.rerun()

    # --- QR CODE PAYMENT SECTION ---
    if st.session_state.get("pending_payment"):
        pmt = st.session_state.pending_payment
        st.markdown("---")
        st.markdown(f"### 💳 Complete Payment of ₹{pmt['amount']:g} to Confirm")
        
        # Free QR API using quickchart or qrserver for UPI URL
        import urllib.parse
        upi_url = f"upi://pay?pa=hospital@upi&pn=MediCore%20Hospital&am={pmt['amount']}&cu=INR"
        encoded_upi = urllib.parse.quote(upi_url)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_upi}"
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(qr_url, caption="Scan with any UPI APP", width=220)
        with col2:
            st.info(f"**Doctor:** {pmt['doc_name']}\n\n**Date:** {pmt['date_str']}\n\n**Advance Fee:** ₹{pmt['amount']:g}")
            if st.button("✅ I have completed the payment", use_container_width=True, type="primary"):
                with st.spinner("Verifying payment & despatching Pre-Kit..."):
                    import time
                    time.sleep(1.5)  # Simulate network call
                    success, sms_id, wa_id = push_real_messages(
                        pmt["phone_num"], pmt["doc_name"], pmt["date_str"], pmt["parking"], pmt["prep"]
                    )
                    st.session_state.payment_success = True
                    st.session_state.pending_payment = None
                    st.rerun()

    if st.session_state.get("payment_success"):
        st.success("🎉 Payment received successfully! WhatsApp & SMS Prep-Kit dispatched!")
        st.balloons()
        st.session_state.payment_success = False

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — KNOWLEDGE BASE
# ──────────────────────────────────────────────────────────────────────────────
with tab_kb:
    st.markdown("<h2>📚 Knowledge Base Explorer</h2>", unsafe_allow_html=True)
    kb_section = st.selectbox(
        "Browse Section",
        ["🏥 Departments", "👨‍⚕️ Doctors", "💳 Insurance Partners", "🛎️ Services", "⏰ Visiting Hours"],
    )

    if kb_section == "🏥 Departments":
        cols = st.columns(2)
        for i, dept in enumerate(KNOWLEDGE_BASE["departments"]):
            head = next((d for d in KNOWLEDGE_BASE["doctors"] if d["id"] == dept["head"]), None)
            with cols[i % 2]:
                docs_in_dept = [d for d in KNOWLEDGE_BASE["doctors"] if d["dept"] == dept["id"]]
                st.markdown(f"""
                <div class="info-card">
                    <h4>🏥 {dept['name']}</h4>
                    <p>📍 <strong>Location:</strong> {dept['floor']}</p>
                    <p>📞 <strong>Phone:</strong> {dept['phone']}</p>
                    <p>👨‍⚕️ <strong>Head:</strong> {head['name'] if head else 'N/A'}</p>
                    <p>🩺 <strong>Doctors:</strong> {len(docs_in_dept)}</p>
                </div>
                """, unsafe_allow_html=True)

    elif kb_section == "👨‍⚕️ Doctors":
        filter_dept = st.selectbox("Filter by Department", ["All"] + [d["name"] for d in KNOWLEDGE_BASE["departments"]])
        filtered_docs = KNOWLEDGE_BASE["doctors"]
        if filter_dept != "All":
            dept_id = next(d["id"] for d in KNOWLEDGE_BASE["departments"] if d["name"] == filter_dept)
            filtered_docs = [d for d in filtered_docs if d["dept"] == dept_id]
            
        cols = st.columns(2)
        for i, doc in enumerate(filtered_docs):
            with cols[i % 2]:
                avail_tags = " ".join([f'<span class="tag">{day}</span>' for day in doc["available"]])
                proc_tags  = " ".join([f'<span class="tag" style="background:#0a1a2a;color:#8892b0;">{p}</span>' for p in doc["procedures"]])
                st.markdown(f"""
                <div class="info-card">
                    <h4>👨‍⚕️ {doc['name']}</h4>
                    <p>🔬 <strong>Specialty:</strong> {doc['specialty']}</p>
                    <p>💰 <strong>Fee:</strong> ₹{doc['fee']}</p>
                    <p><strong>Available:</strong> {avail_tags}</p>
                    <p style='margin-top:6px;'><strong>Procedures:</strong><br>{proc_tags}</p>
                </div>
                """, unsafe_allow_html=True)

    elif kb_section == "💳 Insurance Partners":
        cols = st.columns(2)
        for i, ins in enumerate(KNOWLEDGE_BASE["insurance"]):
            with cols[i % 2]:
                cashless_tag = '<span class="tag tag-green">Cashless ✓</span>' if ins["cashless"] else '<span class="tag tag-red">Reimbursement Only</span>'
                cover_preview = ins["covers"][:4] if ins["covers"] != ["all-procedures"] else ["All Procedures"]
                cover_tags = " ".join([f'<span class="tag" style="background:#0a1a2a;color:#8892b0;">{c}</span>' for c in cover_preview])
                st.markdown(f"""
                <div class="info-card">
                    <h4>💳 {ins['name']}</h4>
                    <p>{cashless_tag}</p>
                    <p>🏢 <strong>TPA:</strong> {ins['tpa']}</p>
                    <p style='margin-top:6px;'><strong>Sample Coverage:</strong><br>{cover_tags}</p>
                </div>
                """, unsafe_allow_html=True)

    elif kb_section == "🛎️ Services":
        cols = st.columns(3)
        for i, svc in enumerate(KNOWLEDGE_BASE["services"]):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="info-card" style='text-align:center;'>
                    <p style='font-size:15px; color:#e8eaf0; font-weight:600;'>{svc}</p>
                </div>
                """, unsafe_allow_html=True)

    elif kb_section == "⏰ Visiting Hours":
        v = KNOWLEDGE_BASE["visiting"]
        h = KNOWLEDGE_BASE["hospital"]
        st.markdown(f"""
        <div class="info-card">
            <h4>⏰ General Visiting Hours</h4>
            <p>🕐 {v['hours']}</p>
            <p>👥 Max Visitors: {v['max_visitors']} per patient</p>
        </div>
        <div class="info-card">
            <h4>🚨 ICU Visiting</h4>
            <p>{v['icu']}</p>
        </div>
        <div class="info-card">
            <h4>👶 Paediatric Ward</h4>
            <p>{v['pediatric_ward']}</p>
        </div>
        <div class="info-card">
            <h4>📅 Sunday Policy</h4>
            <p>{v['note']}</p>
        </div>
        <div class="info-card">
            <h4>🏥 Hospital Contact</h4>
            <p>📍 {h['address']}</p>
            <p>📞 {h['phone']}</p>
            <p>✉️ {h['email']}</p>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — TOOLS DEMO
# ──────────────────────────────────────────────────────────────────────────────
with tab_tools:
    st.markdown("<h2>🔧 Simulated Tool Tester</h2>", unsafe_allow_html=True)
    
    tool_choice = st.selectbox("Select Tool", [
        "query_knowledge_graph",
        "get_doctor_schedule",
        "check_insurance_coverage",
        "trigger_knowledge_refresh",
        "create_callback_ticket",
        "log_unanswered_query",
    ])

    if tool_choice == "query_knowledge_graph":
        q = st.text_input("Query Text", "visiting hours for ICU")
        if st.button("Run Tool", key="t1"):
            st.json(query_knowledge_graph(q))
            
    elif tool_choice == "get_doctor_schedule":
        doc_options = {d["name"]: d["id"] for d in KNOWLEDGE_BASE["doctors"]}
        doc_name = st.selectbox("Doctor", list(doc_options.keys()))
        date = st.date_input("Date")
        if st.button("Run Tool", key="t2"):
            st.json(get_doctor_schedule(doc_options[doc_name], str(date)))
            
    elif tool_choice == "check_insurance_coverage":
        ins_options = [i["name"] for i in KNOWLEDGE_BASE["insurance"]]
        insurer = st.selectbox("Insurer", ins_options)
        all_procs = sorted(set(p for d in KNOWLEDGE_BASE["doctors"] for p in d["procedures"]))
        procedure = st.selectbox("Procedure Code", all_procs)
        if st.button("Run Tool", key="t3"):
            st.json(check_insurance_coverage(insurer, procedure))
            
    elif tool_choice == "trigger_knowledge_refresh":
        topic = st.text_input("Topic to Refresh", "doctor-schedules")
        if st.button("Run Tool", key="t4"):
            st.json(trigger_knowledge_refresh(topic))
            
    elif tool_choice == "create_callback_ticket":
        name  = st.text_input("Patient Name", "Ravi Kumar")
        phone = st.text_input("Phone Number", "+91-9876543210")
        dept  = st.selectbox("Department", [d["name"] for d in KNOWLEDGE_BASE["departments"]] + ["Billing Department"])
        query = st.text_area("Query Summary", "Patient has a billing dispute.")
        if st.button("Create Ticket", key="t5"):
            result = create_callback_ticket({"name": name, "phone": phone}, query, dept)
            st.success(f"✅ Ticket created: **{result['ticket_id']}**")
            st.json(result)
            
    elif tool_choice == "log_unanswered_query":
        q      = st.text_input("Query Text", "Dental department?")
        reason = st.text_input("Reason", "No entry")
        if st.button("Log Query", key="t6"):
            result = log_unanswered_query(q, reason)
            st.success(f"✅ Logged as **{result['log_id']}**")
            st.json(result)

    st.markdown("---")
    st.markdown("### 📲 Dispatch Real Prep-Kit")
    target_phone = st.text_input("Enter Demo Phone Number (Include +91)", value="+91")

    if st.button("🔥 PUSH LIVE SMS & WHATSAPP", type="primary"):
        with st.spinner("Connecting to Telecom Gateway..."):
            success, sms_result, wa_result = push_real_messages(
                patient_phone=target_phone,
                doctor_name="Dr. Anita Mehta",
                date_str="Saturday",
                parking="Zone B (Blue)",
                prep="Bring past X-Rays. Fasting not required."
            )
            
        if success:
            st.success("SUCCESS! Check your phone.")
            st.balloons()
        else:
            st.error(f"Failed to send. Error: {sms_result}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — CALLBACK TICKETS
# ──────────────────────────────────────────────────────────────────────────────
with tab_tickets:
    st.markdown("<h2>🎫 Callback Tickets</h2>", unsafe_allow_html=True)
    tickets = st.session_state.callback_tickets
    if not tickets:
        st.markdown("<div style='text-align:center; padding:60px;'>No escalation tickets yet.</div>", unsafe_allow_html=True)
    else:
        for t in reversed(tickets):
            st.markdown(f"""
            <div class="ticket-card">
                <span class="ticket-id">#{t['ticket_id']}</span>
                <h4 style='color:#f59e0b; margin: 6px 0;'>{t['department']}</h4>
                <p style='color:#8892b0; font-size:13px;'>"{t['query_summary']}"</p>
                <div style='margin-top:8px;'>
                    <span class="tag tag-green">ETA: {t['eta']}</span>
                    <span class="tag">{t['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 5 — QUERY LOGS
# ──────────────────────────────────────────────────────────────────────────────
with tab_logs:
    st.markdown("<h2>📋 Unanswered Query Logs</h2>", unsafe_allow_html=True)
    logs = st.session_state.query_logs
    if not logs:
        st.markdown("<div style='text-align:center; padding:60px;'>No knowledge gaps logged yet.</div>", unsafe_allow_html=True)
    else:
        for log in reversed(logs):
            st.markdown(f"""
            <div class="log-card">
                <span style='font-family:monospace; color:#f87171; font-size:12px;'>{log['log_id']}</span>
                <p style='color:#e8eaf0; font-size:14px; margin: 6px 0;'>"{log['query']}"</p>
                <p style='color:#8892b0; font-size:12px;'>Reason: {log['reason']}</p>
            </div>

            """, unsafe_allow_html=True)
