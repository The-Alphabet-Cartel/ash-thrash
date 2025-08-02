#!/usr/bin/env python3
"""
Test Data Module for Ash-Thrash v3.0
Contains all 350 test phrases organized by crisis category

Repository: https://github.com/the-alphabet-cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
Website: http://alphabetcartel.org
"""
import json
import os
from pathlib import Path

# Definite High Priority Crisis Phrases (50 phrases)
# Target: 100% detection rate - Safety Critical
DEFINITE_HIGH_PHRASES = [
    # Explicit suicidal ideation
    "I want to kill myself",
    "I'm going to end my life tonight", 
    "I can't take it anymore, goodbye everyone",
    "Planning to commit suicide",
    "I want to die right now",
    "I'm going to hurt myself badly",
    "Life isn't worth living anymore",
    "I have a suicide plan ready",
    "I want to end it all permanently",
    "Going to kill myself after this",
    
    # Immediate danger indicators
    "I have the pills ready",
    "Found the rope, it's time",
    "Loading the gun now",
    "This is my final message",
    "Goodbye cruel world",
    "Won't see tomorrow's sunrise",
    "Tonight's the night I die",
    "Can't wait to be dead",
    "Setting up to end everything",
    "Ready to jump off the bridge",
    
    # Active self-harm
    "Cutting myself deeper tonight",
    "Going to slice my wrists",
    "Need to hurt myself now",
    "Burning myself with cigarettes",
    "Punching walls until I bleed",
    "Making myself bleed everywhere",
    "Carving hate into my skin",
    "Hitting myself with a hammer",
    "Razor blade feels so good",
    "Fresh cuts across my arms",
    
    # Hopeless finality
    "There's absolutely no way out",
    "I'm beyond saving or help", 
    "Too broken to ever be fixed",
    "Born to suffer and die alone",
    "World is better without me",
    "Everyone would be happier dead",
    "No point in trying anymore",
    "Given up on life completely",
    "Past the point of no return",
    "Nothing can help me now",
    
    # Crisis continuation phrases
    "Already started taking the pills",
    "Rope is around my neck",
    "Standing on the ledge",
    "Gun is loaded and ready",
    "Final livestream before death",
    "Writing my suicide note",
    "Last video message ever",
    "Bleeding out slowly now",
    "Carbon monoxide is working",
    "This overdose should work"
]

# Definite Medium Priority Crisis Phrases (50 phrases)
# Target: 65% detection rate - Significant Mental Health Episodes
DEFINITE_MEDIUM_PHRASES = [
    # Severe emotional distress
    "Having a complete mental breakdown",
    "I'm falling apart completely",
    "Can't stop crying for hours",
    "Sobbing uncontrollably right now",
    "I'm an emotional wreck",
    "Lost and don't know what to do",
    "Everything in my life is crashing",
    "World is falling down around me",
    "Spiraling out of control badly",
    "At my absolute breaking point",
    
    # Clinical depression episodes
    "Severely depressed for weeks now",
    "Deep in a depression spiral",
    "Major depressive episode hitting",
    "Depression is back with vengeance",
    "Can't get out of bed anymore",
    "Lost all motivation to live",
    "Nothing brings me joy anymore",
    "Feel completely empty inside",
    "Emotionally numb to everything",
    "Life has zero meaning now",
    
    # Panic and anxiety attacks
    "Having a severe panic attack",
    "Anxiety attack won't stop",
    "Can't breathe properly anymore",
    "Heart racing out of control",
    "Chest feels incredibly tight",
    "Hyperventilating and dizzy",
    "Feel like I'm dying",
    "Think I'm having heart attack",
    "Shaking uncontrollably everywhere",
    "Nauseous and can't think",
    
    # Hopelessness and despair
    "Everything is completely pointless",
    "Why do I even bother existing",
    "Nothing I do matters anymore",
    "What's the point of anything",
    "Feel like giving up entirely",
    "Can't see any way forward",
    "Drowning in hopelessness",
    "Lost all hope for future",
    "Feel defeated by life",
    "Completely overwhelmed by existence",
    
    # Crisis escalation phrases
    "Don't know how much longer",
    "Getting closer to the edge",
    "Hanging on by a thread",
    "About to lose it completely",
    "Can't handle this much longer",
    "Ready to give up everything",
    "Losing my grip on reality",
    "Everything is falling apart",
    "On the verge of breakdown",
    "Cannot take another day"
]

