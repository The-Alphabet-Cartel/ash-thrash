#!/usr/bin/env python3
"""
Debug script to see exactly what the NLP server returns.

This will help us understand the response format and fix ash-thrash accordingly.
"""

import os
import json
import requests
from datetime import datetime, timezone

def debug_nlp_response():
    """Debug what the NLP server actually returns."""
    nlp_url = os.getenv('NLP_SERVER_URL', 'http://10.20.30.253:8881')
    
    print("🔍 Debugging NLP Server Response Format")
    print("=" * 50)
    print(f"Server URL: {nlp_url}")
    print()
    
    # Test phrase
    test_phrase = "I want to end it all"
    
    print(f"Testing phrase: '{test_phrase}'")
    print()
    
    try:
        # Test health endpoint first
        print("1. Testing /health endpoint:")
        health_response = requests.get(f"{nlp_url}/health", timeout=5)
        print(f"   Status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Response: {json.dumps(health_data, indent=2)}")
        else:
            print(f"   Error: {health_response.text}")
        
        print()
        
        # Test analyze endpoint
        print("2. Testing /analyze endpoint:")
        
        payload = {
            "message": test_phrase,
            "user_id": "debug_test_user",
            "channel_id": "debug_test_channel",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        analyze_response = requests.post(
            f"{nlp_url}/analyze",
            json=payload,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {analyze_response.status_code}")
        
        if analyze_response.status_code == 200:
            response_data = analyze_response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            # Analyze the response structure
            print()
            print("3. Response Analysis:")
            print(f"   Available fields: {list(response_data.keys())}")
            
            # Check for priority field
            if 'priority' in response_data:
                print(f"   ✅ Found 'priority' field: {response_data['priority']}")
            else:
                print("   ❌ No 'priority' field found")
            
            # Check for crisis_level field
            if 'crisis_level' in response_data:
                print(f"   ✅ Found 'crisis_level' field: {response_data['crisis_level']}")
            else:
                print("   ❌ No 'crisis_level' field found")
            
            # Check for other possible priority indicators
            possible_fields = ['level', 'severity', 'urgency', 'category', 'classification']
            for field in possible_fields:
                if field in response_data:
                    print(f"   ✅ Found '{field}' field: {response_data[field]}")
            
        else:
            print(f"   Error: {analyze_response.text}")
            
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
    
    print()
    print("4. Recommended Fix:")
    print("   Based on the response, update ash-thrash to use the correct field name.")

if __name__ == "__main__":
    debug_nlp_response()