import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from app.logging.logger import PromptLogger
from app.auth.admin import AdminAuth

class AdminDashboard:
    def __init__(self):
        """Initialize admin dashboard."""
        self.logger = PromptLogger()
        self.auth = AdminAuth()
    
    def render_dashboard(self):
        """Render the main admin dashboard."""
        st.title("🔐 Admin Dashboard")
        st.markdown("---")
        
        # Get system statistics
        stats = self.logger.get_statistics()
        
        # System Overview
        st.subheader("📊 System Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Prompts", stats['total_prompts'])
        with col2:
            st.metric("High Risk", stats['risk_levels'].get('high', 0))
        with col3:
            st.metric("Blocked", stats['blocked_prompts'])
        with col4:
            st.metric("Redacted", stats['redacted_prompts'])
        
        # Risk Level Distribution
        st.subheader("🎯 Risk Level Distribution")
        if stats['risk_levels']:
            risk_data = pd.DataFrame([
                {"Risk Level": k.title(), "Count": v} 
                for k, v in stats['risk_levels'].items()
            ])
            st.bar_chart(risk_data.set_index("Risk Level"))
        
        # Model Usage
        st.subheader("🤖 Model Usage")
        if stats['models_used']:
            model_data = pd.DataFrame([
                {"Model": k.upper(), "Usage": v} 
                for k, v in stats['models_used'].items()
            ])
            st.bar_chart(model_data.set_index("Model"))
        
        # Recent Activity
        st.subheader("📋 Recent Activity")
        recent_logs = self.logger.get_recent_logs(10)
        
        if recent_logs:
            activity_data = []
            for log in recent_logs[-10:]:  # Last 10 entries
                activity_data.append({
                    "Time": log.get('timestamp', '')[:19],
                    "Risk": log.get('risk_level', 'unknown').upper(),
                    "Model": log.get('model_used', 'N/A').upper(),
                    "Blocked": "Yes" if log.get('should_block') else "No",
                    "Redacted": "Yes" if log.get('was_redacted') else "No"
                })
            
            df = pd.DataFrame(activity_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent activity found.")
    
    def render_user_management(self):
        """Render user management section."""
        st.subheader("👥 User Management")
        
        # Get current admin users
        admin_users = self.auth.get_admin_users()
        
        # Display current users
        st.write("**Current Admin Users:**")
        if admin_users:
            user_data = []
            for user in admin_users:
                user_data.append({
                    "Username": user['username'],
                    "Role": user['role'].replace('_', ' ').title(),
                    "Created": user['created_at'][:10],
                    "Last Login": user['last_login'][:19] if user['last_login'] else "Never",
                    "Status": "🔒 Locked" if user['locked_until'] else "✅ Active"
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No admin users found.")
        
        # Create new admin user
        with st.expander("➕ Create New Admin User"):
            with st.form("create_admin"):
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_role = st.selectbox("Role", ["admin", "super_admin"])
                
                if st.form_submit_button("Create User"):
                    if new_username and new_password:
                        result = self.auth.create_admin_user(new_username, new_password, new_role)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                    else:
                        st.error("Please fill in all fields.")
        
        # Delete admin user
        with st.expander("🗑️ Delete Admin User"):
            if admin_users:
                usernames = [user['username'] for user in admin_users if user['username'] != 'admin']
                if usernames:
                    delete_username = st.selectbox("Select user to delete", usernames)
                    if st.button("Delete User"):
                        result = self.auth.delete_admin_user(delete_username)
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
                else:
                    st.info("No users available for deletion.")
            else:
                st.info("No admin users found.")
    
    def render_security_monitoring(self):
        """Render security monitoring section."""
        st.subheader("🔒 Security Monitoring")
        
        # Get recent high-risk prompts
        high_risk_logs = self.logger.get_logs_by_risk_level('high')
        
        st.write(f"**High-Risk Prompts (Last {len(high_risk_logs)}):**")
        if high_risk_logs:
            security_data = []
            for log in high_risk_logs[-20:]:  # Last 20 high-risk entries
                security_data.append({
                    "Time": log.get('timestamp', '')[:19],
                    "Prompt": log.get('prompt', '')[:50] + "..." if len(log.get('prompt', '')) > 50 else log.get('prompt', ''),
                    "PII Detected": ", ".join(log.get('pii_detected', [])),
                    "High-Risk Keywords": ", ".join(log.get('high_risk_keywords', [])),
                    "Action": "Blocked" if log.get('should_block') else "Redacted"
                })
            
            df = pd.DataFrame(security_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No high-risk prompts found.")
        
        # Security statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Security Metrics:**")
            stats = self.logger.get_statistics()
            
            # Calculate security ratios
            total = stats['total_prompts']
            if total > 0:
                blocked_ratio = (stats['blocked_prompts'] / total) * 100
                redacted_ratio = (stats['redacted_prompts'] / total) * 100
                high_risk_ratio = (stats['risk_levels'].get('high', 0) / total) * 100
                
                st.metric("Block Rate", f"{blocked_ratio:.1f}%")
                st.metric("Redaction Rate", f"{redacted_ratio:.1f}%")
                st.metric("High-Risk Rate", f"{high_risk_ratio:.1f}%")
        
        with col2:
            st.write("**System Health:**")
            # Mock system health metrics
            st.metric("System Uptime", "99.9%")
            st.metric("Avg Response Time", "1.2s")
            st.metric("Active Sessions", "5")
    
    def render_audit_logs(self):
        """Render audit logs section."""
        st.subheader("📝 Audit Logs")
        
        # Get all logs for audit
        all_logs = self.logger.get_recent_logs(100)
        
        if all_logs:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                audit_risk_filter = st.selectbox(
                    "Filter by Risk",
                    ["All", "low", "medium", "high"],
                    key="audit_risk"
                )
            
            with col2:
                audit_model_filter = st.selectbox(
                    "Filter by Model",
                    ["All", "groq", "gemini"],
                    key="audit_model"
                )
            
            with col3:
                audit_action_filter = st.selectbox(
                    "Filter by Action",
                    ["All", "blocked", "redacted", "processed"],
                    key="audit_action"
                )
            
            # Apply filters
            filtered_logs = all_logs
            
            if audit_risk_filter != "All":
                filtered_logs = [log for log in filtered_logs if log.get('risk_level') == audit_risk_filter]
            
            if audit_model_filter != "All":
                filtered_logs = [log for log in filtered_logs if log.get('model_used') == audit_model_filter]
            
            if audit_action_filter != "All":
                if audit_action_filter == "blocked":
                    filtered_logs = [log for log in filtered_logs if log.get('should_block')]
                elif audit_action_filter == "redacted":
                    filtered_logs = [log for log in filtered_logs if log.get('was_redacted')]
                elif audit_action_filter == "processed":
                    filtered_logs = [log for log in filtered_logs if not log.get('should_block') and not log.get('was_redacted')]
            
            # Display filtered logs
            st.write(f"**Audit Logs ({len(filtered_logs)} entries):**")
            
            if filtered_logs:
                audit_data = []
                for log in filtered_logs:
                    action = "Blocked" if log.get('should_block') else ("Redacted" if log.get('was_redacted') else "Processed")
                    audit_data.append({
                        "Timestamp": log.get('timestamp', '')[:19],
                        "Risk": log.get('risk_level', 'unknown').upper(),
                        "Model": log.get('model_used', 'N/A').upper(),
                        "Action": action,
                        "Processing Time": f"{log.get('processing_time_ms', 0)}ms",
                        "Prompt Length": len(log.get('prompt', ''))
                    })
                
                df = pd.DataFrame(audit_data)
                st.dataframe(df, use_container_width=True)
                
                # Export option
                if st.button("📥 Export Audit Logs (CSV)"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No logs match the selected filters.")
        else:
            st.info("No audit logs found.")
    
    def render_system_settings(self):
        """Render system settings section."""
        st.subheader("⚙️ System Settings")
        
        # Current configuration
        st.write("**Current Configuration:**")
        
        # Mock system settings (in a real app, these would be configurable)
        settings = {
            "Session Timeout": "2 hours",
            "Max Login Attempts": "3",
            "Lockout Duration": "15 minutes",
            "Log Retention": "30 days",
            "Auto Backup": "Enabled",
            "Security Level": "High"
        }
        
        for key, value in settings.items():
            st.write(f"**{key}:** {value}")
        
        # Configuration options
        with st.expander("🔧 Modify Settings"):
            st.info("Settings modification feature coming soon!")
            st.write("In a production environment, these settings would be configurable through the admin interface.")
    
    def render_help_documentation(self):
        """Render help and documentation section."""
        st.subheader("❓ Help & Documentation")
        
        st.write("**Admin Dashboard Guide:**")
        
        with st.expander("📊 Dashboard Overview"):
            st.write("""
            The admin dashboard provides comprehensive monitoring and management capabilities:
            
            **System Overview:**
            - Total prompts analyzed
            - Risk level distribution
            - Model usage statistics
            - Recent activity feed
            
            **User Management:**
            - Create new admin users
            - Delete existing users
            - Monitor user activity
            - Manage user roles
            
            **Security Monitoring:**
            - High-risk prompt tracking
            - Security metrics and ratios
            - System health monitoring
            - Threat detection alerts
            
            **Audit Logs:**
            - Complete activity history
            - Filtered log views
            - Export capabilities
            - Compliance reporting
            """)
        
        with st.expander("🔐 Security Features"):
            st.write("""
            **Authentication & Authorization:**
            - Role-based access control
            - Session management
            - Account lockout protection
            - Password security
            
            **Data Protection:**
            - PII detection and redaction
            - Secure logging practices
            - Audit trail maintenance
            - Compliance monitoring
            """)
        
        with st.expander("📈 Metrics & Analytics"):
            st.write("""
            **Key Performance Indicators:**
            - Prompt processing volume
            - Risk assessment accuracy
            - System response times
            - User activity patterns
            
            **Security Metrics:**
            - Block rate percentage
            - Redaction rate percentage
            - High-risk detection rate
            - False positive analysis
            """) 