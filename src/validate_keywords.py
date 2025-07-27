#!/usr/bin/env python3
"""
Keyword Validation Script for Ash-Thrash

This script validates that our keyword structure matches Ash Bot's requirements
and tests the keyword detection logic.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("🔍 Validating Ash-Compatible Keywords")
    print("=" * 50)
    
    try:
        # Test keyword imports
        from src.keywords import (
            get_high_crisis_keywords, 
            get_medium_crisis_keywords, 
            get_low_crisis_keywords,
            get_all_keywords,
            get_keyword_counts,
            validate_keyword_structure
        )
        
        print("✅ Keyword imports successful")
        
        # Get keyword counts
        counts = get_keyword_counts()
        print(f"\n📊 Keyword Statistics:")
        print(f"   High Crisis: {counts['high_crisis']['total']} keywords")
        print(f"   Medium Crisis: {counts['medium_crisis']['total']} keywords")
        print(f"   Low Crisis: {counts['low_crisis']['total']} keywords")
        print(f"   Total Keywords: {counts['grand_total']} keywords")
        
        # Validate structure
        validation = validate_keyword_structure()
        print(f"\n🔍 Structure Validation:")
        
        if validation['valid']:
            print("   ✅ Keyword structure is valid")
            print(f"   📈 Level counts: {validation['level_counts']}")
        else:
            print("   ❌ Keyword structure has issues:")
            if validation['missing_levels']:
                print(f"      Missing levels: {validation['missing_levels']}")
            if validation['insufficient_counts']:
                for level, info in validation['insufficient_counts'].items():
                    print(f"      {level}: {info['actual']} keywords (need {info['expected']})")
        
        # Test keyword detection
        print(f"\n🧪 Testing Keyword Detection:")
        
        test_phrases = [
            ("I want to kill myself", "high"),
            ("Having a panic attack", "medium"), 
            ("Feeling really stressed", "low"),
            ("Going to the store", "none"),
            ("I want to end it all", "high"),
            ("Everything is falling apart", "medium"),
            ("Overwhelmed with work", "low")
        ]
        
        for phrase, expected in test_phrases:
            try:
                # Test individual keyword functions
                from src.keywords.high_crisis import check_high_crisis_match
                from src.keywords.medium_crisis import check_medium_crisis_match
                from src.keywords.low_crisis import check_low_crisis_match
                
                high_match = check_high_crisis_match(phrase)
                medium_match = check_medium_crisis_match(phrase)
                low_match = check_low_crisis_match(phrase)
                
                # Determine highest priority match (Ash's logic)
                if high_match['has_match']:
                    detected = 'high'
                elif medium_match['has_match']:
                    detected = 'medium'
                elif low_match['has_match']:
                    detected = 'low'
                else:
                    detected = 'none'
                
                status = "✅" if detected == expected else "❌"
                print(f"   {status} \"{phrase}\" → {detected} (expected {expected})")
                
                if detected != expected:
                    # Show what was matched
                    if high_match['has_match']:
                        print(f"      High matches: {[m['keyword'] for m in high_match['matches']]}")
                    if medium_match['has_match']:
                        print(f"      Medium matches: {[m['keyword'] for m in medium_match['matches']]}")
                    if low_match['has_match']:
                        print(f"      Low matches: {[m['keyword'] for m in low_match['matches']]}")
                
            except Exception as e:
                print(f"   ❌ \"{phrase}\" → Error: {e}")
        
        # Test Ash-compatible evaluation
        print(f"\n🎯 Testing Ash-Compatible Evaluation:")
        try:
            from src.utils.ash_compatible_evaluation import simulate_keyword_detection
            
            for phrase, expected in test_phrases:
                detected = simulate_keyword_detection(phrase)
                status = "✅" if detected == expected else "❌"
                print(f"   {status} \"{phrase}\" → {detected} (expected {expected})")
        
        except Exception as e:
            print(f"   ❌ Ash-compatible evaluation error: {e}")
        
        print(f"\n🏁 Validation Complete!")
        
        if validation['valid']:
            print("✅ Keywords ready for comprehensive testing!")
            return True
        else:
            print("❌ Fix keyword issues before running tests")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📝 Make sure keyword files are created in src/keywords/")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)