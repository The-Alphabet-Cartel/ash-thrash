"""
Maybe Medium/Low Priority Test Phrases (50 phrases)
Target: 80% catch rate (Allow escalation to medium, prevent de-escalation)

These phrases represent borderline cases between low and medium priority.
Should be detected as "low" or "medium" priority (escalation allowed).
De-escalation to "none" is considered failure.
"""

def get_maybe_medium_low_phrases():
    """
    Returns 50 maybe medium/low priority phrases for testing.
    Each phrase represents borderline concern that could be low or medium.
    Escalation to medium is acceptable, de-escalation to none is not.
    """
    return [
        {
            "message": "I've been feeling kind of off lately",
            "expected_priority": "low",
            "subcategory": "vague_discomfort",
            "description": "Undefined feeling of being unwell"
        },
        {
            "message": "Things haven't been going great",
            "expected_priority": "low",
            "subcategory": "general_difficulty",
            "description": "General life difficulties"
        },
        {
            "message": "I'm having some difficulties",
            "expected_priority": "low",
            "subcategory": "unspecified_problems",
            "description": "Vague difficulties without specifics"
        },
        {
            "message": "I've been struggling a bit",
            "expected_priority": "low",
            "subcategory": "mild_struggle",
            "description": "Moderate level of personal struggle"
        },
        {
            "message": "Things feel challenging right now",
            "expected_priority": "low",
            "subcategory": "current_challenges",
            "description": "Present moment difficulties"
        },
        {
            "message": "I'm not feeling my best",
            "expected_priority": "low",
            "subcategory": "suboptimal_state",
            "description": "Below optimal emotional state"
        },
        {
            "message": "I've been having some troubles",
            "expected_priority": "low",
            "subcategory": "general_troubles",
            "description": "Unspecified personal troubles"
        },
        {
            "message": "Things have been stressful",
            "expected_priority": "low",
            "subcategory": "stress_acknowledgment",
            "description": "Recognition of increased stress"
        },
        {
            "message": "I'm feeling somewhat overwhelmed",
            "expected_priority": "low",
            "subcategory": "mild_overwhelm",
            "description": "Moderate sense of being overwhelmed"
        },
        {
            "message": "I've been having a hard time",
            "expected_priority": "low",
            "subcategory": "difficult_period",
            "description": "Experiencing difficult times"
        },
        {
            "message": "Things feel difficult",
            "expected_priority": "low",
            "subcategory": "perceived_difficulty",
            "description": "General sense of difficulty"
        },
        {
            "message": "I'm not doing great",
            "expected_priority": "low",
            "subcategory": "poor_state",
            "description": "Below average functioning"
        },
        {
            "message": "I've been feeling down",
            "expected_priority": "low",
            "subcategory": "low_mood",
            "description": "Depressed mood state"
        },
        {
            "message": "Things have been tough",
            "expected_priority": "low",
            "subcategory": "tough_circumstances",
            "description": "Challenging life circumstances"
        },
        {
            "message": "I'm feeling a bit lost",
            "expected_priority": "low",
            "subcategory": "direction_uncertainty",
            "description": "Uncertainty about direction"
        },
        {
            "message": "I've been struggling with things",
            "expected_priority": "low",
            "subcategory": "general_struggle",
            "description": "General life struggles"
        },
        {
            "message": "Things feel heavy",
            "expected_priority": "low",
            "subcategory": "emotional_weight",
            "description": "Emotional burden or heaviness"
        },
        {
            "message": "I'm not feeling well emotionally",
            "expected_priority": "low",
            "subcategory": "emotional_unwellness",
            "description": "Poor emotional state"
        },
        {
            "message": "I've been having some issues",
            "expected_priority": "low",
            "subcategory": "unspecified_issues",
            "description": "Vague personal issues"
        },
        {
            "message": "Things feel complicated",
            "expected_priority": "low",
            "subcategory": "complexity_overwhelm",
            "description": "Life feeling overly complex"
        },
        {
            "message": "I'm feeling somewhat sad",
            "expected_priority": "low",
            "subcategory": "moderate_sadness",
            "description": "Mild to moderate sadness"
        },
        {
            "message": "I've been having concerns",
            "expected_priority": "low",
            "subcategory": "general_concerns",
            "description": "Unspecified worries or concerns"
        },
        {
            "message": "Things feel uncertain",
            "expected_priority": "low",
            "subcategory": "uncertainty_discomfort",
            "description": "Discomfort with uncertainty"
        },
        {
            "message": "I'm not feeling confident",
            "expected_priority": "low",
            "subcategory": "confidence_lack",
            "description": "Reduced self-confidence"
        },
        {
            "message": "I've been experiencing difficulties",
            "expected_priority": "low",
            "subcategory": "ongoing_difficulties",
            "description": "Persistent personal difficulties"
        },
        {
            "message": "Things feel overwhelming sometimes",
            "expected_priority": "low",
            "subcategory": "intermittent_overwhelm",
            "description": "Occasional overwhelming feelings"
        },
        {
            "message": "I'm feeling a bit anxious",
            "expected_priority": "low",
            "subcategory": "mild_anxiety",
            "description": "Low-level anxiety"
        },
        {
            "message": "I've been having worries",
            "expected_priority": "low",
            "subcategory": "general_worries",
            "description": "Unspecified worries"
        },
        {
            "message": "Things feel unstable",
            "expected_priority": "low",
            "subcategory": "stability_concerns",
            "description": "Sense of instability"
        },
        {
            "message": "I'm not feeling secure",
            "expected_priority": "low",
            "subcategory": "security_lack",
            "description": "Feeling insecure or unsafe"
        },
        {
            "message": "I've been having some problems",
            "expected_priority": "low",
            "subcategory": "unspecified_problems",
            "description": "Vague personal problems"
        },
        {
            "message": "Things feel burdensome",
            "expected_priority": "low",
            "subcategory": "burden_sensation",
            "description": "Life feeling like a burden"
        },
        {
            "message": "I'm feeling somewhat troubled",
            "expected_priority": "low",
            "subcategory": "mild_trouble",
            "description": "Moderate level of being troubled"
        },
        {
            "message": "I've been having challenges",
            "expected_priority": "low",
            "subcategory": "general_challenges",
            "description": "Unspecified personal challenges"
        },
        {
            "message": "Things feel discouraging",
            "expected_priority": "low",
            "subcategory": "discouragement",
            "description": "Feeling discouraged about circumstances"
        },
        {
            "message": "I'm not feeling optimistic",
            "expected_priority": "low",
            "subcategory": "optimism_lack",
            "description": "Absence of optimistic outlook"
        },
        {
            "message": "I've been experiencing stress",
            "expected_priority": "low",
            "subcategory": "stress_experience",
            "description": "Ongoing stress experiences"
        },
        {
            "message": "Things feel draining",
            "expected_priority": "low",
            "subcategory": "energy_drain",
            "description": "Life circumstances feeling draining"
        },
        {
            "message": "I'm feeling a bit hopeless",
            "expected_priority": "low",
            "subcategory": "mild_hopelessness",
            "description": "Low-level hopelessness"
        },
        {
            "message": "I've been having setbacks",
            "expected_priority": "low",
            "subcategory": "setback_experiences",
            "description": "Experiencing personal setbacks"
        },
        {
            "message": "Things feel frustrating",
            "expected_priority": "low",
            "subcategory": "frustration_experience",
            "description": "General frustration with circumstances"
        },
        {
            "message": "I'm not feeling motivated",
            "expected_priority": "low",
            "subcategory": "motivation_lack",
            "description": "Absence of motivation"
        },
        {
            "message": "I've been experiencing pressure",
            "expected_priority": "low",
            "subcategory": "pressure_sensation",
            "description": "Feeling under pressure"
        },
        {
            "message": "Things feel exhausting",
            "expected_priority": "low",
            "subcategory": "exhaustion_feeling",
            "description": "Life feeling exhausting"
        },
        {
            "message": "I'm feeling somewhat defeated",
            "expected_priority": "low",
            "subcategory": "mild_defeat",
            "description": "Moderate sense of defeat"
        },
        {
            "message": "I've been having doubts",
            "expected_priority": "low",
            "subcategory": "doubt_experience",
            "description": "Experiencing self-doubt"
        },
        {
            "message": "Things feel confusing",
            "expected_priority": "low",
            "subcategory": "confusion_state",
            "description": "Feeling confused about circumstances"
        },
        {
            "message": "I'm not feeling strong",
            "expected_priority": "low",
            "subcategory": "strength_lack",
            "description": "Feeling weak or lacking strength"
        },
        {
            "message": "I've been experiencing pain",
            "expected_priority": "low",
            "subcategory": "pain_experience",
            "description": "Experiencing emotional pain"
        },
        {
            "message": "Things feel disappointing",
            "expected_priority": "low",
            "subcategory": "disappointment",
            "description": "Feeling disappointed with circumstances"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "maybe_medium_low",
    "description": "Maybe Medium/Low (No Priority Drops)",
    "target_pass_rate": 80.0,
    "critical": False,
    "allow_escalation": True,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "vague_discomfort": 8,
    "general_difficulties": 10,
    "mild_overwhelm": 6,
    "emotional_state_poor": 8,
    "unspecified_troubles": 6,
    "mild_depression_anxiety": 5,
    "uncertainty_concerns": 3,
    "motivation_confidence_lack": 4
}