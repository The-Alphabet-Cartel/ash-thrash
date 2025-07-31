"""
Low Crisis Keywords for Ash-Thrash Testing - EXACT COPY from Ash Bot
These keywords trigger gentle Ash responses without team alerts

Crisis Level: LOW 🟢
Response: Ash reply only (no alerts to team)
"""

# Depression symptoms - mild to moderate depression indicators
DEPRESSION_SYMPTOMS = [
    'feeling depressed', 'feeling down', 'feeling low', 'feeling sad',
    'feeling blue', 'feeling empty', 'feeling hopeless', 'feeling worthless',
    'mood is off', 'not feeling great', 'struggling mentally',
    'mental health declining', 'depression symptoms', 'depressive thoughts',
    'feeling unmotivated', 'lost interest in things', 'anhedonia',
    'nothing feels enjoyable', 'hard to feel happy', 'emotional numbness'
]

# Anxiety symptoms - general anxiety and stress
ANXIETY_SYMPTOMS = [
    'feeling anxious', 'anxiety', 'stressed out', 'really stressed',
    'panic', 'worried', 'nervous', 'on edge', 'restless',
    'mind racing', 'can\'t relax', 'tense', 'jittery',
    'anxiety symptoms', 'social anxiety', 'performance anxiety',
    'test anxiety', 'job interview anxiety', 'meeting anxiety',
    'phone anxiety', 'driving anxiety', 'health anxiety'
]

# Identity and self-worth struggles
IDENTITY_STRUGGLES = [
    'questioning my identity', 'don\'t know who I am', 'identity issues',
    'struggling with self worth', 'low self esteem', 'feeling worthless',
    'imposter syndrome', 'not good enough', 'feeling inadequate',
    'comparing myself to others', 'feeling inferior', 'self doubt',
    'questioning my sexuality', 'questioning my gender', 'coming out struggles',
    'family acceptance issues', 'hiding who I am', 'living a lie'
]

# Relationship and social difficulties
RELATIONSHIP_TRAUMA = [
    'relationship problems', 'dating struggles', 'breakup', 'lonely',
    'feeling isolated', 'no friends', 'social rejection', 'bullying',
    'toxic friends', 'friendship drama', 'family conflict',
    'roommate issues', 'workplace drama', 'social anxiety',
    'fear of abandonment', 'trust issues', 'attachment problems'
]

# LGBTQIA+ specific struggles
LGBTQIA_STRUGGLES = [
    'coming out', 'in the closet', 'family doesn\'t accept me',
    'transphobia', 'homophobia', 'biphobia', 'gender dysphoria',
    'transition struggles', 'chosen name issues', 'pronoun struggles',
    'bathroom anxiety', 'binding problems', 'voice training',
    'hormone therapy', 'surgery consultation', 'LGBT discrimination',
    'religious trauma', 'conversion therapy', 'pride month stress'
]

# Academic and life pressures
FAILURE_FEELINGS = [
    'feeling like a failure', 'disappointed in myself', 'not living up to expectations',
    'parents disappointed', 'failing at life', 'behind my peers',
    'wasted potential', 'missed opportunities', 'regret my choices',
    'academic pressure', 'career confusion', 'quarter life crisis'
]

# Daily functioning struggles
DAILY_FUNCTIONING = [
    'can\'t get motivated', 'procrastinating everything', 'messy room',
    'haven\'t showered', 'eating poorly', 'skipping meals',
    'sleep schedule messed up', 'doom scrolling', 'avoiding responsibilities',
    'executive dysfunction', 'task paralysis', 'overwhelmed by chores',
    'self care failing', 'basic hygiene hard', 'dishes piling up',
    'laundry mountain', 'can\'t adult today', 'functioning poorly'
]

# Work and school stress
WORK_SCHOOL_STRESS = [
    'work is overwhelming', 'burned out', 'deadline pressure',
    'boss is terrible', 'toxic workplace', 'underpaid overworked',
    'school stress', 'exam anxiety', 'paper due', 'grades dropping',
    'struggling in class', 'teacher doesn\'t like me', 'group project hell',
    'job search depression', 'interview anxiety', 'rejection letters',
    'career uncertainty', 'major regret', 'graduation anxiety'
]

# Seasonal and situational depression
SEASONAL_SITUATIONAL = [
    'seasonal depression', 'winter blues', 'holiday depression',
    'anniversary depression', 'birthday blues', 'new year depression',
    'monday blues', 'sunday scaries', 'back to school anxiety',
    'moving stress', 'change anxiety', 'transition stress'
]

# Combine all low crisis categories
LOW_CRISIS_KEYWORDS = {
    'depression_symptoms': DEPRESSION_SYMPTOMS + SEASONAL_SITUATIONAL,
    'anxiety_symptoms': ANXIETY_SYMPTOMS,
    'identity_struggles': IDENTITY_STRUGGLES,
    'relationship_trauma': RELATIONSHIP_TRAUMA,
    'lgbtqia_struggles': LGBTQIA_STRUGGLES,
    'failure_feelings': FAILURE_FEELINGS,
    'daily_functioning': DAILY_FUNCTIONING,
    'work_school_stress': WORK_SCHOOL_STRESS
}

def get_low_crisis_keywords():
    """
    Returns the complete dictionary of low crisis keywords
    
    Returns:
        dict: Dictionary with category names as keys and keyword lists as values
    """
    return LOW_CRISIS_KEYWORDS

def get_category_keywords(category):
    """
    Get keywords for a specific low crisis category
    
    Args:
        category (str): Category name ('depression_symptoms', 'anxiety_symptoms', etc.)
        
    Returns:
        list: List of keywords for the specified category
    """
    return LOW_CRISIS_KEYWORDS.get(category, [])

def get_all_low_keywords_flat():
    """
    Get all low crisis keywords as a flat list (for regex compilation)
    
    Returns:
        list: All low crisis keywords in a single list
    """
    all_keywords = []
    for keywords in LOW_CRISIS_KEYWORDS.values():
        all_keywords.extend(keywords)
    return all_keywords

def get_low_crisis_stats():
    """
    Get statistics about low crisis keywords
    
    Returns:
        dict: Statistics including counts by category
    """
    stats = {}
    total = 0
    
    for category, keywords in LOW_CRISIS_KEYWORDS.items():
        count = len(keywords)
        stats[category] = count
        total += count
    
    stats['total'] = total
    return stats

def check_low_crisis_match(text):
    """
    Check if text matches any low crisis keywords
    
    Args:
        text (str): Text to check
        
    Returns:
        dict: Match results with matched keywords and categories
    """
    text_lower = text.lower()
    matches = []
    matched_categories = set()
    
    for category, keywords in LOW_CRISIS_KEYWORDS.items():
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
        'crisis_level': 'low' if matches else 'none'
    }