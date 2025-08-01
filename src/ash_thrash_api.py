#!/usr/bin/env python3
"""
Ash-Thrash REST API Server v3.0
API service for triggering tests and retrieving results

Repository: https://github.com/the-alphabet-cartel/ash-thrash
Discord: https://discord.gg/alphabetcartel
Website: http://alphabetcartel.org

Runs on port 8884
"""

import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our core testing engine
from src.ash_thrash_core import AshThrashTester, ComprehensiveTestResults
from src.test_data import get_phrase_count_summary, validate_test_data, get_category_info

# Pydantic models for API
class TriggerTestRequest(BaseModel):
    test_type: str = "comprehensive"  # comprehensive, quick, category_<name>
    triggered_by: str = "api"
    parameters: Optional[Dict] = None

class TestStatusResponse(BaseModel):
    test_id: str
    status: str  # running, completed, failed
    progress: Optional[Dict] = None
    estimated_completion: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    nlp_server_status: str
    nlp_server_url: str
    test_data_status: str
    total_phrases: int
    uptime_seconds: float

class TriggerResponse(BaseModel):
    success: bool
    message: str
    test_id: str
    estimated_duration_seconds: int
    status_endpoint: str

# Global variables for test tracking
running_tests: Dict[str, Dict] = {}
completed_tests: Dict[str, ComprehensiveTestResults] = {}
start_time = datetime.now(timezone.utc)

