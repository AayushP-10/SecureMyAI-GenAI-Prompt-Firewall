#!/usr/bin/env python3
"""
Script to generate sample data for testing SecureMyAI features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.logging.logger import PromptLogger
from app.firewall.classifier import get_detailed_analysis
from app.firewall.redactor import PromptRedactor
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample prompt data for testing."""
    print("🔄 Generating sample data for SecureMyAI...")
    
    logger = PromptLogger()
    redactor = PromptRedactor()
    
    # Sample prompts with different risk levels
    sample_prompts = [
        # Low risk prompts
        {
            "prompt": "How can I improve my Python coding skills?",
            "model": "groq",
            "risk_level": "low"
        },
        {
            "prompt": "What are the best practices for web development?",
            "model": "gemini",
            "risk_level": "low"
        },
        {
            "prompt": "Explain machine learning algorithms for beginners",
            "model": "groq",
            "risk_level": "low"
        },
        
        # Medium risk prompts
        {
            "prompt": "My password is hunter2, how can I make it more secure?",
            "model": "gemini",
            "risk_level": "medium"
        },
        {
            "prompt": "I have an API key: sk-1234567890abcdef, how should I store it?",
            "model": "groq",
            "risk_level": "medium"
        },
        {
            "prompt": "My email is john.doe@company.com, how can I protect it?",
            "model": "gemini",
            "risk_level": "medium"
        },
        
        # High risk prompts
        {
            "prompt": "My credit card number is 4111-1111-1111-1111, what should I do if it's stolen?",
            "model": "groq",
            "risk_level": "high"
        },
        {
            "prompt": "My SSN is 123-45-6789, how can I protect my identity?",
            "model": "gemini",
            "risk_level": "high"
        },
        {
            "prompt": "My phone number is 555-123-4567 and my address is 123 Main St, how can I keep this private?",
            "model": "groq",
            "risk_level": "high"
        }
    ]
    
    # Generate data over the past few days
    base_time = datetime.now() - timedelta(days=3)
    
    for i, sample in enumerate(sample_prompts):
        # Create timestamp with some variation
        timestamp = base_time + timedelta(
            hours=i*2,
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        prompt = sample["prompt"]
        model = sample["model"]
        expected_risk = sample["risk_level"]
        
        # Get detailed analysis
        detailed_analysis = get_detailed_analysis(prompt)
        
        # Determine if should block
        should_block = expected_risk == "high"
        block_reason = "High-risk content detected" if should_block else None
        
        # Handle redaction for medium risk
        redaction_result = None
        llm_response = None
        
        if should_block:
            llm_response = f"🚫 **PROMPT BLOCKED**\n\n**Reason:** {block_reason}\n\nThis prompt contains sensitive information and has been blocked for security reasons."
        else:
            if expected_risk == "medium":
                redaction_result = redactor.redact_prompt(prompt)
                prompt_to_send = redaction_result["redacted_prompt"]
            else:
                prompt_to_send = prompt
            
            # Mock LLM response
            llm_response = f"This is a sample response for: {prompt_to_send[:50]}..."
        
        # Log the analysis
        log_entry = logger.log_prompt_analysis(
            prompt=prompt,
            detailed_analysis=detailed_analysis,
            should_block=should_block,
            block_reason=block_reason,
            model_used=model,
            llm_response=llm_response,
            redaction_result=redaction_result,
            processing_time_ms=random.randint(100, 500)
        )
        
        print(f"✅ Generated sample {i+1}/{len(sample_prompts)}: {expected_risk.upper()} risk")
    
    # Generate some additional random data
    additional_prompts = [
        "How do I implement authentication in my app?",
        "What's the best way to handle user passwords?",
        "My secret token is abc123def456, is this secure?",
        "How can I protect my database credentials?",
        "What are the security best practices for APIs?",
        "My private key is -----BEGIN PRIVATE KEY-----, how should I store it?",
        "How do I implement rate limiting?",
        "What's the difference between JWT and session tokens?",
        "My access token is xyz789, how long should it be valid?",
        "How can I secure my web application?"
    ]
    
    for i, prompt in enumerate(additional_prompts):
        timestamp = base_time + timedelta(
            days=random.randint(0, 3),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        detailed_analysis = get_detailed_analysis(prompt)
        model = random.choice(["groq", "gemini"])
        
        # Random risk level
        risk_levels = ["low", "medium", "high"]
        expected_risk = random.choice(risk_levels)
        
        should_block = expected_risk == "high"
        block_reason = "High-risk content detected" if should_block else None
        
        redaction_result = None
        llm_response = None
        
        if should_block:
            llm_response = f"🚫 **PROMPT BLOCKED**\n\n**Reason:** {block_reason}"
        else:
            if expected_risk == "medium":
                redaction_result = redactor.redact_prompt(prompt)
                prompt_to_send = redaction_result["redacted_prompt"]
            else:
                prompt_to_send = prompt
            
            llm_response = f"Sample response for prompt analysis..."
        
        log_entry = logger.log_prompt_analysis(
            prompt=prompt,
            detailed_analysis=detailed_analysis,
            should_block=should_block,
            block_reason=block_reason,
            model_used=model,
            llm_response=llm_response,
            redaction_result=redaction_result,
            processing_time_ms=random.randint(80, 800)
        )
    
    print(f"✅ Generated {len(additional_prompts)} additional random samples")
    
    # Show statistics
    stats = logger.get_statistics()
    print("\n📊 Generated Data Statistics:")
    print(f"   Total Prompts: {stats['total_prompts']}")
    print(f"   Risk Levels: {stats['risk_levels']}")
    print(f"   Models Used: {stats['models_used']}")
    print(f"   Blocked: {stats['blocked_prompts']}")
    print(f"   Redacted: {stats['redacted_prompts']}")
    
    print("\n🎉 Sample data generation complete!")
    print("💡 Now you can test the admin dashboard and prompt history features.")

if __name__ == "__main__":
    generate_sample_data() 