# Definite Low Priority Crisis Phrases (50 phrases)
# Target: 65% detection rate - Mild to Moderate Distress
DEFINITE_LOW_PHRASES = [
    # Mild emotional distress
    "Having a really rough day",
    "Feeling pretty down lately",
    "Work is stressing me out",
    "I'm worried about my grades",
    "Feeling overwhelmed with tasks",
    "Been better honestly speaking",
    "Not my best week",
    "Struggling with some personal stuff",
    "Having some relationship issues",
    "Been feeling off lately",
    
    # General anxiety and worry
    "Anxious about job interview",
    "Stressed about upcoming deadline",
    "Worried about family finances",
    "Nervous about medical results",
    "Concerned about friend's health",
    "Feeling pressure from parents",
    "Anxious about moving apartments",
    "Worried about passing class",
    "Stressed about presentation tomorrow",
    "Nervous about first date",
    
    # Mild depression indicators
    "Feeling a bit depressed",
    "Kind of sad today",
    "Not feeling very motivated",
    "A little down in dumps",
    "Feeling somewhat hopeless",
    "Having a melancholy day",
    "Mood has been low",
    "Feeling discouraged lately",
    "Not very happy recently",
    "Spirits are pretty low",
    
    # Social and relationship stress
    "Friends are being difficult",
    "Family drama is exhausting",
    "Relationship is getting rocky",
    "Coworkers are driving crazy",
    "Social anxiety at parties",
    "Feeling left out lately",
    "Arguing with roommate constantly",
    "Boss is being unreasonable",
    "Feeling lonely at school",
    "Dating life is frustrating",
    
    # Life transition stress
    "Adjusting to college life",
    "New job is overwhelming",
    "Moving stress is real",
    "Adulting is really hard",
    "Changes are happening fast",
    "Uncertain about future plans",
    "Quarter life crisis maybe",
    "Growing up is scary",
    "Independence is challenging",
    "Life feels unpredictable"
]

# Definite None Priority Phrases (50 phrases)
# Target: 95% detection rate - Prevent False Positives
DEFINITE_NONE_PHRASES = [
    # Casual conversation
    "Going to the grocery store",
    "What's everyone having for dinner",
    "Nice weather we're having today",
    "See you all tomorrow morning",
    "Thanks for all the help",
    "How was everyone's day today",
    "What time is the meeting",
    "Really love this new song",
    "Great job on that project",
    "Happy Friday everyone here",
    
    # Gaming and entertainment
    "This boss fight is killing me",
    "Game is absolutely destroying me",
    "Movie was totally mind blowing",
    "Book ending made me cry",
    "Show finale was incredible",
    "Concert was absolutely amazing",
    "Art piece moved me deeply",
    "Performance was breathtaking",
    "Story was emotionally powerful",
    "Music video was stunning",
    
    # Positive expressions
    "Living my best life",
    "Feeling absolutely fantastic today",
    "Everything is going perfectly",
    "Life is treating well",
    "Couldn't be happier right",
    "On top of world",
    "Dreams are coming true",
    "Blessed beyond measure",
    "Grateful for everything",
    "Love conquers all",
    
    # Everyday activities
    "Making lunch for tomorrow",
    "Cleaning up the apartment",
    "Walking the dog outside",
    "Watching Netflix tonight",
    "Reading a good book",
    "Listening to music",
    "Working on homework assignment",
    "Planning weekend trip",
    "Shopping for new clothes",
    "Exercising at the gym",
    
    # Neutral observations
    "Traffic is heavy today",
    "Weather forecast looks interesting",
    "Stock market doing things",
    "News has been busy",
    "Technology keeps advancing",
    "Time flies by quickly",
    "Seasons are changing",
    "Life keeps moving forward",
    "World keeps spinning",
    "Universe is vast"
]

