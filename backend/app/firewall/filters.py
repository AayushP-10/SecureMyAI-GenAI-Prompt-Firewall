import re
from typing import Dict, List, Tuple

class PromptFilter:
    def __init__(self):
        # Regex patterns for different types of PII
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'date_of_birth': r'\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-]\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
        }
        
        # High-risk keywords that should trigger blocking
        self.high_risk_keywords = [
            'password', 'secret', 'api_key', 'token', 'private_key', 'ssh_key',
            'database_password', 'admin_password', 'root_password', 'master_key',
            'encryption_key', 'decryption_key', 'access_token', 'refresh_token',
            'social_security', 'ssn', 'credit_card', 'cvv', 'pin', 'passport',
            'driver_license', 'bank_account', 'routing_number', 'swift_code'
        ]
        
        # Medium-risk keywords
        self.medium_risk_keywords = [
            'personal', 'private', 'confidential', 'sensitive', 'internal',
            'proprietary', 'classified', 'restricted', 'secure', 'protected'
        ]

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII patterns in the given text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary with pattern type as key and list of matches as value
        """
        detected = {}
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[pattern_name] = matches
        
        return detected

    def check_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Check for high and medium risk keywords in the text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary with risk level as key and list of keywords as value
        """
        text_lower = text.lower()
        found_keywords = {'high': [], 'medium': []}
        
        for keyword in self.high_risk_keywords:
            if keyword in text_lower:
                found_keywords['high'].append(keyword)
        
        for keyword in self.medium_risk_keywords:
            if keyword in text_lower:
                found_keywords['medium'].append(keyword)
        
        return found_keywords

    def analyze_prompt(self, prompt: str) -> Dict:
        """
        Complete analysis of a prompt for security risks.
        
        Args:
            prompt (str): The prompt to analyze
            
        Returns:
            Dict: Analysis results including risk level, detected PII, and keywords
        """
        pii_detected = self.detect_pii(prompt)
        keywords_found = self.check_keywords(prompt)
        
        # Determine overall risk level
        risk_level = 'low'
        
        # High risk for specific PII types
        if any(pii in pii_detected for pii in ['ssn', 'credit_card']):
            risk_level = 'high'
        # Medium risk for other PII or any high-risk keywords (which can be redacted)
        elif pii_detected or keywords_found['high'] or keywords_found['medium']:
            risk_level = 'medium'
        
        return {
            'risk_level': risk_level,
            'pii_detected': pii_detected,
            'keywords_found': keywords_found,
            'should_block': risk_level == 'high',
            'total_pii_count': sum(len(matches) for matches in pii_detected.values()),
            'high_risk_keywords_count': len(keywords_found['high']),
            'medium_risk_keywords_count': len(keywords_found['medium'])
        }

    def should_block_prompt(self, prompt: str) -> Tuple[bool, str]:
        """
        Determine if a prompt should be blocked and provide reason.
        
        Args:
            prompt (str): The prompt to check
            
        Returns:
            Tuple[bool, str]: (should_block, reason)
        """
        analysis = self.analyze_prompt(prompt)
        
        if analysis['should_block']:
            reasons = []
            
            if analysis['pii_detected']:
                pii_types = list(analysis['pii_detected'].keys())
                reasons.append(f"Detected PII: {', '.join(pii_types)}")
            
            if analysis['keywords_found']['high']:
                reasons.append(f"High-risk keywords: {', '.join(analysis['keywords_found']['high'])}")
            
            return True, '; '.join(reasons)
        
        return False, "No high-risk content detected" 