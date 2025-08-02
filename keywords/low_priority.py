"""
Low Priority Crisis Test Phrases (50 phrases)
Target: 65% catch rate

These phrases represent mild distress or emotional difficulty that benefits from
gentle support but doesn't indicate crisis. Should be detected as "low" priority.
"""

def get_low_priority_phrases():
    """
    Returns 50 low priority crisis phrases for testing.
    Each phrase indicates mild distress or emotional difficulty.
    """
    return [
        {
            "message": "I'm feeling pretty down today",
            "expected_priority": "low",
            "subcategory": "mild_sadness",
            "description": "Temporary low mood"
        },
        {
            "message": "I've been having some anxiety lately",
            "expected_priority": "low",
            "subcategory": "mild_anxiety",
            "description": "Recent onset of mild anxiety"
        },
        {
            "message": "I'm going through a rough patch",
            "expected_priority": "low",
            "subcategory": "difficult_period",
            "description": "Temporary difficult life period"
        },
        {
            "message": "I feel a bit overwhelmed with work",
            "expected_priority": "low",
            "subcategory": "work_stress",
            "description": "Work-related overwhelm"
        },
        {
            "message": "I'm having trouble sleeping",
            "expected_priority": "low",
            "subcategory": "sleep_issues",
            "description": "Sleep difficulties"
        },
        {
            "message": "I feel sad and don't know why",
            "expected_priority": "low",
            "subcategory": "unexplained_sadness",
            "description": "Sadness without clear cause"
        },
        {
            "message": "I'm stressed about my relationships",
            "expected_priority": "low",
            "subcategory": "relationship_stress",
            "description": "Relationship-related stress"
        },
        {
            "message": "I feel disconnected from my friends",
            "expected_priority": "low",
            "subcategory": "social_disconnection",
            "description": "Feeling distant from friends"
        },
        {
            "message": "I'm worried about my future",
            "expected_priority": "low",
            "subcategory": "future_anxiety",
            "description": "Concerns about future prospects"
        },
        {
            "message": "I feel like I'm not good enough",
            "expected_priority": "low",
            "subcategory": "inadequacy_feelings",
            "description": "Feelings of inadequacy"
        },
        {
            "message": "I'm having self-doubt issues",
            "expected_priority": "low",
            "subcategory": "self_doubt",
            "description": "Self-doubt and uncertainty"
        },
        {
            "message": "I feel lonely sometimes",
            "expected_priority": "low",
            "subcategory": "occasional_loneliness",
            "description": "Periodic loneliness"
        },
        {
            "message": "I'm struggling with my identity",
            "expected_priority": "low",
            "subcategory": "identity_questions",
            "description": "Identity exploration and questioning"
        },
        {
            "message": "I feel insecure about myself",
            "expected_priority": "low",
            "subcategory": "insecurity",
            "description": "General insecurity feelings"
        },
        {
            "message": "I'm having trouble with motivation",
            "expected_priority": "low",
            "subcategory": "motivation_issues",
            "description": "Lack of motivation and drive"
        },
        {
            "message": "I feel like I'm falling behind",
            "expected_priority": "low",
            "subcategory": "comparison_concerns",
            "description": "Feeling behind peers or expectations"
        },
        {
            "message": "I'm dealing with mild depression",
            "expected_priority": "low",
            "subcategory": "mild_depression",
            "description": "Acknowledged mild depressive symptoms"
        },
        {
            "message": "I feel anxious about social situations",
            "expected_priority": "low",
            "subcategory": "social_anxiety",
            "description": "Social anxiety concerns"
        },
        {
            "message": "I'm having trouble with confidence",
            "expected_priority": "low",
            "subcategory": "confidence_issues",
            "description": "Low self-confidence"
        },
        {
            "message": "I feel like I don't belong",
            "expected_priority": "low",
            "subcategory": "belonging_issues",
            "description": "Feeling out of place or not belonging"
        },
        {
            "message": "I'm struggling with low self-esteem",
            "expected_priority": "low",
            "subcategory": "low_self_esteem",
            "description": "Poor self-regard and self-worth"
        },
        {
            "message": "I feel tired all the time",
            "expected_priority": "low",
            "subcategory": "fatigue",
            "description": "Persistent tiredness or fatigue"
        },
        {
            "message": "I'm having trouble focusing",
            "expected_priority": "low",
            "subcategory": "concentration_issues",
            "description": "Difficulty with focus and concentration"
        },
        {
            "message": "I feel like I'm not achieving anything",
            "expected_priority": "low",
            "subcategory": "achievement_concerns",
            "description": "Feeling unaccomplished or unproductive"
        },
        {
            "message": "I'm worried about disappointing others",
            "expected_priority": "low",
            "subcategory": "disappointment_fear",
            "description": "Fear of letting others down"
        },
        {
            "message": "I feel like I'm not living up to expectations",
            "expected_priority": "low",
            "subcategory": "expectation_pressure",
            "description": "Pressure from personal or external expectations"
        },
        {
            "message": "I'm having trouble with body image",
            "expected_priority": "low",
            "subcategory": "body_image_issues",
            "description": "Concerns about physical appearance"
        },
        {
            "message": "I feel like I'm missing out on life",
            "expected_priority": "low",
            "subcategory": "fomo",
            "description": "Fear of missing out on experiences"
        },
        {
            "message": "I'm struggling with perfectionism",
            "expected_priority": "low",
            "subcategory": "perfectionism",
            "description": "Perfectionist tendencies causing stress"
        },
        {
            "message": "I feel like I'm not smart enough",
            "expected_priority": "low",
            "subcategory": "intellectual_insecurity",
            "description": "Doubts about intelligence or capability"
        },
        {
            "message": "I'm having trouble with social anxiety",
            "expected_priority": "low",
            "subcategory": "social_anxiety",
            "description": "Anxiety in social interactions"
        },
        {
            "message": "I feel like I don't have enough friends",
            "expected_priority": "low",
            "subcategory": "friendship_concerns",
            "description": "Concerns about social connections"
        },
        {
            "message": "I'm worried about being judged",
            "expected_priority": "low",
            "subcategory": "judgment_fear",
            "description": "Fear of negative evaluation by others"
        },
        {
            "message": "I feel like I'm not attractive enough",
            "expected_priority": "low",
            "subcategory": "attractiveness_concerns",
            "description": "Insecurity about physical attractiveness"
        },
        {
            "message": "I'm struggling with imposter syndrome",
            "expected_priority": "low",
            "subcategory": "imposter_syndrome",
            "description": "Feeling like a fraud or impostor"
        },
        {
            "message": "I feel like I'm not talented enough",
            "expected_priority": "low",
            "subcategory": "talent_insecurity",
            "description": "Doubts about personal abilities or talents"
        },
        {
            "message": "I'm having trouble with procrastination",
            "expected_priority": "low",
            "subcategory": "procrastination",
            "description": "Difficulties with task completion and motivation"
        },
        {
            "message": "I feel like I'm wasting my life",
            "expected_priority": "low",
            "subcategory": "life_direction_concerns",
            "description": "Concerns about life direction and purpose"
        },
        {
            "message": "I'm worried about my career",
            "expected_priority": "low",
            "subcategory": "career_anxiety",
            "description": "Professional development concerns"
        },
        {
            "message": "I feel like I'm not interesting enough",
            "expected_priority": "low",
            "subcategory": "personality_insecurity",
            "description": "Doubts about personal interest or charisma"
        },
        {
            "message": "I'm struggling with comparison to others",
            "expected_priority": "low",
            "subcategory": "comparison_issues",
            "description": "Negative social comparison patterns"
        },
        {
            "message": "I feel like I'm not worthy of love",
            "expected_priority": "low",
            "subcategory": "love_worthiness",
            "description": "Doubts about deserving love and affection"
        },
        {
            "message": "I'm having trouble with boundaries",
            "expected_priority": "low",
            "subcategory": "boundary_issues",
            "description": "Difficulty setting or maintaining boundaries"
        },
        {
            "message": "I feel like I'm too sensitive",
            "expected_priority": "low",
            "subcategory": "sensitivity_concerns",
            "description": "Concerns about emotional sensitivity"
        },
        {
            "message": "I'm worried about my appearance",
            "expected_priority": "low",
            "subcategory": "appearance_anxiety",
            "description": "Anxiety about physical appearance"
        },
        {
            "message": "I feel like I'm not contributing enough",
            "expected_priority": "low",
            "subcategory": "contribution_concerns",
            "description": "Feeling inadequate in contributions to others"
        },
        {
            "message": "I'm struggling with decision-making",
            "expected_priority": "low",
            "subcategory": "decision_difficulty",
            "description": "Difficulty making choices and decisions"
        },
        {
            "message": "I feel like I'm not brave enough",
            "expected_priority": "low",
            "subcategory": "courage_concerns",
            "description": "Doubts about personal courage or bravery"
        },
        {
            "message": "I'm having trouble with self-acceptance",
            "expected_priority": "low",
            "subcategory": "self_acceptance_issues",
            "description": "Difficulty accepting oneself as is"
        },
        {
            "message": "I feel like I'm not deserving of happiness",
            "expected_priority": "low",
            "subcategory": "happiness_worthiness",
            "description": "Doubts about deserving happiness and joy"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "definite_low",
    "description": "Low Priority Crisis",
    "target_pass_rate": 65.0,
    "critical": False,
    "allow_escalation": False,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "mild_depression": 3,
    "mild_anxiety": 4,
    "social_anxiety": 3,
    "self_esteem_issues": 8,
    "identity_questions": 3,
    "relationship_stress": 3,
    "work_stress": 2,
    "future_anxiety": 2,
    "body_image_issues": 3,
    "perfectionism": 2,
    "comparison_issues": 3,
    "motivation_issues": 2,
    "confidence_issues": 4,
    "belonging_issues": 2,
    "achievement_concerns": 3,
    "life_direction_concerns": 3,
    "insecurity_general": 6
}