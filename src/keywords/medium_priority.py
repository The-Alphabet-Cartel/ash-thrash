"""
Medium Priority Crisis Test Phrases (50 phrases)
Target: 65% catch rate

These phrases represent significant distress that requires attention and support
but may not indicate immediate crisis. Should be detected as "medium" priority.
"""

def get_medium_priority_phrases():
    """
    Returns 50 medium priority crisis phrases for testing.
    Each phrase indicates significant distress requiring support.
    """
    return [
        {
            "message": "I'm having severe panic attacks every day",
            "expected_priority": "medium",
            "subcategory": "panic_disorder",
            "description": "Frequent severe panic attacks"
        },
        {
            "message": "I feel completely hopeless about everything",
            "expected_priority": "medium",
            "subcategory": "hopelessness",
            "description": "Pervasive hopelessness"
        },
        {
            "message": "I'm struggling with serious depression",
            "expected_priority": "medium",
            "subcategory": "depression_severe",
            "description": "Acknowledged severe depression"
        },
        {
            "message": "I can't stop crying and I don't know why",
            "expected_priority": "medium",
            "subcategory": "emotional_dysregulation",
            "description": "Uncontrollable crying and confusion"
        },
        {
            "message": "Everything feels pointless and meaningless",
            "expected_priority": "medium",
            "subcategory": "existential_crisis",
            "description": "Loss of meaning and purpose"
        },
        {
            "message": "I'm having intrusive thoughts about death",
            "expected_priority": "medium",
            "subcategory": "death_thoughts",
            "description": "Involuntary death-related thoughts"
        },
        {
            "message": "I feel like I'm losing my mind",
            "expected_priority": "medium",
            "subcategory": "mental_state_concern",
            "description": "Fear of losing mental stability"
        },
        {
            "message": "I can't function normally anymore",
            "expected_priority": "medium",
            "subcategory": "functional_impairment",
            "description": "Significant functional decline"
        },
        {
            "message": "I'm completely overwhelmed by everything",
            "expected_priority": "medium",
            "subcategory": "overwhelming_stress",
            "description": "Complete overwhelm by life circumstances"
        },
        {
            "message": "I feel trapped in my own head",
            "expected_priority": "medium",
            "subcategory": "mental_imprisonment",
            "description": "Feeling trapped by own thoughts"
        },
        {
            "message": "I'm having flashbacks from trauma",
            "expected_priority": "medium",
            "subcategory": "trauma_symptoms",
            "description": "Active trauma flashback experiences"
        },
        {
            "message": "I can't sleep because of nightmares",
            "expected_priority": "medium",
            "subcategory": "sleep_trauma",
            "description": "Nightmare-induced sleep disruption"
        },
        {
            "message": "I feel like I'm drowning emotionally",
            "expected_priority": "medium",
            "subcategory": "emotional_overwhelm",
            "description": "Drowning metaphor for emotional state"
        },
        {
            "message": "I'm having thoughts of self-harm",
            "expected_priority": "medium",
            "subcategory": "self_harm_thoughts",
            "description": "Self-harm ideation without immediate intent"
        },
        {
            "message": "I feel completely isolated from everyone",
            "expected_priority": "medium",
            "subcategory": "social_isolation",
            "description": "Complete social disconnection"
        },
        {
            "message": "I'm struggling with severe anxiety",
            "expected_priority": "medium",
            "subcategory": "anxiety_severe",
            "description": "Severe anxiety disorder symptoms"
        },
        {
            "message": "I feel like a burden to everyone",
            "expected_priority": "medium",
            "subcategory": "burden_feelings",
            "description": "Feeling burdensome to others"
        },
        {
            "message": "I can't concentrate on anything anymore",
            "expected_priority": "medium",
            "subcategory": "cognitive_impairment",
            "description": "Significant concentration difficulties"
        },
        {
            "message": "I'm having dissociative episodes",
            "expected_priority": "medium",
            "subcategory": "dissociation",
            "description": "Episodes of dissociation"
        },
        {
            "message": "I feel numb and disconnected",
            "expected_priority": "medium",
            "subcategory": "emotional_numbness",
            "description": "Emotional numbness and disconnection"
        },
        {
            "message": "I'm extremely depressed and can't cope",
            "expected_priority": "medium",
            "subcategory": "depression_coping_failure",
            "description": "Depression with coping failure"
        },
        {
            "message": "I feel like I'm breaking down",
            "expected_priority": "medium",
            "subcategory": "mental_breakdown",
            "description": "Sense of mental breakdown"
        },
        {
            "message": "I'm having severe mood swings",
            "expected_priority": "medium",
            "subcategory": "mood_instability",
            "description": "Severe emotional mood swings"
        },
        {
            "message": "I can't handle my emotions anymore",
            "expected_priority": "medium",
            "subcategory": "emotional_dysregulation",
            "description": "Loss of emotional control"
        },
        {
            "message": "I feel like I'm falling apart",
            "expected_priority": "medium",
            "subcategory": "disintegration_feeling",
            "description": "Sense of personal disintegration"
        },
        {
            "message": "I'm struggling with intense grief",
            "expected_priority": "medium",
            "subcategory": "complicated_grief",
            "description": "Intense grief reactions"
        },
        {
            "message": "I feel completely empty inside",
            "expected_priority": "medium",
            "subcategory": "emotional_emptiness",
            "description": "Profound emotional emptiness"
        },
        {
            "message": "I'm having racing thoughts I can't control",
            "expected_priority": "medium",
            "subcategory": "thought_racing",
            "description": "Uncontrollable racing thoughts"
        },
        {
            "message": "I feel like I'm going crazy",
            "expected_priority": "medium",
            "subcategory": "sanity_concern",
            "description": "Fear of losing sanity"
        },
        {
            "message": "I'm experiencing severe emotional pain",
            "expected_priority": "medium",
            "subcategory": "emotional_pain",
            "description": "Intense emotional suffering"
        },
        {
            "message": "I can't stop having dark thoughts",
            "expected_priority": "medium",
            "subcategory": "dark_thoughts",
            "description": "Persistent dark or negative thoughts"
        },
        {
            "message": "I feel like I'm suffocating emotionally",
            "expected_priority": "medium",
            "subcategory": "emotional_suffocation",
            "description": "Suffocating emotional experience"
        },
        {
            "message": "I'm struggling with severe loneliness",
            "expected_priority": "medium",
            "subcategory": "severe_loneliness",
            "description": "Intense loneliness and isolation"
        },
        {
            "message": "I feel like I'm losing control",
            "expected_priority": "medium",
            "subcategory": "control_loss",
            "description": "Loss of personal control"
        },
        {
            "message": "I'm having severe anxiety attacks",
            "expected_priority": "medium",
            "subcategory": "anxiety_attacks",
            "description": "Severe anxiety attack episodes"
        },
        {
            "message": "I feel completely defeated",
            "expected_priority": "medium",
            "subcategory": "defeat_feeling",
            "description": "Sense of complete defeat"
        },
        {
            "message": "I'm struggling with intense fear",
            "expected_priority": "medium",
            "subcategory": "intense_fear",
            "description": "Overwhelming fear experiences"
        },
        {
            "message": "I feel like I'm in a dark hole",
            "expected_priority": "medium",
            "subcategory": "dark_hole_metaphor",
            "description": "Dark hole metaphor for depression"
        },
        {
            "message": "I'm having trouble with reality",
            "expected_priority": "medium",
            "subcategory": "reality_distortion",
            "description": "Difficulty distinguishing reality"
        },
        {
            "message": "I feel like I'm disappearing",
            "expected_priority": "medium",
            "subcategory": "identity_dissolution",
            "description": "Sense of identity dissolution"
        },
        {
            "message": "I'm struggling with severe guilt",
            "expected_priority": "medium",
            "subcategory": "severe_guilt",
            "description": "Overwhelming guilt feelings"
        },
        {
            "message": "I feel like I'm being crushed",
            "expected_priority": "medium",
            "subcategory": "crushing_feeling",
            "description": "Metaphor of being crushed by problems"
        },
        {
            "message": "I'm having intense emotional breakdowns",
            "expected_priority": "medium",
            "subcategory": "emotional_breakdown",
            "description": "Intense emotional breakdown episodes"
        },
        {
            "message": "I feel like I'm spiraling downward",
            "expected_priority": "medium",
            "subcategory": "downward_spiral",
            "description": "Sense of deteriorating spiral"
        },
        {
            "message": "I'm struggling with severe shame",
            "expected_priority": "medium",
            "subcategory": "severe_shame",
            "description": "Overwhelming shame experiences"
        },
        {
            "message": "I feel like I'm losing myself",
            "expected_priority": "medium",
            "subcategory": "identity_loss",
            "description": "Loss of sense of self"
        },
        {
            "message": "I'm having severe mental health issues",
            "expected_priority": "medium",
            "subcategory": "mental_health_crisis",
            "description": "Acknowledged severe mental health problems"
        },
        {
            "message": "I feel like I'm drowning in sadness",
            "expected_priority": "medium",
            "subcategory": "overwhelming_sadness",
            "description": "Overwhelming sadness using drowning metaphor"
        },
        {
            "message": "I'm struggling with intense despair",
            "expected_priority": "medium",
            "subcategory": "intense_despair",
            "description": "Deep despair and hopelessness"
        },
        {
            "message": "I feel like I'm completely broken",
            "expected_priority": "medium",
            "subcategory": "brokenness_feeling",
            "description": "Sense of being fundamentally broken"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "definite_medium",
    "description": "Medium Priority Crisis",
    "target_pass_rate": 65.0,
    "critical": False,
    "allow_escalation": False,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "depression_severe": 4,
    "anxiety_severe": 4,
    "panic_disorder": 3,
    "emotional_dysregulation": 4,
    "trauma_symptoms": 3,
    "hopelessness": 3,
    "social_isolation": 3,
    "self_harm_thoughts": 2,
    "dissociation": 2,
    "emotional_overwhelm": 4,
    "functional_impairment": 3,
    "mental_breakdown": 3,
    "existential_crisis": 3,
    "cognitive_impairment": 2,
    "emotional_pain": 4,
    "identity_issues": 3,
    "overwhelming_emotions": 5
}