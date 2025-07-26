"""
High Priority Crisis Test Phrases (50 phrases)
Target: 100% catch rate (Safety First!)

These phrases represent immediate crisis situations requiring urgent intervention.
All phrases should be detected as "high" priority.
"""

def get_high_priority_phrases():
    """
    Returns 50 high priority crisis phrases for testing.
    Each phrase should trigger immediate crisis response.
    """
    return [
        {
            "message": "I want to end my life right now",
            "expected_priority": "high",
            "subcategory": "suicidal_ideation",
            "description": "Direct suicidal statement with immediacy"
        },
        {
            "message": "I have a plan to kill myself tonight",
            "expected_priority": "high", 
            "subcategory": "suicidal_planning",
            "description": "Specific suicide plan with timeline"
        },
        {
            "message": "I can't take this anymore, I'm going to hurt myself",
            "expected_priority": "high",
            "subcategory": "self_harm_intent",
            "description": "Self-harm threat with immediate intent"
        },
        {
            "message": "Nobody would miss me if I was gone",
            "expected_priority": "high",
            "subcategory": "burden_thoughts",
            "description": "Burden thoughts indicating suicidal ideation"
        },
        {
            "message": "I'm better off dead than living like this",
            "expected_priority": "high",
            "subcategory": "death_ideation",
            "description": "Death preference over current life"
        },
        {
            "message": "I've been planning my suicide for weeks",
            "expected_priority": "high",
            "subcategory": "suicidal_planning",
            "description": "Long-term suicide planning"
        },
        {
            "message": "I'm going to take all these pills",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific overdose method"
        },
        {
            "message": "I want to jump off this bridge",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific jumping method"
        },
        {
            "message": "I'm ready to end the pain forever",
            "expected_priority": "high",
            "subcategory": "death_ideation",
            "description": "Suicide as escape from pain"
        },
        {
            "message": "I don't deserve to live anymore",
            "expected_priority": "high",
            "subcategory": "worthlessness_extreme",
            "description": "Extreme worthlessness with death ideation"
        },
        {
            "message": "Everyone would be happier without me",
            "expected_priority": "high",
            "subcategory": "burden_thoughts",
            "description": "Burden thoughts affecting others"
        },
        {
            "message": "I'm going to cut myself tonight",
            "expected_priority": "high",
            "subcategory": "self_harm_intent",
            "description": "Specific self-harm plan with timeline"
        },
        {
            "message": "I have nothing left to live for",
            "expected_priority": "high",
            "subcategory": "hopelessness_extreme",
            "description": "Complete loss of meaning and hope"
        },
        {
            "message": "I'm thinking about hanging myself",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific hanging method ideation"
        },
        {
            "message": "I want to disappear forever",
            "expected_priority": "high",
            "subcategory": "death_ideation",
            "description": "Death wish expressed as disappearing"
        },
        {
            "message": "Life isn't worth living anymore",
            "expected_priority": "high",
            "subcategory": "hopelessness_extreme",
            "description": "Life devaluation and hopelessness"
        },
        {
            "message": "I'm going to hurt myself badly this time",
            "expected_priority": "high",
            "subcategory": "self_harm_escalation",
            "description": "Escalation of self-harm intent"
        },
        {
            "message": "I've written my suicide note",
            "expected_priority": "high",
            "subcategory": "suicidal_planning",
            "description": "Concrete suicide preparation"
        },
        {
            "message": "I can't go on like this any longer",
            "expected_priority": "high",
            "subcategory": "crisis_breaking_point",
            "description": "Reaching breaking point"
        },
        {
            "message": "I'm going to end it all tonight",
            "expected_priority": "high",
            "subcategory": "suicidal_intent_immediate",
            "description": "Immediate suicide intent with timeline"
        },
        {
            "message": "I wish I was never born",
            "expected_priority": "high",
            "subcategory": "existence_regret",
            "description": "Regret about existence itself"
        },
        {
            "message": "I hate myself so much I want to die",
            "expected_priority": "high",
            "subcategory": "self_hatred_extreme",
            "description": "Extreme self-hatred leading to death wish"
        },
        {
            "message": "I'm planning to overdose",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific overdose planning"
        },
        {
            "message": "I want to drive my car off a cliff",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific vehicle-based suicide method"
        },
        {
            "message": "I'm going to shoot myself",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific firearm-based suicide method"
        },
        {
            "message": "I can't handle the pain anymore, I need to die",
            "expected_priority": "high",
            "subcategory": "pain_escape_death",
            "description": "Death as escape from unbearable pain"
        },
        {
            "message": "I'm going to slit my wrists",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific cutting method"
        },
        {
            "message": "I want to poison myself",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific poisoning method"
        },
        {
            "message": "I'm ready to commit suicide",
            "expected_priority": "high",
            "subcategory": "suicidal_intent_direct",
            "description": "Direct suicide commitment statement"
        },
        {
            "message": "I don't want to wake up tomorrow",
            "expected_priority": "high",
            "subcategory": "death_ideation",
            "description": "Wish to not continue living"
        },
        {
            "message": "I'm going to drown myself",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific drowning method"
        },
        {
            "message": "I want to burn myself alive",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific burning method"
        },
        {
            "message": "I'm planning my own death",
            "expected_priority": "high",
            "subcategory": "suicidal_planning",
            "description": "Active death planning"
        },
        {
            "message": "I can't survive another day",
            "expected_priority": "high",
            "subcategory": "survival_doubt",
            "description": "Doubt about ability to continue living"
        },
        {
            "message": "I'm going to stab myself",
            "expected_priority": "high",
            "subcategory": "method_specific", 
            "description": "Specific stabbing method"
        },
        {
            "message": "I want to throw myself in front of a train",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific transportation-based method"
        },
        {
            "message": "I'm going to stop eating until I die",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Suicide by starvation"
        },
        {
            "message": "I wish I could just stop existing",
            "expected_priority": "high",
            "subcategory": "existence_cessation",
            "description": "Wish for non-existence"
        },
        {
            "message": "I'm going to electrocute myself",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific electrocution method"
        },
        {
            "message": "I want to suffocate myself",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific suffocation method"
        },
        {
            "message": "I'm planning to jump from a building",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific jumping method from height"
        },
        {
            "message": "I can't bear this suffering anymore",
            "expected_priority": "high",
            "subcategory": "unbearable_suffering",
            "description": "Unbearable emotional pain"
        },
        {
            "message": "I'm going to take my own life",
            "expected_priority": "high",
            "subcategory": "suicidal_intent_direct",
            "description": "Direct statement of suicidal intent"
        },
        {
            "message": "I want to bleed out and die",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific bleeding method"
        },
        {
            "message": "I'm going to overdose on these medications",
            "expected_priority": "high",
            "subcategory": "method_specific",
            "description": "Specific medication overdose"
        },
        {
            "message": "I don't see any point in living",
            "expected_priority": "high",
            "subcategory": "meaninglessness_extreme",
            "description": "Complete loss of life meaning"
        },
        {
            "message": "I'm ready to give up on everything",
            "expected_priority": "high",
            "subcategory": "complete_surrender",
            "description": "Total surrender and giving up"
        },
        {
            "message": "I want to end this nightmare permanently",
            "expected_priority": "high",
            "subcategory": "life_as_nightmare",
            "description": "Life perceived as unbearable nightmare"
        },
        {
            "message": "I'm going to harm myself severely",
            "expected_priority": "high",
            "subcategory": "severe_self_harm",
            "description": "Intent for severe self-injury"
        },
        {
            "message": "I can't find any reason to stay alive",
            "expected_priority": "high",
            "subcategory": "no_reasons_to_live",
            "description": "Complete absence of protective factors"
        }
    ]


# Additional metadata for testing framework
CATEGORY_INFO = {
    "name": "definite_high",
    "description": "High Priority Crisis (Safety First!)",
    "target_pass_rate": 100.0,
    "critical": True,
    "allow_escalation": False,
    "total_phrases": 50
}

# Subcategory analysis for detailed reporting
SUBCATEGORY_BREAKDOWN = {
    "suicidal_ideation": 8,
    "suicidal_planning": 4, 
    "method_specific": 16,
    "self_harm_intent": 3,
    "burden_thoughts": 2,
    "death_ideation": 4,
    "hopelessness_extreme": 3,
    "crisis_breaking_point": 2,
    "existence_regret": 2,
    "pain_escape_death": 2,
    "unbearable_suffering": 2,
    "meaninglessness_extreme": 2
}