import streamlit as st
import base64
import time
from datetime import datetime
from app.llm.groq import call_groq
from app.llm.gemini import call_gemini
from app.firewall.classifier import classify_risk, should_block_prompt, get_detailed_analysis
from app.firewall.redactor import PromptRedactor
from app.logging.logger import PromptLogger
from app.auth.admin import AdminAuth
from app.admin.dashboard import AdminDashboard
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Initialize logger and auth
logger = PromptLogger()
auth = AdminAuth()
admin_dashboard = AdminDashboard()

# --- Page Configuration ---
st.set_page_config(
    page_title="SecureMyAI",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="auto",
)

# --- Background Visual ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: scroll;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# As we can't add a real image file, we'll use a dark gradient as a placeholder
# In a real scenario, you would replace this with set_png_as_page_bg('background.png')
def set_dark_gradient_bg():
    page_bg_css = """
    <style>
    .stApp {
        background: linear-gradient(to right top, #0d1117, #1f2833, #31404f, #44586c, #58728a);
        background-attachment: fixed;
    }
    </style>
    """
    st.markdown(page_bg_css, unsafe_allow_html=True)

set_dark_gradient_bg()

# --- Session State Management ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'admin_user' not in st.session_state:
    st.session_state.admin_user = None
if 'admin_last_activity' not in st.session_state:
    st.session_state.admin_last_activity = None
if 'result' not in st.session_state:
    st.session_state.result = None
if 'error' not in st.session_state:
    st.session_state.error = None

# --- Admin Authentication ---
def admin_login():
    """Render admin login form."""
    st.title("🔐 Admin Login")
    st.markdown("---")
    
    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Login")
        with col2:
            if st.form_submit_button("Back to Main"):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        if submitted:
            if username and password:
                result = auth.authenticate(username, password)
                if result['success']:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_user = result['user']
                    st.session_state.admin_last_activity = datetime.now().isoformat()
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.error("Please enter both username and password.")

def admin_logout():
    """Logout admin user."""
    st.session_state.admin_logged_in = False
    st.session_state.admin_user = None
    st.session_state.admin_last_activity = None
    st.rerun()

# --- Sidebar Navigation ---
st.sidebar.title("🛡️ SecureMyAI")

# Check admin session validity
if st.session_state.admin_logged_in:
    if not auth.is_valid_session(st.session_state):
        st.session_state.admin_logged_in = False
        st.session_state.admin_user = None
        st.session_state.admin_last_activity = None

# Navigation options
if st.session_state.admin_logged_in:
    # Admin is logged in
    st.sidebar.success(f"👤 Logged in as: {st.session_state.admin_user['username']}")
    
    page = st.sidebar.radio("Navigation", [
        "Admin Dashboard", 
        "User Management", 
        "Security Monitoring", 
        "Audit Logs", 
        "System Settings",
        "Help & Docs",
        "Prompt Analysis", 
        "Prompt History"
    ])
    
    # Update last activity
    st.session_state.admin_last_activity = datetime.now().isoformat()
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        admin_logout()
else:
    # Regular user navigation
    page = st.sidebar.radio("Navigation", ["Prompt Analysis", "Prompt History", "Admin Login"])

# --- Admin Pages ---
if st.session_state.admin_logged_in:
    if page == "Admin Dashboard":
        admin_dashboard.render_dashboard()
    
    elif page == "User Management":
        admin_dashboard.render_user_management()
    
    elif page == "Security Monitoring":
        admin_dashboard.render_security_monitoring()
    
    elif page == "Audit Logs":
        admin_dashboard.render_audit_logs()
    
    elif page == "System Settings":
        admin_dashboard.render_system_settings()
    
    elif page == "Help & Docs":
        admin_dashboard.render_help_documentation()

# --- Admin Login Page ---
elif page == "Admin Login":
    admin_login()

