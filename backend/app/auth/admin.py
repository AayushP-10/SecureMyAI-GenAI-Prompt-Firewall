import hashlib
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

class AdminAuth:
    def __init__(self, admin_file: str = "admin_config.json"):
        """
        Initialize admin authentication system.
        
        Args:
            admin_file (str): Path to admin configuration file
        """
        self.admin_file = Path(admin_file)
        self.session_timeout = timedelta(hours=2)  # 2 hour session timeout
        self.max_login_attempts = 3
        self.lockout_duration = timedelta(minutes=15)  # 15 minute lockout
        
        # Initialize admin config if it doesn't exist
        self._init_admin_config()
    
    def _init_admin_config(self):
        """Initialize admin configuration with default admin user."""
        if not self.admin_file.exists():
            default_config = {
                "admin_users": {
                    "admin": {
                        "password_hash": self._hash_password("admin123"),
                        "role": "super_admin",
                        "created_at": datetime.now().isoformat(),
                        "last_login": None,
                        "login_attempts": 0,
                        "locked_until": None
                    }
                },
                "system_config": {
                    "session_timeout_hours": 2,
                    "max_login_attempts": 3,
                    "lockout_duration_minutes": 15,
                    "enable_audit_log": True
                }
            }
            
            with open(self.admin_file, 'w') as f:
                json.dump(default_config, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_config(self) -> Dict:
        """Load admin configuration."""
        with open(self.admin_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict):
        """Save admin configuration."""
        with open(self.admin_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def authenticate(self, username: str, password: str) -> Dict:
        """
        Authenticate admin user.
        
        Args:
            username (str): Admin username
            password (str): Admin password
            
        Returns:
            Dict: Authentication result with status and user info
        """
        try:
            config = self._load_config()
            admin_users = config.get("admin_users", {})
            
            if username not in admin_users:
                return {
                    "success": False,
                    "message": "Invalid username or password",
                    "user": None
                }
            
            user = admin_users[username]
            
            # Check if account is locked
            if user.get("locked_until"):
                locked_until = datetime.fromisoformat(user["locked_until"])
                if datetime.now() < locked_until:
                    remaining = locked_until - datetime.now()
                    return {
                        "success": False,
                        "message": f"Account locked. Try again in {int(remaining.total_seconds() / 60)} minutes",
                        "user": None
                    }
                else:
                    # Unlock account
                    user["locked_until"] = None
                    user["login_attempts"] = 0
            
            # Verify password
            if user["password_hash"] == self._hash_password(password):
                # Successful login
                user["last_login"] = datetime.now().isoformat()
                user["login_attempts"] = 0
                user["locked_until"] = None
                
                # Save updated config
                self._save_config(config)
                
                return {
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "username": username,
                        "role": user["role"],
                        "last_login": user["last_login"]
                    }
                }
            else:
                # Failed login
                user["login_attempts"] = user.get("login_attempts", 0) + 1
                
                # Check if account should be locked
                if user["login_attempts"] >= config["system_config"]["max_login_attempts"]:
                    lockout_duration = timedelta(minutes=config["system_config"]["lockout_duration_minutes"])
                    user["locked_until"] = (datetime.now() + lockout_duration).isoformat()
                
                self._save_config(config)
                
                return {
                    "success": False,
                    "message": "Invalid username or password",
                    "user": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}",
                "user": None
            }
    
    def create_admin_user(self, username: str, password: str, role: str = "admin") -> Dict:
        """
        Create a new admin user.
        
        Args:
            username (str): New admin username
            password (str): New admin password
            role (str): Admin role (admin, super_admin)
            
        Returns:
            Dict: Creation result
        """
        try:
            config = self._load_config()
            admin_users = config.get("admin_users", {})
            
            if username in admin_users:
                return {
                    "success": False,
                    "message": "Username already exists"
                }
            
            # Create new admin user
            admin_users[username] = {
                "password_hash": self._hash_password(password),
                "role": role,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "login_attempts": 0,
                "locked_until": None
            }
            
            config["admin_users"] = admin_users
            self._save_config(config)
            
            return {
                "success": True,
                "message": f"Admin user '{username}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating admin user: {str(e)}"
            }
    
    def delete_admin_user(self, username: str) -> Dict:
        """
        Delete an admin user.
        
        Args:
            username (str): Username to delete
            
        Returns:
            Dict: Deletion result
        """
        try:
            config = self._load_config()
            admin_users = config.get("admin_users", {})
            
            if username not in admin_users:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            if username == "admin":
                return {
                    "success": False,
                    "message": "Cannot delete the default admin user"
                }
            
            del admin_users[username]
            config["admin_users"] = admin_users
            self._save_config(config)
            
            return {
                "success": True,
                "message": f"Admin user '{username}' deleted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting admin user: {str(e)}"
            }
    
    def get_admin_users(self) -> List[Dict]:
        """
        Get list of all admin users (without password hashes).
        
        Returns:
            List[Dict]: List of admin users
        """
        try:
            config = self._load_config()
            admin_users = config.get("admin_users", {})
            
            users = []
            for username, user_data in admin_users.items():
                users.append({
                    "username": username,
                    "role": user_data["role"],
                    "created_at": user_data["created_at"],
                    "last_login": user_data.get("last_login"),
                    "login_attempts": user_data.get("login_attempts", 0),
                    "locked_until": user_data.get("locked_until")
                })
            
            return users
            
        except Exception as e:
            return []
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Dict:
        """
        Change admin user password.
        
        Args:
            username (str): Admin username
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            Dict: Password change result
        """
        try:
            config = self._load_config()
            admin_users = config.get("admin_users", {})
            
            if username not in admin_users:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            user = admin_users[username]
            
            # Verify old password
            if user["password_hash"] != self._hash_password(old_password):
                return {
                    "success": False,
                    "message": "Current password is incorrect"
                }
            
            # Update password
            user["password_hash"] = self._hash_password(new_password)
            config["admin_users"] = admin_users
            self._save_config(config)
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error changing password: {str(e)}"
            }
    
    def is_valid_session(self, session_data: Dict) -> bool:
        """
        Check if admin session is still valid.
        
        Args:
            session_data (Dict): Session data from Streamlit
            
        Returns:
            bool: True if session is valid
        """
        if not session_data.get("admin_logged_in"):
            return False
        
        last_activity = session_data.get("admin_last_activity")
        if not last_activity:
            return False
        
        try:
            last_activity_time = datetime.fromisoformat(last_activity)
            if datetime.now() - last_activity_time > self.session_timeout:
                return False
            return True
        except:
            return False 