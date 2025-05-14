"""
Utility functions for extracting information from model responses.
"""
import re

def extract_guideline_updates(response: str, current_draft: str) -> str:
    """
    Extract updates to the guideline from the model's response.
    Looks for content between "GUIDELINE UPDATE:" and "END GUIDELINE UPDATE" markers.
    
    Args:
        response: The model's response text
        current_draft: The current guideline draft
        
    Returns:
        The updated guideline draft
    """
    # If there's no current draft, start with an empty one
    if not current_draft:
        current_draft = ""
    
    # Look for guideline updates in the response
    pattern = r"GUIDELINE UPDATE:(.*?)END GUIDELINE UPDATE"
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        # Extract the latest update
        latest_update = matches[-1].strip()
        
        # If we already have a draft, append the new content
        if current_draft:
            return current_draft + "\n\n" + latest_update
        else:
            return latest_update
    
    # If we can't find an explicit update but don't have a draft yet,
    # try to extract something useful from the response
    if not current_draft:
        # Look for any structured content that might be guideline-like
        sections = re.split(r'\n\s*\n', response)
        
        # Filter out very short sections and join the rest
        potential_guideline = "\n\n".join([s for s in sections if len(s.strip()) > 50])
        
        if potential_guideline:
            return potential_guideline
    
    # If no updates found or we already have a draft, return the current draft
    return current_draft 