from .filters import PromptFilter

def classify_risk(prompt: str) -> str:
    """
    Classify the risk level of a prompt using comprehensive filtering.
    
    Args:
        prompt (str): The prompt to analyze
        
    Returns:
        str: Risk level ('low', 'medium', 'high')
    """
    filter_instance = PromptFilter()
    analysis = filter_instance.analyze_prompt(prompt)
    return analysis['risk_level']

def should_block_prompt(prompt: str) -> tuple[bool, str]:
    """
    Determine if a prompt should be blocked and provide the reason.
    
    Args:
        prompt (str): The prompt to check
        
    Returns:
        tuple[bool, str]: (should_block, reason)
    """
    filter_instance = PromptFilter()
    return filter_instance.should_block_prompt(prompt)

def get_detailed_analysis(prompt: str) -> dict:
    """
    Get detailed analysis of a prompt including PII detection and keyword analysis.
    
    Args:
        prompt (str): The prompt to analyze
        
    Returns:
        dict: Complete analysis results
    """
    filter_instance = PromptFilter()
    return filter_instance.analyze_prompt(prompt) 