# Initialize FastAPI app
app = FastAPI(
    title="Ash-Thrash Testing API",
    description="Crisis Detection Testing Suite for Ash NLP System",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tester
tester = AshThrashTester()

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with basic info"""
    return {
        "service": "Ash-Thrash Testing API",
        "version": "3.0.0",
        "description": "Crisis Detection Testing Suite for The Alphabet Cartel",
        "endpoints": {
            "health": "GET /health",
            "trigger_test": "POST /api/test/trigger", 
            "test_status": "GET /api/test/status/{test_id}",
            "test_results": "GET /api/test/results/{test_id}",
            "latest_results": "GET /api/test/latest",
            "test_data_info": "GET /api/test/data",
            "goals": "GET /api/test/goals"
        },
        "links": {
            "discord": "https://discord.gg/alphabetcartel",
            "website": "http://alphabetcartel.org",
            "repository": "https://github.com/the-alphabet-cartel/ash-thrash"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check NLP server connectivity
    nlp_status = "unknown"
    try:
        from src.ash_thrash_core import NLPClient
        async with NLPClient(tester.nlp_url, timeout=5) as client:
            if await client.health_check():
                nlp_status = "healthy"
            else:
                nlp_status = "unhealthy"
    except Exception:
        nlp_status = "unreachable"
    
    # Validate test data
    validation = validate_test_data()
    test_data_status = "valid" if validation["correct_total"] and validation["all_categories_have_50"] else "invalid"
    
    # Calculate uptime
    uptime = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    return HealthResponse(
        status="healthy" if nlp_status == "healthy" and test_data_status == "valid" else "degraded",
        version="3.0.0",
        nlp_server_status=nlp_status,
        nlp_server_url=tester.nlp_url,
        test_data_status=test_data_status,
        total_phrases=validation["total_phrases"],
        uptime_seconds=uptime
    )

@app.post("/api/test/trigger", response_model=TriggerResponse)
async def trigger_test(request: TriggerTestRequest, background_tasks: BackgroundTasks):
    """Trigger a new test run"""
    test_type = request.test_type.lower()
    
    # Validate test type
    valid_types = ["comprehensive", "quick"]
    category_types = [f"category_{cat}" for cat in get_category_info().keys()]
    
    if test_type not in valid_types and test_type not in category_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid test_type. Valid options: {valid_types + category_types}"
        )
    
    # Generate test ID
    test_id = f"{test_type}_{int(datetime.now(timestamp=timezone.utc).timestamp())}"
    
    # Estimate duration based on test type
    duration_estimates = {
        "comprehensive": 180,  # 3 minutes for 350 phrases
        "quick": 30,          # 30 seconds for subset
    }
    # Category-specific tests
    if test_type.startswith("category_"):
        duration_estimates[test_type] = 25  # ~25 seconds for 50 phrases
    
    estimated_duration = duration_estimates.get(test_type, 60)
    
    # Track running test
    running_tests[test_id] = {
        "test_id": test_id,
        "test_type": test_type,
        "status": "starting",
        "triggered_by": request.triggered_by,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "estimated_completion": datetime.now(timezone.utc).timestamp() + estimated_duration,
        "parameters": request.parameters or {}
    }
    
    # Start test in background
    background_tasks.add_task(run_test_background, test_id, test_type)
    
    return TriggerResponse(
        success=True,
        message=f"{test_type} test triggered successfully",
        test_id=test_id,
        estimated_duration_seconds=estimated_duration,
        status_endpoint=f"/api/test/status/{test_id}"
    )

async def run_test_background(test_id: str, test_type: str):
    """Run test in background and store results"""
    try:
        # Update status to running
        running_tests[test_id]["status"] = "running"
        running_tests[test_id]["progress"] = {"current_category": "initializing", "percent_complete": 0}
        
        # Run the appropriate test
        if test_type == "comprehensive":
            results = await tester.run_comprehensive_test()
        elif test_type == "quick":
            results = await tester.run_quick_validation()
        elif test_type.startswith("category_"):
            category_name = test_type.replace("category_", "")
            results = await tester.run_category_specific_test(category_name)
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        # Update test ID to match our API ID
        results.test_id = test_id
        
        # Store completed results
        completed_tests[test_id] = results
        
        # Update running test status
        running_tests[test_id]["status"] = "completed"
        running_tests[test_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        running_tests[test_id]["progress"] = {"percent_complete": 100}
        
        # Save results to file
        await save_test_results(results)
        
        # Trigger Discord webhook if configured
        await send_discord_notification(results)
        
    except Exception as e:
        # Mark test as failed
        running_tests[test_id]["status"] = "failed"
        running_tests[test_id]["error"] = str(e)
        running_tests[test_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

@app.get("/api/test/status/{test_id}", response_model=TestStatusResponse)
async def get_test_status(test_id: str):
    """Get status of a running or completed test"""
    if test_id in running_tests:
        test_info = running_tests[test_id]
        
        # Calculate estimated completion if still running
        estimated_completion = None
        if test_info["status"] == "running":
            estimated_completion = datetime.fromtimestamp(
                test_info["estimated_completion"], tz=timezone.utc
            ).isoformat()
        
        return TestStatusResponse(
            test_id=test_id,
            status=test_info["status"],
            progress=test_info.get("progress"),
            estimated_completion=estimated_completion
        )
    else:
        raise HTTPException(status_code=404, detail="Test not found")

@app.get("/api/test/results/{test_id}")
async def get_test_results(test_id: str):
    """Get complete results for a specific test"""
    if test_id in completed_tests:
        results = completed_tests[test_id]
        return json.loads(json.dumps(results, default=str))  # Convert dataclass to dict
    elif test_id in running_tests and running_tests[test_id]["status"] != "completed":
        raise HTTPException(status_code=202, detail="Test still running")
    else:
        # Try to load from file
        results_file = Path("results") / f"{test_id}_results.json"
        if results_file.exists():
            with open(results_file, 'r') as f:
                return json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Test results not found")

@app.get("/api/test/latest")
async def get_latest_results():
    """Get the most recent test results"""
    if not completed_tests:
        # Try to find latest file
        results_dir = Path("results")
        if results_dir.exists():
            json_files = list(results_dir.glob("*_results.json"))
            if json_files:
                latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    return json.load(f)
        
        raise HTTPException(status_code=404, detail="No test results available")
    
    # Return most recent completed test
    latest_test_id = max(completed_tests.keys(), key=lambda x: completed_tests[x].started_at)
    results = completed_tests[latest_test_id]
    return json.loads(json.dumps(results, default=str))

@app.get("/api/test/data")
async def get_test_data_info():
    """Get information about test data"""
    validation = validate_test_data()
    category_info = get_category_info()
    phrase_counts = get_phrase_count_summary()
    
    return {
        "validation": validation,
        "categories": category_info,
        "phrase_counts": phrase_counts,
        "nlp_server_url": tester.nlp_url
    }

@app.get("/api/test/goals")
async def get_testing_goals():
    """Get testing goals and current achievement status"""
    from src.test_data import get_testing_goals
    
    goals = get_testing_goals()
    
    # Try to get current achievement status from latest results
    current_achievement = {}
    if completed_tests:
        latest_test_id = max(completed_tests.keys(), key=lambda x: completed_tests[x].started_at)
        latest_results = completed_tests[latest_test_id]
        
        for category_name, category_result in latest_results.category_results.items():
            current_achievement[category_name] = {
                "current_pass_rate": category_result.pass_rate,
                "goal_met": category_result.goal_met,
                "last_updated": latest_results.completed_at
            }
    
    return {
        "goals": goals,
        "current_achievement": current_achievement,
        "summary": {
            "total_categories": len(goals),
            "categories_meeting_goals": sum(1 for cat in current_achievement.values() if cat["goal_met"]),
            "overall_achievement_rate": (
                sum(1 for cat in current_achievement.values() if cat["goal_met"]) / len(goals) * 100
                if current_achievement else 0.0
            )
        }
    }

@app.get("/api/test/history")
async def get_test_history(limit: int = 10):
    """Get recent test history"""
    # Get completed tests
    history = []
    
    for test_id, results in list(completed_tests.items())[-limit:]:
        history.append({
            "test_id": test_id,
            "test_type": results.test_type,
            "started_at": results.started_at,
            "completed_at": results.completed_at,
            "overall_pass_rate": results.overall_pass_rate,
            "goal_achievement_rate": results.goal_achievement_rate,
            "total_tests": results.total_tests,
            "total_duration_seconds": results.total_duration_seconds
        })
    
    # Sort by start time (most recent first)
    history.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {"history": history, "total_count": len(completed_tests)}

async def save_test_results(results: ComprehensiveTestResults):
    """Save test results to file"""
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    results_file = results_dir / f"{results.test_id}_results.json"
    
    # Convert dataclass to dict for JSON serialization
    results_dict = json.loads(json.dumps(results, default=str))
    
    with open(results_file, 'w') as f:
        json.dump(results_dict, f, indent=2)

async def send_discord_notification(results: ComprehensiveTestResults):
    """Send Discord webhook notification for completed tests"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        return  # No webhook configured
    
    try:
        import aiohttp
        
        # Create Discord embed
        embed = {
            "title": f"🧪 Ash-Thrash Test Completed: {results.test_type.title()}",
            "description": f"Test ID: `{results.test_id}`",
            "color": 0x00ff00 if results.overall_pass_rate >= 85 else 0xff9900 if results.overall_pass_rate >= 70 else 0xff0000,
            "fields": [
                {
                    "name": "📊 Overall Results",
                    "value": f"**Pass Rate:** {results.overall_pass_rate:.1f}%\n**Goal Achievement:** {results.goal_achievement_rate:.1f}%\n**Duration:** {results.total_duration_seconds:.1f}s",
                    "inline": True
                },
                {
                    "name": "🎯 Test Details", 
                    "value": f"**Total Tests:** {results.total_tests}\n**Passed:** {results.total_passed}\n**Failed:** {results.total_failed}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Ash-Thrash Testing Suite | The Alphabet Cartel",
                "icon_url": "https://alphabetcartel.org/favicon.ico"
            },
            "timestamp": results.completed_at
        }
        
        # Add category breakdown for comprehensive tests
        if results.test_type == "comprehensive" and len(results.category_results) > 1:
            category_summary = []
            for category, result in results.category_results.items():
                status = "✅" if result.goal_met else "❌"
                category_summary.append(f"{status} {category}: {result.pass_rate:.1f}%")
            
            embed["fields"].append({
                "name": "📋 Category Results",
                "value": "\n".join(category_summary[:10]),  # Limit to avoid Discord limits
                "inline": False
            })
        
        # Add suggestions if any
        if results.suggestions:
            suggestions_text = "\n".join(results.suggestions[:3])  # Limit to top 3
            embed["fields"].append({
                "name": "🔧 Tuning Suggestions",
                "value": suggestions_text,
                "inline": False
            })
        
        # Send webhook
        async with aiohttp.ClientSession() as session:
            webhook_payload = {
                "username": "Ash-Thrash",
                "embeds": [embed]
            }
            
            async with session.post(webhook_url, json=webhook_payload) as response:
                if response.status != 204:
                    print(f"⚠️ Discord webhook failed: {response.status}")
                else:
                    print("✅ Discord notification sent successfully")
                    
    except Exception as e:
        print(f"❌ Discord webhook error: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the API server"""
    print("🚀 Starting Ash-Thrash API Server")
    print("=" * 40)
    print(f"Version: 3.0.0")
    print(f"NLP Server: {tester.nlp_url}")
    print(f"Port: 8884")
    print(f"Discord: https://discord.gg/alphabetcartel")
    print(f"Website: http://alphabetcartel.org")
    
    # Validate test data on startup
    validation = validate_test_data()
    if validation["correct_total"] and validation["all_categories_have_50"]:
        print(f"✅ Test data validated: {validation['total_phrases']} phrases")
    else:
        print(f"❌ Test data validation failed: {validation['total_phrases']} phrases")
    
    # Test NLP connectivity
    try:
        from src.ash_thrash_core import NLPClient
        async with NLPClient(tester.nlp_url, timeout=5) as client:
            if await client.health_check():
                print("✅ NLP server connectivity verified")
            else:
                print("⚠️ NLP server health check failed")
    except Exception as e:
        print(f"❌ NLP server unreachable: {str(e)}")
    
    print("🎯 API server ready for testing!")

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url.path),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

def main():
    """Main function to run the API server"""
    # Environment configuration
    host = os.getenv('THRASH_API_HOST', '0.0.0.0')
    port = int(os.getenv('GLOBAL_THRASH_API_PORT', 8884))
    log_level = os.getenv('GLOBAL_LOG_LEVEL', 'info').lower()
    
    # Create results directory
    Path("results").mkdir(exist_ok=True)
    
    # Run server
    uvicorn.run(
        "src.ash_thrash_api:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False,  # Disable reload in production
        access_log=True
    )

if __name__ == "__main__":
    main()