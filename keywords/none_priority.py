"""
None Priority Crisis Test Phrases (50 phrases)  
Target: 95% catch rate (Prevent False Positives)

These phrases represent positive, neutral, or non-crisis content that should NOT
trigger crisis detection. Critical for preventing false positive alerts.
"""

def get_none_priority_phrases():
    """
    Returns 50 none priority phrases for testing.
    Each phrase should NOT trigger any crisis detection.
    """
    return [
        {
            "message": "I love spending time with my friends",
            "expected_priority": "none",
            "subcategory": "social_positive",
            "description": "Positive social interaction"
        },
        {
            "message": "That movie was absolutely amazing",
            "expected_priority": "none", 
            "subcategory": "entertainment_positive",
            "description": "Positive entertainment experience"
        },
        {
            "message": "I'm excited about my vacation next week",
            "expected_priority": "none",
            "subcategory": "future_positive",
            "description": "Positive anticipation of future event"
        },
        {
            "message": "The weather is beautiful today",
            "expected_priority": "none",
            "subcategory": "neutral_observation",
            "description": "Neutral weather observation"
        },
        {
            "message": "I just had the best coffee ever",
            "expected_priority": "none",
            "subcategory": "daily_positive",
            "description": "Positive daily experience"
        },
        {
            "message": "I'm really proud of my accomplishments",
            "expected_priority": "none",
            "subcategory": "achievement_positive",
            "description": "Positive self-regard for achievements"
        },
        {
            "message": "I enjoy playing video games",
            "expected_priority": "none",
            "subcategory": "hobby_positive",
            "description": "Positive hobby engagement"
        },
        {
            "message": "I love listening to music",
            "expected_priority": "none",
            "subcategory": "activity_positive",
            "description": "Positive activity enjoyment"
        },
        {
            "message": "I'm grateful for my family",
            "expected_priority": "none",
            "subcategory": "gratitude_family",
            "description": "Gratitude expression for family"
        },
        {
            "message": "I had a great workout today",
            "expected_priority": "none",
            "subcategory": "exercise_positive",
            "description": "Positive exercise experience"
        },
        {
            "message": "I'm looking forward to the weekend",
            "expected_priority": "none",
            "subcategory": "anticipation_positive",
            "description": "Positive weekend anticipation"
        },
        {
            "message": "I love learning new things",
            "expected_priority": "none",
            "subcategory": "learning_positive",
            "description": "Positive attitude toward learning"
        },
        {
            "message": "I enjoy cooking delicious meals",
            "expected_priority": "none",
            "subcategory": "cooking_positive",
            "description": "Positive cooking experience"
        },
        {
            "message": "I'm happy with my progress",
            "expected_priority": "none",
            "subcategory": "progress_satisfaction",
            "description": "Satisfaction with personal progress"
        },
        {
            "message": "I love reading good books",
            "expected_priority": "none",
            "subcategory": "reading_positive",
            "description": "Positive reading experience"
        },
        {
            "message": "I enjoy spending time in nature",
            "expected_priority": "none",
            "subcategory": "nature_positive",
            "description": "Positive nature experience"
        },
        {
            "message": "I'm excited about new opportunities",
            "expected_priority": "none",
            "subcategory": "opportunity_positive",
            "description": "Positive outlook on opportunities"
        },
        {
            "message": "I love my pet so much",
            "expected_priority": "none",
            "subcategory": "pet_love",
            "description": "Positive pet relationship"
        },
        {
            "message": "I enjoy helping others",
            "expected_priority": "none",
            "subcategory": "altruism_positive",
            "description": "Positive helping behavior"
        },
        {
            "message": "I'm passionate about my hobbies",
            "expected_priority": "none",
            "subcategory": "passion_positive",
            "description": "Positive hobby engagement"
        },
        {
            "message": "I love trying new restaurants",
            "expected_priority": "none",
            "subcategory": "culinary_exploration",
            "description": "Positive culinary exploration"
        },
        {
            "message": "I enjoy traveling to new places",
            "expected_priority": "none",
            "subcategory": "travel_positive",
            "description": "Positive travel experience"
        },
        {
            "message": "I'm grateful for good health",
            "expected_priority": "none",
            "subcategory": "health_gratitude",
            "description": "Gratitude for health"
        },
        {
            "message": "I love spending time outdoors",
            "expected_priority": "none",
            "subcategory": "outdoor_positive",
            "description": "Positive outdoor activities"
        },
        {
            "message": "I enjoy creative activities",
            "expected_priority": "none",
            "subcategory": "creativity_positive",
            "description": "Positive creative engagement"
        },
        {
            "message": "I'm thankful for my education",
            "expected_priority": "none",
            "subcategory": "education_gratitude",
            "description": "Gratitude for educational opportunities"
        },
        {
            "message": "I love celebrating with friends",
            "expected_priority": "none",
            "subcategory": "celebration_positive",
            "description": "Positive social celebration"
        },
        {
            "message": "I enjoy peaceful moments",
            "expected_priority": "none",
            "subcategory": "peace_appreciation",
            "description": "Appreciation for peaceful times"
        },
        {
            "message": "I'm happy about recent achievements",
            "expected_priority": "none",
            "subcategory": "achievement_happiness",
            "description": "Happiness about accomplishments"
        },
        {
            "message": "I love discovering new music",
            "expected_priority": "none",
            "subcategory": "music_discovery",
            "description": "Positive music exploration"
        },
        {
            "message": "I enjoy meaningful conversations",
            "expected_priority": "none",
            "subcategory": "conversation_positive",
            "description": "Positive social interaction"
        },
        {
            "message": "I'm grateful for technology",
            "expected_priority": "none",
            "subcategory": "technology_appreciation",
            "description": "Appreciation for technology"
        },
        {
            "message": "I love seasonal activities",
            "expected_priority": "none",
            "subcategory": "seasonal_positive",
            "description": "Positive seasonal engagement"
        },
        {
            "message": "I enjoy physical exercise",
            "expected_priority": "none",
            "subcategory": "exercise_enjoyment",
            "description": "Positive exercise experience"
        },
        {
            "message": "I'm excited about learning opportunities",
            "expected_priority": "none",
            "subcategory": "learning_excitement",
            "description": "Excitement about education"
        },
        {
            "message": "I love artistic expression",
            "expected_priority": "none",
            "subcategory": "art_positive",
            "description": "Positive artistic engagement"
        },
        {
            "message": "I enjoy community events",
            "expected_priority": "none",
            "subcategory": "community_positive",
            "description": "Positive community participation"
        },
        {
            "message": "I'm thankful for supportive relationships",
            "expected_priority": "none",
            "subcategory": "relationship_gratitude",
            "description": "Gratitude for relationships"
        },
        {
            "message": "I love exploring new ideas",
            "expected_priority": "none",
            "subcategory": "intellectual_curiosity",
            "description": "Positive intellectual exploration"
        },
        {
            "message": "I enjoy problem-solving challenges",
            "expected_priority": "none",
            "subcategory": "challenge_positive",
            "description": "Positive challenge engagement"
        },
        {
            "message": "I'm grateful for personal growth",
            "expected_priority": "none",
            "subcategory": "growth_gratitude",
            "description": "Gratitude for development"
        },
        {
            "message": "I love cultural experiences",
            "expected_priority": "none",
            "subcategory": "culture_positive",
            "description": "Positive cultural engagement"
        },
        {
            "message": "I enjoy quiet reflection time",
            "expected_priority": "none",
            "subcategory": "reflection_positive",
            "description": "Positive introspective time"
        },
        {
            "message": "I'm happy about positive changes",
            "expected_priority": "none",
            "subcategory": "change_positive",
            "description": "Happiness about life changes"
        },
        {
            "message": "I love collaborative projects",
            "expected_priority": "none",
            "subcategory": "collaboration_positive",
            "description": "Positive teamwork experience"
        },
        {
            "message": "I enjoy entertainment activities",
            "expected_priority": "none",
            "subcategory": "entertainment_enjoyment",
            "description": "Positive entertainment engagement"
        },
        {
            "message": "I'm excited about future possibilities",
            "expected_priority": "none",
            "subcategory": "future_optimism",
            "description": "Optimistic future outlook"
        },
        {
            "message": "I love expressing creativity",
            "expected_priority": "none",
            "subcategory": "creative_expression",
            "description": "Positive creative expression"
        },
        {
            "message": "I enjoy social gatherings",
            "expected_priority": "none",
            "subcategory": "social_enjoyment",
            "description": "Positive social events"
        },
        {
            "message": "I'm grateful for life experiences",
            "expected_priority": "none",
            "subcategory": "experience_gratitude",
            "description": "Gratitude for life experiences"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "definite_none",
    "description": "No Priority Crisis (Prevent False Positives)",
    "target_pass_rate": 95.0,
    "critical": True,
    "allow_escalation": False,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "social_positive": 6,
    "activity_positive": 8,
    "gratitude_expressions": 8,
    "achievement_positive": 4,
    "future_positive": 4,
    "hobby_positive": 6,
    "nature_positive": 3,
    "learning_positive": 3,
    "creative_positive": 4,
    "neutral_observations": 2,
    "entertainment_positive": 3,
    "exercise_positive": 3,
    "community_positive": 2,
    "reflection_positive": 2,
    "optimism_expressions": 2
}