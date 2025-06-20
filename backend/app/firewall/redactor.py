import re
from typing import Dict, Tuple, List

class PromptRedactor:
    def __init__(self):
        # Redaction patterns - these should match the patterns in filters.py
        self.redaction_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'date_of_birth': r'\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-]\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b',
        }
        
        # Keywords that should be redacted (high-risk only)
        self.redact_keywords_list = [
            'password', 'secret', 'api_key', 'token', 'private_key', 'ssh_key',
            'database_password', 'admin_password', 'root_password', 'master_key',
            'encryption_key', 'decryption_key', 'access_token', 'refresh_token',
            'social_security', 'ssn', 'credit_card', 'cvv', 'pin', 'passport',
            'driver_license', 'bank_account', 'routing_number', 'swift_code'
        ]

    def redact_pii(self, text: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Redact PII patterns from text and return redacted version with mapping.
        """
        redacted_text = text
        redaction_mapping = {}
        
        for pattern_name, pattern in self.redaction_patterns.items():
            found_matches = re.findall(pattern, text, re.IGNORECASE)
            if found_matches:
                redaction_mapping[pattern_name] = found_matches
                # Replace all matches with [REDACTED_TYPE]
                redacted_text = re.sub(pattern, f'[REDACTED_{pattern_name.upper()}]', redacted_text, flags=re.IGNORECASE)
        
        return redacted_text, redaction_mapping

    def redact_keywords(self, text: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Redact high-risk keywords from text, but skip if already redacted.
        """
        redacted_text = text
        keyword_mapping = {'redacted_keywords': []}
        text_lower = text.lower()
        for keyword in self.redact_keywords_list:
            # Skip if already redacted
            if '[REDACTED_KEYWORD]' in redacted_text or '[REDACTED_SECRET]' in redacted_text:
                continue
            if keyword in text_lower:
                keyword_mapping['redacted_keywords'].append(keyword)
                # Replace keyword with [REDACTED_KEYWORD]
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                redacted_text = pattern.sub('[REDACTED_KEYWORD]', redacted_text)
        return redacted_text, keyword_mapping

    def redact_secret_assignments(self, text: str) -> str:
        """
        Redact values assigned to sensitive keywords (e.g., password, api_key, token, etc.).
        """
        keywords = '|'.join([re.escape(k) for k in self.redact_keywords_list])
        # Match: password is xxx, password: xxx, password=xxx, password xxx
        assignment_pattern = re.compile(rf'\b({keywords})\b\s*(=|:|is)?\s*([\S]+)', re.IGNORECASE)
        def replacer(match):
            sep = match.group(2) or ''
            return f'[REDACTED_KEYWORD] {sep} [REDACTED_SECRET]'
        return assignment_pattern.sub(replacer, text)

    def redact_prompt(self, prompt: str) -> Dict:
        """
        Redact sensitive information from a prompt.
        """
        # First redact PII
        redacted_text, pii_mapping = self.redact_pii(prompt)
        # Then redact secret assignments (keyword + value)
        redacted_text = self.redact_secret_assignments(redacted_text)
        # Then redact keywords (standalone)
        final_redacted_text, keyword_mapping = self.redact_keywords(redacted_text)
        # Count total redactions
        total_redactions = sum(len(matches) for matches in pii_mapping.values())
        total_redactions += len(keyword_mapping['redacted_keywords'])
        return {
            'original_prompt': prompt,
            'redacted_prompt': final_redacted_text,
            'pii_redactions': pii_mapping,
            'keyword_redactions': keyword_mapping,
            'total_redactions': total_redactions,
            'was_redacted': total_redactions > 0
        }

    def get_redaction_summary(self, redaction_result: Dict) -> str:
        """
        Generate a human-readable summary of what was redacted.
        """
        summary_parts = []
        
        if redaction_result['pii_redactions']:
            for pii_type, matches in redaction_result['pii_redactions'].items():
                summary_parts.append(f"{len(matches)} {pii_type}(s)")
        
        if redaction_result['keyword_redactions']['redacted_keywords']:
            keywords = redaction_result['keyword_redactions']['redacted_keywords']
            summary_parts.append(f"{len(keywords)} sensitive keyword(s): {', '.join(keywords)}")
        
        if summary_parts:
            return f"Redacted: {'; '.join(summary_parts)}"
        else:
            return "No sensitive information detected" 