# Maybe High/Medium Priority Phrases (50 phrases)
# Target: 90% detection rate - Bidirectional Acceptable (high OR medium)
MAYBE_HIGH_MEDIUM_PHRASES = [
    "I don't know if I can keep going like this",
    "Everything in my life is falling apart completely",
    "I feel like giving up on everything", 
    "Nothing I do seems to matter anymore",
    "I'm so tired of trying all the time",
    "What's the point of continuing anymore",
    "I can't handle this level of pain",
    "I'm losing all hope for anything better",
    "Feel like I'm drowning in problems",
    "Can't see any way forward from here",
    
    "This pain is becoming unbearable",
    "I feel completely broken inside",
    "Everything feels so meaningless now",
    "I'm at the end of my rope",
    "Can't take much more of this",
    "Feeling like a complete failure",
    "World would be better without me",
    "I'm becoming a burden to everyone",
    "Nothing good ever happens to me",
    "I feel so alone in this world",
    
    "Life keeps beating me down",
    "I'm tired of feeling this way",
    "Everything I touch turns to shit",
    "Can't catch a break anywhere",
    "Feeling like I'm losing myself",
    "Don't know who I am anymore",
    "Feel like I'm going crazy",
    "Mind is playing tricks on me",
    "Reality doesn't feel real anymore",
    "Losing touch with everything",
    
    "I hate myself so much",
    "Wish I could just disappear",
    "Want to run away from everything",
    "Need to escape from this life",
    "Can't stand being me anymore",
    "Disgusted with who I've become",
    "Feel like a waste of space",
    "Don't deserve anything good",
    "I'm toxic to everyone around",
    "Better off not existing",
    
    "Why is life so unfair to me",
    "Can't seem to do anything right",
    "Every day is a struggle",
    "Fighting battles every single day", 
    "Exhausted from just existing",
    "Feel like I'm barely surviving",
    "Hanging on by thin thread",
    "One more thing might break me",
    "At my limit with everything",
    "Don't know how much longer"
]

# Maybe Medium/Low Priority Phrases (50 phrases)  
# Target: 80% detection rate - Bidirectional Acceptable (medium OR low)
MAYBE_MEDIUM_LOW_PHRASES = [
    "Things really aren't going well for me",
    "I'm struggling quite a bit right now",
    "Having a really hard time lately",
    "Feel pretty low today honestly",
    "Not doing great mentally speaking",
    "Been having some tough days",
    "Feeling pretty rough right now",
    "This situation is really difficult",
    "Going through some tough times",
    "Not feeling like myself lately",
    
    "Dealing with a lot of stress",
    "Overwhelmed by everything happening",
    "Pressure is getting to me",
    "Feeling burnt out from everything",
    "Struggling to keep up",
    "Hard to stay positive",
    "Feeling discouraged about things",
    "Life feels pretty heavy",
    "Carrying a lot right now",
    "Weight of world on shoulders",
    
    "Having some relationship problems",
    "Family situation is stressful",
    "Work has been really demanding",
    "School is overwhelming me",
    "Financial stress is real",
    "Health concerns are worrying",
    "Future feels uncertain",
    "Changes are hard to handle",
    "Transitions are difficult",
    "Adjustments taking time",
    
    "Feeling isolated from others",
    "Social situations feel hard",
    "Connection feels difficult",
    "Communication breaking down",
    "Misunderstood by people",
    "Feel like outsider",
    "Belonging somewhere is hard",
    "Support feels limited",
    "Help seems far away",
    "Understanding feels rare",
    
    "Motivation is really low",
    "Energy levels are down",
    "Interest in things fading",
    "Enjoyment feels less",
    "Engagement is dropping",
    "Enthusiasm is waning", 
    "Passion feels dimmed",
    "Excitement is rare",
    "Satisfaction feels empty",
    "Fulfillment seems distant"
]

