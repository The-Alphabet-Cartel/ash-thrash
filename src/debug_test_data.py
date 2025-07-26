#!/usr/bin/env python3
"""
Debug script to check the test data format
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.test_data import get_all_test_phrases, get_category_info
    
    print("🔍 Debugging Test Data Format")
    print("=" * 40)
    
    all_phrases = get_all_test_phrases()
    category_info = get_category_info()
    
    print(f"Categories found: {list(all_phrases.keys())}")
    print()
    
    for category, phrases in all_phrases.items():
        print(f"📂 Category: {category}")
        print(f"   Count: {len(phrases)}")
        
        if phrases:
            first_phrase = phrases[0]
            print(f"   Type: {type(first_phrase)}")
            print(f"   Sample: {first_phrase}")
            
            if isinstance(first_phrase, dict):
                print(f"   Keys: {list(first_phrase.keys())}")
            
        print()
        
        # Just check first category for detailed debugging
        if category == "definite_high":
            print("   📝 First 3 phrases:")
            for i, phrase in enumerate(phrases[:3]):
                print(f"   {i+1}. {phrase}")
            print()
            break
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Using fallback data...")
    
    # Test with simple fallback
    test_phrases = {
        "definite_high": ["test phrase 1", "test phrase 2"]
    }
    
    print(f"Fallback data: {test_phrases}")

print("🔍 Debug complete")