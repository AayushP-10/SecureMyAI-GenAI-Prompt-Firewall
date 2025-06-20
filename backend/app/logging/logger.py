import json
import csv
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class PromptLogger:
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the prompt logger.
        
        Args:
            log_dir (str): Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Define log file paths
        self.csv_file = self.log_dir / "prompt_log.csv"
        self.json_file = self.log_dir / "prompt_log.json"
        
        # Initialize CSV file with headers if it doesn't exist
        self._init_csv_file()
    
    def _init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_file.exists():
            headers = [
                'timestamp',
                'prompt',
                'risk_level',
                'should_block',
                'block_reason',
                'model_used',
                'was_redacted',
                'redacted_prompt',
                'pii_detected',
                'high_risk_keywords',
                'medium_risk_keywords',
                'total_pii_count',
                'high_risk_keywords_count',
                'medium_risk_keywords_count',
                'llm_response_length',
                'processing_time_ms'
            ]
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def log_prompt_analysis(self, 
                          prompt: str,
                          detailed_analysis: Dict[str, Any],
                          should_block: bool,
                          block_reason: str,
                          model_used: str,
                          llm_response: str,
                          redaction_result: Dict[str, Any] = None,
                          processing_time_ms: int = None) -> Dict[str, Any]:
        """
        Log a complete prompt analysis to both CSV and JSON formats.
        
        Args:
            prompt (str): Original prompt
            detailed_analysis (Dict): Analysis results from classifier
            should_block (bool): Whether prompt was blocked
            block_reason (str): Reason for blocking
            model_used (str): LLM model used
            llm_response (str): Response from LLM
            redaction_result (Dict): Redaction results if applicable
            processing_time_ms (int): Processing time in milliseconds
            
        Returns:
            Dict: Log entry that was saved
        """
        timestamp = datetime.now().isoformat()
        
        # Prepare log entry
        log_entry = {
            'timestamp': timestamp,
            'prompt': prompt,
            'risk_level': detailed_analysis.get('risk_level', 'unknown'),
            'should_block': should_block,
            'block_reason': block_reason,
            'model_used': model_used,
            'was_redacted': redaction_result.get('was_redacted', False) if redaction_result else False,
            'redacted_prompt': redaction_result.get('redacted_prompt', '') if redaction_result else '',
            'pii_detected': list(detailed_analysis.get('pii_detected', {}).keys()),
            'high_risk_keywords': detailed_analysis.get('keywords_found', {}).get('high', []),
            'medium_risk_keywords': detailed_analysis.get('keywords_found', {}).get('medium', []),
            'total_pii_count': detailed_analysis.get('total_pii_count', 0),
            'high_risk_keywords_count': detailed_analysis.get('high_risk_keywords_count', 0),
            'medium_risk_keywords_count': detailed_analysis.get('medium_risk_keywords_count', 0),
            'llm_response_length': len(llm_response) if llm_response else 0,
            'processing_time_ms': processing_time_ms or 0,
            'detailed_analysis': detailed_analysis,
            'redaction_details': redaction_result,
            'llm_response': llm_response
        }
        
        # Log to CSV
        self._log_to_csv(log_entry)
        
        # Log to JSON
        self._log_to_json(log_entry)
        
        return log_entry
    
    def _log_to_csv(self, log_entry: Dict[str, Any]):
        """Log entry to CSV file."""
        try:
            row = [
                log_entry['timestamp'],
                log_entry['prompt'],
                log_entry['risk_level'],
                log_entry['should_block'],
                log_entry['block_reason'],
                log_entry['model_used'],
                log_entry['was_redacted'],
                log_entry['redacted_prompt'],
                '; '.join(log_entry['pii_detected']),
                '; '.join(log_entry['high_risk_keywords']),
                '; '.join(log_entry['medium_risk_keywords']),
                log_entry['total_pii_count'],
                log_entry['high_risk_keywords_count'],
                log_entry['medium_risk_keywords_count'],
                log_entry['llm_response_length'],
                log_entry['processing_time_ms']
            ]
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
            print(f"Error logging to CSV: {e}")
    
    def _log_to_json(self, log_entry: Dict[str, Any]):
        """Log entry to JSON file."""
        try:
            # Read existing logs
            logs = []
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            # Add new log entry
            logs.append(log_entry)
            
            # Write back to file
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error logging to JSON: {e}")
    
    def get_recent_logs(self, limit: int = 10) -> list:
        """
        Get recent log entries.
        
        Args:
            limit (int): Number of recent entries to return
            
        Returns:
            list: Recent log entries
        """
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    return logs[-limit:] if len(logs) > limit else logs
            return []
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
    
    def get_logs_by_risk_level(self, risk_level: str) -> list:
        """
        Get logs filtered by risk level.
        
        Args:
            risk_level (str): Risk level to filter by ('low', 'medium', 'high')
            
        Returns:
            list: Filtered log entries
        """
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    return [log for log in logs if log.get('risk_level') == risk_level]
            return []
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
    
    def get_logs_by_model(self, model: str) -> list:
        """
        Get logs filtered by model used.
        
        Args:
            model (str): Model to filter by ('groq', 'gemini')
            
        Returns:
            list: Filtered log entries
        """
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    return [log for log in logs if log.get('model_used') == model]
            return []
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged prompts.
        
        Returns:
            Dict: Statistics about the logs
        """
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                if not logs:
                    return {
                        'total_prompts': 0,
                        'risk_levels': {},
                        'models_used': {},
                        'blocked_prompts': 0,
                        'redacted_prompts': 0
                    }
                
                # Calculate statistics
                total_prompts = len(logs)
                risk_levels = {}
                models_used = {}
                blocked_prompts = 0
                redacted_prompts = 0
                
                for log in logs:
                    # Risk levels
                    risk = log.get('risk_level', 'unknown')
                    risk_levels[risk] = risk_levels.get(risk, 0) + 1
                    
                    # Models used
                    model = log.get('model_used', 'unknown')
                    models_used[model] = models_used.get(model, 0) + 1
                    
                    # Blocked prompts
                    if log.get('should_block', False):
                        blocked_prompts += 1
                    
                    # Redacted prompts
                    if log.get('was_redacted', False):
                        redacted_prompts += 1
                
                return {
                    'total_prompts': total_prompts,
                    'risk_levels': risk_levels,
                    'models_used': models_used,
                    'blocked_prompts': blocked_prompts,
                    'redacted_prompts': redacted_prompts
                }
            return {
                'total_prompts': 0,
                'risk_levels': {},
                'models_used': {},
                'blocked_prompts': 0,
                'redacted_prompts': 0
            }
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                'total_prompts': 0,
                'risk_levels': {},
                'models_used': {},
                'blocked_prompts': 0,
                'redacted_prompts': 0
            } 