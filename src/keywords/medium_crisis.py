"""
Medium Crisis Keywords for Ash-Thrash Testing - EXACT COPY from Ash Bot
These keywords trigger crisis team alerts but not staff DMs

Crisis Level: MEDIUM 🟡
Response: Ash reply + Crisis team ping (no direct staff DM)
"""

# Severe emotional distress - significant mental health episodes
SEVERE_EMOTIONAL_DISTRESS = [
    'having a breakdown', 'mental breakdown', 'falling apart', 'losing my mind',
    'can\'t stop crying', 'sobbing uncontrollably', 'emotional wreck',
    'completely lost', 'don\'t know what to do', 'everything is falling apart',
    'world is crashing down', 'life is a mess', 'spiraling out of control',
    'hitting rock bottom', 'at my breaking point', 'can\'t handle this'
]

# Severe depression episodes - clinical level symptoms
SEVERE_DEPRESSION = [
    'severely depressed', 'deep depression', 'clinical depression',
    'major depressive episode', 'depression is back', 'depressive spiral',
    'can\'t get out of bed', 'lost all motivation', 'nothing brings joy',
    'feel empty inside', 'hollow feeling', 'emotionally numb',
    'life has no meaning', 'everything is pointless', 'why bother',
    'what\'s the point', 'nothing matters anymore', 'life is meaningless'
]

# Panic and anxiety attacks - acute episodes
PANIC_ANXIETY_ATTACKS = [
    'panic attack', 'anxiety attack', 'having a panic attack',
    'can\'t breathe', 'heart racing', 'chest tight', 'hyperventilating',
    'feel like dying', 'think I\'m dying', 'can\'t catch my breath',
    'dizzy and nauseous', 'shaking uncontrollably', 'sweating profusely',
    'agoraphobic episode', 'trapped feeling', 'can\'t leave house'
]

# Trauma responses - PTSD and trauma reactions
TRAUMA_RESPONSES = [
    'ptsd episode', 'trauma response', 'triggered badly', 'flashback',
    'reliving trauma', 'nightmare episode', 'dissociating',
    'out of body experience', 'not feeling real', 'memory flooding back',
    'trauma anniversary', 'abuse memories', 'assault memories',
    'can\'t escape the memories', 'intrusive thoughts', 'trigger warning'
]

# Identity crisis - severe questioning and distress
IDENTITY_CRISIS = [
    'identity crisis', 'don\'t know who I am', 'questioning everything',
    'lost my sense of self', 'feel like a stranger', 'imposter syndrome',
    'gender crisis', 'sexuality crisis', 'faith crisis',
    'major life crisis', 'existential crisis', 'quarter life crisis',
    'midlife crisis', 'who am I really', 'lost my identity'
]

# Relationship trauma - severe interpersonal distress
RELATIONSHIP_TRAUMA = [
    'toxic relationship', 'emotional abuse', 'manipulative partner',
    'gaslighting', 'being controlled', 'walking on eggshells',
    'fear my partner', 'relationship violence', 'domestic abuse',
    'sexual assault', 'rape survivor', 'abuse survivor',
    'childhood trauma', 'family abuse', 'parental abuse'
]

# Severe life stressors - major life disruptions
SEVERE_LIFE_STRESS = [
    'life falling apart', 'everything going wrong', 'crisis after crisis',
    'can\'t catch a break', 'one thing after another', 'overwhelmed completely',
    'major financial crisis', 'about to be homeless', 'lost my job',
    'getting divorced', 'custody battle', 'legal troubles',
    'serious health diagnosis', 'chronic illness', 'disability struggles'
]

# Suicidal ideation (medium level) - concerning but not immediate
CONCERNING_IDEATION = [
    'sometimes think about dying', 'wonder if it would be easier',
    'think about not existing', 'passive suicidal thoughts',
    'wouldn\'t mind not waking up', 'tired of fighting',
    'don\'t see the point anymore', 'would anyone even notice',
    'maybe everyone would be better off', 'feel like a burden'
]

# Combine all medium crisis categories
MEDIUM_CRISIS_KEYWORDS = {
    'severe_emotional_distress': SEVERE_EMOTIONAL_DISTRESS,
    'severe_depression': SEVERE_DEPRESSION,
    'panic_anxiety_attacks': PANIC_ANXIETY_ATTACKS,
    'trauma_responses': TRAUMA_RESPONSES,
    'identity_crisis': IDENTITY_CRISIS,
    'relationship_trauma': RELATIONSHIP_TRAUMA,
    'severe_life_stress': SEVERE_LIFE_STRESS,
    'concerning_ideation': CONCERNING_IDEATION
}

def get_medium_crisis_keywords():
    """
    Returns the complete dictionary of medium crisis keywords
    
    Returns:
        dict: Dictionary with category names as keys and keyword lists as values
    """
    return MEDIUM_CRISIS_KEYWORDS

def get_category_keywords(category):
    """
    Get keywords for a specific medium crisis category
    
    Args:
        category (str): Category name ('severe_emotional_distress', 'panic_anxiety_attacks', etc.)
        
    Returns:
        list: List of keywords for the specified category
    """
    return MEDIUM_CRISIS_KEYWORDS.get(category, [])

def get_all_medium_keywords_flat():
    """
    Get all medium crisis keywords as a flat list (for regex compilation)
    
    Returns:
        list: All medium crisis keywords in a single list
    """
    all_keywords = []
    for keywords in MEDIUM_CRISIS_KEYWORDS.values():
        all_keywords.extend(keywords)
    return all_keywords

def get_medium_crisis_stats():
    """
    Get statistics about medium crisis keywords
    
    Returns:
        dict: Statistics including counts by category
    """
    stats = {}
    total = 0
    
    for category, keywords in MEDIUM_CRISIS_KEYWORDS.items():
        count = len(keywords)
        stats[category] = count
        total += count
    
    stats['total'] = total
    return stats

def check_medium_crisis_match(text):
    """
    Check if text matches any medium crisis keywords
    
    Args:
        text (str): Text to check
        
    Returns:
        dict: Match results with matched keywords and categories
    """
    text_lower = text.lower()
    matches = []
    matched_categories = set()
    
    for category, keywords in MEDIUM_CRISIS_KEYWORDS.items():
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
        'crisis_level': 'medium' if matches else 'none'
    }