# --- Regular User Pages ---
else:
    # --- Prompt History Page ---
    if page == "Prompt History":
        st.title("📋 Prompt History")
        st.markdown("---")
        
        # Get statistics
        stats = logger.get_statistics()
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Prompts", stats['total_prompts'])
        with col2:
            st.metric("Blocked", stats['blocked_prompts'])
        with col3:
            st.metric("Redacted", stats['redacted_prompts'])
        with col4:
            high_risk = stats['risk_levels'].get('high', 0)
            st.metric("High Risk", high_risk)
        
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_filter = st.selectbox(
                "Risk Level",
                ["All", "low", "medium", "high"],
                index=0
            )
        
        with col2:
            model_filter = st.selectbox(
                "Model",
                ["All", "groq", "gemini"],
                index=0
            )
        
        with col3:
            search_term = st.text_input("Search prompts", placeholder="Enter keywords...")
        
        # Get filtered logs
        logs = logger.get_recent_logs(100)  # Get last 100 logs
        
        # Apply filters
        if risk_filter != "All":
            logs = [log for log in logs if log.get('risk_level') == risk_filter]
        
        if model_filter != "All":
            logs = [log for log in logs if log.get('model_used') == model_filter]
        
        if search_term:
            logs = [log for log in logs if search_term.lower() in log.get('prompt', '').lower()]
        
        # Display logs
        st.subheader(f"📊 Results ({len(logs)} entries)")
        
        if not logs:
            st.info("No prompts found matching your filters.")
        else:
            for i, log in enumerate(reversed(logs)):  # Show newest first
                with st.expander(f"📝 {log['prompt'][:50]}{'...' if len(log['prompt']) > 50 else ''}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Original Prompt:**")
                        st.code(log['prompt'])
                        
                        if log.get('redacted_prompt'):
                            st.write("**Redacted Prompt:**")
                            st.code(log['redacted_prompt'])
                        
                        if log.get('llm_response'):
                            st.write("**LLM Response:**")
                            st.markdown(log['llm_response'][:200] + "..." if len(log['llm_response']) > 200 else log['llm_response'])
                    
                    with col2:
                        # Risk level badge
                        risk_level = log.get('risk_level', 'unknown')
                        if risk_level == 'high':
                            st.error(f"Risk: {risk_level.upper()}")
                        elif risk_level == 'medium':
                            st.warning(f"Risk: {risk_level.upper()}")
                        else:
                            st.success(f"Risk: {risk_level.upper()}")
                        
                        # Other details
                        st.write(f"**Model:** {log.get('model_used', 'N/A').upper()}")
                        st.write(f"**Blocked:** {'Yes' if log.get('should_block') else 'No'}")
                        st.write(f"**Redacted:** {'Yes' if log.get('was_redacted') else 'No'}")
                        st.write(f"**Time:** {log.get('timestamp', 'N/A')[:19]}")
                        st.write(f"**Processing:** {log.get('processing_time_ms', 0)}ms")
                        
                        # PII and keywords
                        if log.get('pii_detected'):
                            st.write(f"**PII:** {', '.join(log['pii_detected'])}")
                        
                        if log.get('high_risk_keywords'):
                            st.write(f"**High Risk:** {', '.join(log['high_risk_keywords'])}")
                        
                        if log.get('medium_risk_keywords'):
                            st.write(f"**Medium Risk:** {', '.join(log['medium_risk_keywords'])}")

    # --- Prompt Analysis Page ---
    else:
        st.title("🛡️ SecureMyAI Prompt Firewall")
        st.markdown("---")

        with st.form("prompt_form"):
            prompt = st.text_area(
                "Enter your prompt below:",
                height=150,
                placeholder="e.g., How can I build a secure authentication system?",
            )

            llm_option = st.radio(
                "Choose your LLM:",
                ("Groq (Mixtral)", "Gemini 2.5"),
                horizontal=True,
            )

            submitted = st.form_submit_button("Analyze Prompt")

        if submitted:
            if not prompt:
                st.session_state.error = "Please enter a prompt."
                st.session_state.result = None
            else:
                st.session_state.error = None
                st.session_state.result = None
                
                # Start timing
                start_time = time.time()
                
                with st.spinner("Analyzing... Please wait."):
                    try:
                        llm_choice = "groq" if "Groq" in llm_option else "gemini"
                        
                        # 1. Get detailed analysis
                        detailed_analysis = get_detailed_analysis(prompt)
                        
                        # 2. Check if prompt should be blocked
                        should_block, block_reason = should_block_prompt(prompt)
                        
                        # 3. Initialize redactor
                        redactor = PromptRedactor()
                        
                        # 4. Handle different risk levels
                        llm_response = None
                        redaction_result = None
                        
                        if should_block:
                            # High risk - block completely
                            llm_response = f"🚫 **PROMPT BLOCKED**\n\n**Reason:** {block_reason}\n\nThis prompt contains sensitive information and has been blocked for security reasons."
                        else:
                            # Low or medium risk - proceed with potential redaction
                            if detailed_analysis["risk_level"] == "medium":
                                # Medium risk - redact and send to LLM
                                redaction_result = redactor.redact_prompt(prompt)
                                prompt_to_send = redaction_result["redacted_prompt"]
                            else:
                                # Low risk - send original prompt
                                prompt_to_send = prompt
                            
                            # Send to LLM
                            if llm_choice == "groq":
                                llm_response = call_groq(prompt_to_send)
                            else:
                                llm_response = call_gemini(prompt_to_send)
                        
                        # Calculate processing time
                        processing_time_ms = int((time.time() - start_time) * 1000)
                        
                        # 5. Log the analysis
                        log_entry = logger.log_prompt_analysis(
                            prompt=prompt,
                            detailed_analysis=detailed_analysis,
                            should_block=should_block,
                            block_reason=block_reason,
                            model_used=llm_choice,
                            llm_response=llm_response,
                            redaction_result=redaction_result,
                            processing_time_ms=processing_time_ms
                        )

                        st.session_state.result = {
                            "detailed_analysis": detailed_analysis,
                            "should_block": should_block,
                            "block_reason": block_reason,
                            "llm_response": llm_response,
                            "model_used": llm_choice,
                            "redaction_result": redaction_result,
                            "processing_time_ms": processing_time_ms
                        }
                    except Exception as e:
                        st.session_state.error = f"An unexpected error occurred: {e}"

        # --- Display Results ---
        st.markdown("---")

        if st.session_state.error:
            st.error(st.session_state.error)

        if st.session_state.result:
            st.subheader("Analysis Complete")

            detailed_analysis = st.session_state.result["detailed_analysis"]
            should_block = st.session_state.result["should_block"]
            block_reason = st.session_state.result["block_reason"]
            llm_response = st.session_state.result["llm_response"]
            model_used = st.session_state.result["model_used"]
            redaction_result = st.session_state.result.get("redaction_result")
            processing_time_ms = st.session_state.result.get("processing_time_ms", 0)

            # Display risk level with appropriate styling
            risk_level = detailed_analysis["risk_level"]
            if risk_level == "high":
                st.warning(f"**Risk Assessment:** {risk_level.upper()}", icon="⚠️")
            elif risk_level == "medium":
                st.info(f"**Risk Assessment:** {risk_level.upper()}", icon="ℹ️")
            else:
                st.success(f"**Risk Assessment:** {risk_level.upper()}", icon="✅")
            
            # Display processing time
            st.caption(f"⏱️ Processing time: {processing_time_ms}ms")
            
            # Display redaction info if applicable
            if redaction_result and redaction_result["was_redacted"]:
                st.info(f"🔒 **Redaction Applied:** {redaction_result['total_redactions']} items redacted before sending to LLM", icon="🔒")
                
                with st.expander("📝 View Redaction Details"):
                    st.write("**Original Prompt:**")
                    st.code(redaction_result["original_prompt"])
                    st.write("**Redacted Prompt (sent to LLM):**")
                    st.code(redaction_result["redacted_prompt"])
                    
                    if redaction_result["pii_redactions"]:
                        st.write("**PII Redactions:**")
                        for pii_type, matches in redaction_result["pii_redactions"].items():
                            st.write(f"- {pii_type.title()}: {', '.join(matches[:3])}{'...' if len(matches) > 3 else ''}")
                    
                    if redaction_result["keyword_redactions"]["redacted_keywords"]:
                        st.write("**Keyword Redactions:**")
                        st.write(f"- {', '.join(redaction_result['keyword_redactions']['redacted_keywords'])}")
            
            # Display detailed analysis in expandable sections
            with st.expander("🔍 Detailed Security Analysis", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("PII Detected", detailed_analysis["total_pii_count"])
                    st.metric("High-Risk Keywords", detailed_analysis["high_risk_keywords_count"])
                
                with col2:
                    st.metric("Medium-Risk Keywords", detailed_analysis["medium_risk_keywords_count"])
                    st.metric("Model Used", model_used.upper())
                
                # Show detected PII if any
                if detailed_analysis["pii_detected"]:
                    st.subheader("🚨 Detected PII:")
                    for pii_type, matches in detailed_analysis["pii_detected"].items():
                        st.write(f"**{pii_type.title()}:** {', '.join(matches[:3])}{'...' if len(matches) > 3 else ''}")
                
                # Show detected keywords if any
                if detailed_analysis["keywords_found"]["high"] or detailed_analysis["keywords_found"]["medium"]:
                    st.subheader("🔑 Detected Keywords:")
                    if detailed_analysis["keywords_found"]["high"]:
                        st.write(f"**High Risk:** {', '.join(detailed_analysis['keywords_found']['high'])}")
                    if detailed_analysis["keywords_found"]["medium"]:
                        st.write(f"**Medium Risk:** {', '.join(detailed_analysis['keywords_found']['medium'])}")
            
            # Display LLM response
            with st.expander("🤖 LLM Response", expanded=True):
                st.markdown(llm_response) 