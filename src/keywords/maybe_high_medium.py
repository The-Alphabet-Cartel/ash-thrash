"""
Maybe High/Medium Priority Test Phrases (50 phrases)
Target: 90% catch rate (Allow escalation to high, prevent de-escalation)

These phrases represent borderline cases between medium and high priority.
Should be detected as "medium" or "high" priority (escalation allowed).
De-escalation to "low" or "none" is considered failure.
"""

def get_maybe_high_medium_phrases():
    """
    Returns 50 maybe high/medium priority phrases for testing.
    Each phrase represents borderline crisis that could be medium or high.
    Escalation to high is acceptable, de-escalation to low/none is not.
    """
    return [
        {
            "message": "I don't think I can handle much more",
            "expected_priority": "medium",
            "subcategory": "overwhelm_threshold",
            "description": "Approaching emotional breaking point"
        },
        {
            "message": "Everything seems to be falling apart",
            "expected_priority": "medium",
            "subcategory": "life_deterioration",
            "description": "Sense of life circumstances collapsing"
        },
        {
            "message": "I feel like I'm at my breaking point",
            "expected_priority": "medium",
            "subcategory": "breaking_point",
            "description": "Near emotional breaking point"
        },
        {
            "message": "I'm not sure how much longer I can do this",
            "expected_priority": "medium",
            "subcategory": "endurance_doubt",
            "description": "Doubt about ability to continue"
        },
        {
            "message": "Things have been really difficult lately",
            "expected_priority": "medium",
            "subcategory": "persistent_difficulty",
            "description": "Ongoing challenging circumstances"
        },
        {
            "message": "I feel like I'm barely holding on",
            "expected_priority": "medium",
            "subcategory": "tenuous_coping",
            "description": "Minimal coping capacity remaining"
        },
        {
            "message": "I'm struggling more than usual",
            "expected_priority": "medium",
            "subcategory": "increased_struggle",
            "description": "Escalation of usual difficulties"
        },
        {
            "message": "Everything feels really hard right now",
            "expected_priority": "medium",
            "subcategory": "pervasive_difficulty",
            "description": "General sense of everything being difficult"
        },
        {
            "message": "I don't know if I can keep going",
            "expected_priority": "medium",
            "subcategory": "continuation_doubt",
            "description": "Uncertainty about ability to continue"
        },
        {
            "message": "I feel like I'm reaching my limit",
            "expected_priority": "medium",
            "subcategory": "limit_approaching",
            "description": "Approaching personal limits"
        },
        {
            "message": "I'm having a really tough time",
            "expected_priority": "medium",
            "subcategory": "severe_difficulty",
            "description": "Experiencing significant challenges"
        },
        {
            "message": "Everything seems overwhelming",
            "expected_priority": "medium",
            "subcategory": "general_overwhelm",
            "description": "Widespread feeling of being overwhelmed"
        },
        {
            "message": "I feel like I'm losing hope",
            "expected_priority": "medium",
            "subcategory": "hope_diminishing",
            "description": "Gradual loss of hope"
        },
        {
            "message": "I'm not doing well at all",
            "expected_priority": "medium",
            "subcategory": "poor_functioning",
            "description": "Significant functional impairment"
        },
        {
            "message": "I feel like giving up sometimes",
            "expected_priority": "medium",
            "subcategory": "surrender_thoughts",
            "description": "Occasional thoughts of giving up"
        },
        {
            "message": "Everything feels too much to handle",
            "expected_priority": "medium",
            "subcategory": "capacity_exceeded",
            "description": "Feeling exceeded by life demands"
        },
        {
            "message": "I'm struggling to cope with things",
            "expected_priority": "medium",
            "subcategory": "coping_failure",
            "description": "Difficulty managing life circumstances"
        },
        {
            "message": "I feel like I'm drowning",
            "expected_priority": "medium",
            "subcategory": "drowning_metaphor",
            "description": "Overwhelmed using drowning metaphor"
        },
        {
            "message": "I don't know what to do anymore",
            "expected_priority": "medium",
            "subcategory": "solution_exhaustion",
            "description": "Feeling out of options"
        },
        {
            "message": "I feel like everything is wrong",
            "expected_priority": "medium",
            "subcategory": "pervasive_wrongness",
            "description": "Sense that everything is problematic"
        },
        {
            "message": "I'm having a really hard time",
            "expected_priority": "medium",
            "subcategory": "significant_struggle",
            "description": "Experiencing considerable difficulty"
        },
        {
            "message": "I feel like I can't breathe",
            "expected_priority": "medium",
            "subcategory": "suffocation_feeling",
            "description": "Metaphorical or literal breathing difficulty"
        },
        {
            "message": "Everything feels impossible",
            "expected_priority": "medium",
            "subcategory": "impossibility_feeling",
            "description": "Sense that everything is insurmountable"
        },
        {
            "message": "I'm struggling to function",
            "expected_priority": "medium",
            "subcategory": "functional_struggle",
            "description": "Difficulty with basic functioning"
        },
        {
            "message": "I feel like I'm losing myself",
            "expected_priority": "medium",
            "subcategory": "identity_erosion",
            "description": "Sense of losing personal identity"
        },
        {
            "message": "I don't see how things can get better",
            "expected_priority": "medium",
            "subcategory": "improvement_doubt",
            "description": "Inability to envision improvement"
        },
        {
            "message": "I feel like I'm suffocating",
            "expected_priority": "medium",
            "subcategory": "suffocation_metaphor",
            "description": "Feeling of being suffocated by circumstances"
        },
        {
            "message": "Everything feels hopeless",
            "expected_priority": "medium",
            "subcategory": "pervasive_hopelessness",
            "description": "Widespread sense of hopelessness"
        },
        {
            "message": "I'm struggling to survive",
            "expected_priority": "medium",
            "subcategory": "survival_struggle",
            "description": "Difficulty with basic survival"
        },
        {
            "message": "I feel like I'm breaking",
            "expected_priority": "medium",
            "subcategory": "breaking_sensation",
            "description": "Sense of personal breaking point"
        },
        {
            "message": "I don't think I can take anymore",
            "expected_priority": "medium",
            "subcategory": "tolerance_limit",
            "description": "Reaching tolerance limits"
        },
        {
            "message": "I feel like I'm crashing",
            "expected_priority": "medium",
            "subcategory": "crash_metaphor",
            "description": "Sense of personal crash or collapse"
        },
        {
            "message": "Everything feels meaningless",
            "expected_priority": "medium",
            "subcategory": "meaninglessness",
            "description": "Loss of meaning in life"
        },
        {
            "message": "I'm struggling to exist",
            "expected_priority": "medium",
            "subcategory": "existence_struggle",
            "description": "Difficulty with basic existence"
        },
        {
            "message": "I feel like I'm fading away",
            "expected_priority": "medium",
            "subcategory": "fading_sensation",
            "description": "Sense of gradually disappearing"
        },
        {
            "message": "I don't know how to continue",
            "expected_priority": "medium",
            "subcategory": "continuation_confusion",
            "description": "Uncertainty about how to proceed"
        },
        {
            "message": "I feel like I'm collapsing",
            "expected_priority": "medium",
            "subcategory": "collapse_sensation",
            "description": "Sense of personal collapse"
        },
        {
            "message": "Everything feels unbearable",
            "expected_priority": "medium",
            "subcategory": "unbearable_feeling",
            "description": "Sense that everything is unbearable"
        },
        {
            "message": "I'm struggling to breathe",
            "expected_priority": "medium",
            "subcategory": "breathing_difficulty",
            "description": "Difficulty breathing (metaphorical or literal)"
        },
        {
            "message": "I feel like I'm disappearing",
            "expected_priority": "medium",
            "subcategory": "disappearing_sensation",
            "description": "Sense of gradually vanishing"
        },
        {
            "message": "I don't think I can survive this",
            "expected_priority": "medium",
            "subcategory": "survival_doubt",
            "description": "Doubt about ability to survive circumstances"
        },
        {
            "message": "I feel like I'm falling apart",
            "expected_priority": "medium",
            "subcategory": "disintegration",
            "description": "Sense of personal disintegration"
        },
        {
            "message": "Everything feels too painful",
            "expected_priority": "medium",
            "subcategory": "excessive_pain",
            "description": "Overwhelming emotional pain"
        },
        {
            "message": "I'm struggling to hold on",
            "expected_priority": "medium",
            "subcategory": "tenuous_grip",
            "description": "Difficulty maintaining stability"
        },
        {
            "message": "I feel like I'm losing everything",
            "expected_priority": "medium",
            "subcategory": "loss_sensation",
            "description": "Sense of losing everything important"
        },
        {
            "message": "I don't see any way out",
            "expected_priority": "medium",
            "subcategory": "trapped_feeling",
            "description": "Feeling trapped with no solutions"
        },
        {
            "message": "I feel like I'm dying inside",
            "expected_priority": "medium",
            "subcategory": "internal_death",
            "description": "Sense of inner death or decay"
        },
        {
            "message": "Everything feels like too much",
            "expected_priority": "medium",
            "subcategory": "excessive_demands",
            "description": "Feeling that life demands are excessive"
        },
        {
            "message": "I'm struggling to stay afloat",
            "expected_priority": "medium",
            "subcategory": "sinking_metaphor",
            "description": "Using drowning metaphor for struggling"
        },
        {
            "message": "I feel like I'm completely lost",
            "expected_priority": "medium",
            "subcategory": "lost_sensation",
            "description": "Complete sense of being lost"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "maybe_high_medium",
    "description": "Maybe High/Medium (No Priority Drops)",
    "target_pass_rate": 90.0,
    "critical": False,
    "allow_escalation": True,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "overwhelm_threshold": 8,
    "breaking_point": 6,
    "coping_failure": 8,
    "drowning_metaphors": 4,
    "hopelessness_emerging": 6,
    "functional_struggle": 5,
    "existence_difficulty": 4,
    "collapse_sensations": 4,
    "survival_doubt": 3,
    "meaninglessness": 2
}