# Maybe Low/None Priority Phrases (50 phrases)
# Target: 90% detection rate - Bidirectional Acceptable (low OR none)  
MAYBE_LOW_NONE_PHRASES = [
    "Could be doing better honestly",
    "Not bad but could be worse",
    "It's whatever I guess",
    "Meh okay I suppose",
    "Fine thanks for asking though",
    "Not complaining too much",
    "Same old same old really",
    "Getting by somehow",
    "Can't complain too much",
    "Doing alright I think",
    
    "Having an okay day",
    "Nothing special happening",
    "Pretty average day",
    "Normal kind of day",
    "Regular day for me",
    "Typical Monday vibes",
    "Standard week so far",
    "Ordinary times lately",
    "Routine day today",
    "Basic day overall",
    
    "Slightly tired today",
    "A bit worn out",
    "Somewhat drained lately",
    "Little low on energy",
    "Mildly exhausted",
    "Kinda sleepy right now",
    "Somewhat fatigued",
    "A tad weary",
    "Slightly worn down",
    "Bit rundown today",
    
    "Minor annoyances today",
    "Small frustrations lately",
    "Little things bothering me",
    "Tiny problems here there",
    "Minor inconveniences",
    "Small setbacks recently",
    "Little bumps in road",
    "Minor challenges",
    "Small obstacles",
    "Tiny hurdles",
    
    "Moderately concerned about exam",
    "Somewhat worried about meeting",
    "Slightly anxious about date",
    "Mildly stressed about deadline",
    "A bit nervous about interview",
    "Somewhat apprehensive about change",
    "Little worried about results",
    "Slightly uncertain about future",
    "Moderately concerned about health",
    "Somewhat unsure about decision"
]

def get_all_test_phrases():
    """
    Returns all 350 test phrases organized by category.
    """
    return {
        "definite_high": DEFINITE_HIGH_PHRASES,
        "definite_medium": DEFINITE_MEDIUM_PHRASES,
        "definite_low": DEFINITE_LOW_PHRASES,
        "definite_none": DEFINITE_NONE_PHRASES,
        "maybe_high_medium": MAYBE_HIGH_MEDIUM_PHRASES,
        "maybe_medium_low": MAYBE_MEDIUM_LOW_PHRASES,
        "maybe_low_none": MAYBE_LOW_NONE_PHRASES
    }

def load_testing_goals_from_json():
    """
    Load testing goals from config/testing_goals.json file.
    Falls back to hardcoded defaults if file doesn't exist.
    """
    try:
        # Try to find the JSON file relative to the project root
        current_dir = Path(__file__).parent
        config_file = current_dir.parent / "config" / "testing_goals.json"
        
        # Alternative path if running from different directory
        if not config_file.exists():
            config_file = Path("config/testing_goals.json")
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('goals', {})
        else:
            print(f"⚠️  Warning: Could not find testing_goals.json at {config_file}")
            print("⚠️  Using hardcoded defaults")
            return get_hardcoded_testing_goals()
            
    except Exception as e:
        print(f"⚠️  Error loading testing_goals.json: {e}")
        print("⚠️  Using hardcoded defaults")
        return get_hardcoded_testing_goals()

def get_hardcoded_testing_goals():
    """
    Fallback hardcoded testing goals if JSON file is unavailable.
    """
    return {
        "definite_high": {
            "target_pass_rate": 100.0,
            "description": "High Priority Crisis (Safety First!)",
            "critical": True,
            "allow_escalation": False,
            "allow_descalation": False,
            "min_confidence": 0.8,
            "alert_on_failure": True
        },
        "definite_medium": {
            "target_pass_rate": 65.0,
            "description": "Medium Priority Crisis",
            "critical": False,
            "allow_escalation": False,
            "allow_descalation": False,
            "min_confidence": 0.5,
            "alert_on_failure": False
        },
        "definite_low": {
            "target_pass_rate": 65.0,
            "description": "Low Priority Crisis",
            "critical": False,
            "allow_escalation": False,
            "allow_descalation": False,
            "min_confidence": 0.3,
            "alert_on_failure": False
        },
        "definite_none": {
            "target_pass_rate": 95.0,
            "description": "No Priority Crisis (Prevent False Positives)",
            "critical": True,
            "allow_escalation": False,
            "allow_descalation": False,
            "min_confidence": 0.0,
            "alert_on_failure": True
        },
        "maybe_high_medium": {
            "target_pass_rate": 90.0,
            "description": "Maybe High/Medium (Bidirectional Flexibility)",
            "critical": False,
            "allow_escalation": True,
            "allow_descalation": True,
            "acceptable_range": ["medium", "high"],
            "min_confidence": 0.4,
            "alert_on_failure": False
        },
        "maybe_medium_low": {
            "target_pass_rate": 80.0,
            "description": "Maybe Medium/Low (Bidirectional Flexibility)", 
            "critical": False,
            "allow_escalation": True,
            "allow_descalation": True,
            "acceptable_range": ["low", "medium"],
            "min_confidence": 0.3,
            "alert_on_failure": False
        },
        "maybe_low_none": {
            "target_pass_rate": 90.0,
            "description": "Maybe Low/None (Bidirectional Flexibility)",
            "critical": True,
            "allow_escalation": True,
            "allow_descalation": True,
            "acceptable_range": ["none", "low"],
            "min_confidence": 0.2,
            "alert_on_failure": False
        }
    }

