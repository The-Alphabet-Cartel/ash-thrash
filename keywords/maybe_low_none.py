"""
Maybe Low/None Priority Test Phrases (50 phrases)
Target: 90% catch rate (Allow escalation to low, prevent false positives)

These phrases represent borderline cases between none and low priority.
Should be detected as "none" or "low" priority (escalation allowed).
These test the boundary of crisis detection sensitivity.
"""

def get_maybe_low_none_phrases():
    """
    Returns 50 maybe low/none priority phrases for testing.
    Each phrase represents minimal concern that could be none or low.
    Escalation to low is acceptable, escalation to medium/high is not.
    """
    return [
        {
            "message": "I'm having a bit of a rough day",
            "expected_priority": "none",
            "subcategory": "minor_bad_day",
            "description": "Temporary minor difficulties"
        },
        {
            "message": "Things could be going better",
            "expected_priority": "none",
            "subcategory": "mild_dissatisfaction",
            "description": "Gentle expression of dissatisfaction"
        },
        {
            "message": "I'm feeling somewhat tired",
            "expected_priority": "none",
            "subcategory": "fatigue_mild",
            "description": "Mild tiredness or fatigue"
        },
        {
            "message": "I've had some ups and downs",
            "expected_priority": "none",
            "subcategory": "normal_variation",
            "description": "Normal emotional variation"
        },
        {
            "message": "Things feel a little challenging",
            "expected_priority": "none",
            "subcategory": "minor_challenge",
            "description": "Small challenges within normal range"
        },
        {
            "message": "I'm not feeling 100% today",
            "expected_priority": "none",
            "subcategory": "suboptimal_day",
            "description": "Not at peak but within normal range"
        },
        {
            "message": "I've been having minor issues",
            "expected_priority": "none",
            "subcategory": "minor_problems",
            "description": "Small, manageable problems"
        },
        {
            "message": "Things feel slightly difficult",
            "expected_priority": "none",
            "subcategory": "minimal_difficulty",
            "description": "Very mild difficulty"
        },
        {
            "message": "I'm feeling a bit under the weather",
            "expected_priority": "none",
            "subcategory": "mild_unwellness",
            "description": "Slight physical or emotional unwellness"
        },
        {
            "message": "I've had some small setbacks",
            "expected_priority": "none",
            "subcategory": "minor_setbacks",
            "description": "Small, temporary setbacks"
        },
        {
            "message": "Things feel somewhat stressful",
            "expected_priority": "none",
            "subcategory": "mild_stress",
            "description": "Low-level stress"
        },
        {
            "message": "I'm not feeling completely myself",
            "expected_priority": "none",
            "subcategory": "slight_off_feeling",
            "description": "Slightly different from usual self"
        },
        {
            "message": "I've been having little worries",
            "expected_priority": "none",
            "subcategory": "minor_worries",
            "description": "Small, manageable worries"
        },
        {
            "message": "Things feel mildly overwhelming",
            "expected_priority": "none",
            "subcategory": "minimal_overwhelm",
            "description": "Very slight overwhelm"
        },
        {
            "message": "I'm feeling a bit scattered",
            "expected_priority": "none",
            "subcategory": "mild_disorganization",
            "description": "Slight disorganization or scatteredness"
        },
        {
            "message": "I've had some minor concerns",
            "expected_priority": "none",
            "subcategory": "small_concerns",
            "description": "Minor, manageable concerns"
        },
        {
            "message": "Things feel slightly off",
            "expected_priority": "none",
            "subcategory": "slight_anomaly",
            "description": "Something feels slightly unusual"
        },
        {
            "message": "I'm not feeling perfectly content",
            "expected_priority": "none",
            "subcategory": "mild_discontent",
            "description": "Slight dissatisfaction with current state"
        },
        {
            "message": "I've been having small troubles",
            "expected_priority": "none",
            "subcategory": "minor_troubles",
            "description": "Small, manageable troubles"
        },
        {
            "message": "Things feel a little uncertain",
            "expected_priority": "none",
            "subcategory": "mild_uncertainty",
            "description": "Slight uncertainty about future"
        },
        {
            "message": "I'm feeling somewhat distracted",
            "expected_priority": "none",
            "subcategory": "mild_distraction",
            "description": "Difficulty focusing, mild distraction"
        },
        {
            "message": "I've had some light difficulties",
            "expected_priority": "none",
            "subcategory": "light_problems",
            "description": "Very mild difficulties"
        },
        {
            "message": "Things feel moderately challenging",
            "expected_priority": "none",
            "subcategory": "moderate_challenge",
            "description": "Medium-level challenge within normal range"
        },
        {
            "message": "I'm not feeling entirely happy",
            "expected_priority": "none",
            "subcategory": "incomplete_happiness",
            "description": "Not completely happy but not distressed"
        },
        {
            "message": "I've been having casual concerns",
            "expected_priority": "none",
            "subcategory": "casual_worries",
            "description": "Light, non-urgent concerns"
        },
        {
            "message": "Things feel somewhat unsettled",
            "expected_priority": "none",
            "subcategory": "mild_unsettlement",
            "description": "Slight feeling of being unsettled"
        },
        {
            "message": "I'm feeling a bit restless",
            "expected_priority": "none",
            "subcategory": "mild_restlessness",
            "description": "Slight restlessness or agitation"
        },
        {
            "message": "I've had some minor struggles",
            "expected_priority": "none",
            "subcategory": "small_struggles",
            "description": "Small, manageable struggles"
        },
        {
            "message": "Things feel slightly complicated",
            "expected_priority": "none",
            "subcategory": "mild_complexity",
            "description": "Slight increase in life complexity"
        },
        {
            "message": "I'm not feeling completely at ease",
            "expected_priority": "none",
            "subcategory": "mild_unease",
            "description": "Slight discomfort or unease"
        },
        {
            "message": "I've been having small challenges",
            "expected_priority": "none",
            "subcategory": "minor_challenges",
            "description": "Small challenges within normal range"
        },
        {
            "message": "Things feel a little heavy",
            "expected_priority": "none",
            "subcategory": "slight_weight",
            "description": "Mild emotional weight or burden"
        },
        {
            "message": "I'm feeling somewhat unsure",
            "expected_priority": "none",
            "subcategory": "mild_uncertainty",
            "description": "Slight uncertainty or doubt"
        },
        {
            "message": "I've had some brief moments of sadness",
            "expected_priority": "none",
            "subcategory": "temporary_sadness",
            "description": "Brief, passing moments of sadness"
        },
        {
            "message": "Things feel mildly difficult",
            "expected_priority": "none",
            "subcategory": "minimal_difficulty",
            "description": "Very mild difficulty level"
        },
        {
            "message": "I'm not feeling entirely positive",
            "expected_priority": "none",
            "subcategory": "reduced_positivity",
            "description": "Less positive than usual but not negative"
        },
        {
            "message": "I've been having minor emotional ups and downs",
            "expected_priority": "none",
            "subcategory": "normal_mood_variation",
            "description": "Normal emotional fluctuations"
        },
        {
            "message": "Things feel somewhat demanding",
            "expected_priority": "none",
            "subcategory": "mild_demands",
            "description": "Slightly increased life demands"
        },
        {
            "message": "I'm feeling a bit emotionally drained",
            "expected_priority": "none",
            "subcategory": "mild_emotional_fatigue",
            "description": "Slight emotional exhaustion"
        },
        {
            "message": "I've had some small disappointments",
            "expected_priority": "none",
            "subcategory": "minor_disappointments",
            "description": "Small, manageable disappointments"
        },
        {
            "message": "Things feel slightly burdensome",
            "expected_priority": "none",
            "subcategory": "mild_burden",
            "description": "Slight sense of burden"
        },
        {
            "message": "I'm not feeling completely satisfied",
            "expected_priority": "none",
            "subcategory": "mild_dissatisfaction",
            "description": "Slight dissatisfaction with current state"
        },
        {
            "message": "I've been having light stress",
            "expected_priority": "none",
            "subcategory": "minimal_stress",
            "description": "Very low level stress"
        },
        {
            "message": "Things feel a little discouraging",
            "expected_priority": "none",
            "subcategory": "mild_discouragement",
            "description": "Slight discouragement"
        },
        {
            "message": "I'm feeling somewhat uninspired",
            "expected_priority": "none",
            "subcategory": "mild_lack_inspiration",
            "description": "Reduced inspiration or motivation"
        },
        {
            "message": "I've had some minor frustrations",
            "expected_priority": "none",
            "subcategory": "small_frustrations",
            "description": "Small, manageable frustrations"
        },
        {
            "message": "Things feel slightly overwhelming at times",
            "expected_priority": "none",
            "subcategory": "occasional_mild_overwhelm",
            "description": "Occasional slight overwhelm"
        },
        {
            "message": "I'm not feeling entirely motivated",
            "expected_priority": "none",
            "subcategory": "reduced_motivation",
            "description": "Slightly lower motivation than usual"
        },
        {
            "message": "I've been having occasional doubts",
            "expected_priority": "none",
            "subcategory": "intermittent_doubt",
            "description": "Occasional, mild self-doubt"
        },
        {
            "message": "Things feel somewhat taxing",
            "expected_priority": "none",
            "subcategory": "mild_taxation",
            "description": "Slightly taxing or demanding"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "maybe_low_none",
    "description": "Maybe Low/None (Prevent False Positives)",
    "target_pass_rate": 90.0,
    "critical": True,
    "allow_escalation": True,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "minor_daily_issues": 12,
    "mild_emotional_states": 10,
    "normal_life_variation": 8,
    "slight_discomfort": 8,
    "minimal_stress": 6,
    "temporary_setbacks": 4,
    "reduced_positivity": 2
}