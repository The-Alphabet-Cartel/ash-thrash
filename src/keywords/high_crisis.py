"""
High Crisis Keywords for Ash-Thrash Testing - EXACT COPY from Ash Bot
These keywords trigger immediate staff alerts and crisis team response

Crisis Level: HIGH 🔴
Response: Ash reply + Staff DM + Crisis team ping in dedicated channel
"""

# Suicidal ideation keywords - immediate danger indicators
SUICIDAL_IDEATION = [
    'kill myself', 'end it all', 'want to die', 'suicide', 'suicidal',
    'better off dead', 'can\'t go on', 'no point living', 'end my life',
    'not worth living', 'want to disappear forever', 'ready to die',
    'take my own life', 'don\'t want to be here', 'tired of living',
    'world without me', 'everyone better without me', 'can\'t do this anymore',
    'want out', 'done with life', 'rather be dead', 'wish i was dead'
]

# Self-harm keywords - active harm or urges
SELF_HARM = [
    'cut myself', 'hurt myself', 'self harm', 'want to cut', 'need to cut',
    'deserve pain', 'cutting again', 'relapsed cutting', 'razor blade',
    'burn myself', 'hit myself', 'punish myself', 'make it bleed',
    'carve into skin', 'slice my arms', 'fresh cuts', 'deeper cuts',
    'self injury', 'harm myself', 'cut deeper', 'razor to skin'
]

# Immediate danger - active plans or means
IMMEDIATE_DANGER = [
    'have a plan', 'goodbye everyone', 'this is goodbye', 'final message',
    'pills ready', 'bridge tonight', 'gun loaded', 'rope tied',
    'last time', 'won\'t see tomorrow', 'tonight\'s the night', 'it\'s time',
    'found the pills', 'written my note', 'made my choice', 'can\'t wait anymore',
    'have the means', 'know how to do it', 'planned it out', 'setting a date'
]

# Severe hopelessness - extremely concerning despair
SEVERE_HOPELESSNESS = [
    'no way out', 'never getting better', 'pointless to try', 'beyond help',
    'too broken to fix', 'permanent damage', 'irreversibly fucked',
    'no hope left', 'given up completely', 'past saving', 'too far gone',
    'nothing can help', 'will never be okay', 'born to suffer'
]

# Additional high-risk phrases that might emerge
ADDITIONAL_HIGH_RISK = [
    'loading the gun', 'tying the noose', 'final livestream', 'last video',
    'overdose tonight', 'jumping off', 'step in front', 'carbon monoxide',
    'slitting my wrists', 'bleeding out', 'end the pain forever'
]

# Combine all high crisis categories
HIGH_CRISIS_KEYWORDS = {
    'suicidal_ideation': SUICIDAL_IDEATION,
    'self_harm': SELF_HARM,
    'immediate_danger': IMMEDIATE_DANGER + ADDITIONAL_HIGH_RISK,
    'severe_hopelessness': SEVERE_HOPELESSNESS
}

def get_high_crisis_keywords():
    """
    Returns the complete dictionary of high crisis keywords
    
    Returns:
        dict: Dictionary with category names as keys and keyword lists as values
    """
    return HIGH_CRISIS_KEYWORDS

def get_category_keywords(category):
    """
    Get keywords for a specific high crisis category
    
    Args:
        category (str): Category name ('suicidal_ideation', 'self_harm', etc.)
        
    Returns:
        list: List of keywords for the specified category
    """
    return HIGH_CRISIS_KEYWORDS.get(category, [])

def get_all_high_keywords_flat():
    """
    Get all high crisis keywords as a flat list (for regex compilation)
    
    Returns:
        list: All high crisis keywords in a single list
    """
    all_keywords = []
    for keywords in HIGH_CRISIS_KEYWORDS.values():
        all_keywords.extend(keywords)
    return all_keywords

def get_high_crisis_stats():
    """
    Get statistics about high crisis keywords
    
    Returns:
        dict: Statistics including counts by category
    """
    stats = {}
    total = 0
    
    for category, keywords in HIGH_CRISIS_KEYWORDS.items():
        count = len(keywords)
        stats[category] = count
        total += count
    
    stats['total'] = total
    return stats

def check_high_crisis_match(text):
    """
    Check if text matches any high crisis keywords
    
    Args:
        text (str): Text to check
        
    Returns:
        dict: Match results with matched keywords and categories
    """
    text_lower = text.lower()
    matches = []
    matched_categories = set()
    
    for category, keywords in HIGH_CRISIS_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches.append({
                    'keyword': keyword,
                    'category': category
                })
                matched_categories.add(category)
    
    return {
        'has_match': len(matches) > 0,
        'matches': matches,
        'matched_categories': list(matched_categories),
        'crisis_level': 'high' if matches else 'none'
    }