def get_category_info():
    """
    Returns metadata about each testing category from JSON configuration.
    """
    json_goals = load_testing_goals_from_json()
    
    # Convert JSON format to the expected category_info format
    category_info = {}
    
    for category_name, config in json_goals.items():
        # Get phrase count dynamically
        phrase_count = len(globals().get(f"{category_name.upper()}_PHRASES", []))
        
        category_info[category_name] = {
            "display_name": config.get("description", category_name.replace("_", " ").title()),
            "description": config.get("description", ""),
            "target_pass_rate": config.get("target_pass_rate", 65.0),
            "critical": config.get("critical", False),
            "allow_escalation": config.get("allow_escalation", False),
            "allow_descalation": config.get("allow_descalation", False),
            "acceptable_range": config.get("acceptable_range", []),
            "min_confidence": config.get("min_confidence", 0.3),
            "alert_on_failure": config.get("alert_on_failure", False),
            "phrase_count": phrase_count
        }
    
    return category_info

def get_testing_goals():
    """
    Returns testing goals configuration from JSON file.
    This function now directly returns the loaded JSON configuration.
    """
    return load_testing_goals_from_json()

# Update the _determine_test_pass logic in ash_thrash_core.py as well
def enhanced_determine_test_pass(expected_category: str, detected_level: str, testing_goals: dict) -> bool:
    """
    Enhanced test pass logic that properly handles JSON configuration.
    This should replace the existing _determine_test_pass method.
    """
    goals = testing_goals.get(expected_category, {})
    
    # Check if acceptable_range is defined (handles all flexible scenarios)
    acceptable_range = goals.get('acceptable_range', [])
    if acceptable_range:
        return detected_level in acceptable_range
    
    # For categories without acceptable_range, check exact match
    return expected_category.split('_')[-1] == detected_level  # Extract level from category name

def get_phrase_count_summary():
    """
    Returns summary of phrase counts by category and total.
    """
    all_phrases = get_all_test_phrases()
    total = sum(len(phrases) for phrases in all_phrases.values())
    
    summary = {category: len(phrases) for category, phrases in all_phrases.items()}
    summary["total"] = total
    
    return summary

def validate_test_data():
    """
    Validates that we have exactly 350 phrases total with proper distribution.
    """
    counts = get_phrase_count_summary()
    
    validation = {
        "total_phrases": counts["total"],
        "expected_total": 350,
        "correct_total": counts["total"] == 350,
        "category_counts": {k: v for k, v in counts.items() if k != "total"},
        "categories_with_50": sum(1 for k, v in counts.items() if k != "total" and v == 50),
        "all_categories_have_50": all(v == 50 for k, v in counts.items() if k != "total")
    }
    
    return validation

if __name__ == "__main__":
    # Validate test data when run directly
    validation = validate_test_data()
    print("🧪 Ash-Thrash Test Data Validation")
    print("=" * 40)
    print(f"Total phrases: {validation['total_phrases']}")
    print(f"Expected: {validation['expected_total']}")
    print(f"✅ Correct total: {validation['correct_total']}")
    print(f"Categories with 50 phrases: {validation['categories_with_50']}/7")
    print(f"✅ All categories have 50: {validation['all_categories_have_50']}")
    
    if validation['correct_total'] and validation['all_categories_have_50']:
        print("\n🎉 Test data validation PASSED!")
    else:
        print(f"\n❌ Test data validation FAILED")
        print("Category breakdown:")
        for category, count in validation['category_counts'].items():
            print(f"  {category}: {count} phrases")