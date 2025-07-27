# 🔌 Ash-Thrash API Documentation

> **RESTful API for Crisis Detection Testing Operations**

**Base URL:** `http://10.20.30.16:8884`  
**API Version:** v2.1  
**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Discord:** https://discord.gg/alphabetcartel

---

## 📋 Overview

The Ash-Thrash API provides programmatic access to crisis detection testing operations, results retrieval, and system monitoring. It serves as the backbone for dashboard integration and automated testing workflows.

### API Features

- **RESTful Design** - Standard HTTP methods and status codes
- **JSON Responses** - All responses in JSON format
- **Real-time Status** - Live testing status and progress
- **Historical Data** - Access to past test results and trends
- **Health Monitoring** - System health and connectivity checks
- **Batch Operations** - Run comprehensive or targeted tests

---

## 🔐 Authentication

Currently, the Ash-Thrash API operates within a trusted network environment and does not require authentication. Access is restricted to the local network (10.20.30.0/24).

**Security Notes:**
- API accessible only from local network
- No external internet access required
- Consider implementing API keys for production deployments

---

## 📊 Base Endpoints

### Health Check

**Get API Health Status**

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-26T10:30:00Z",
  "version": "2.1.0",
  "services": {
    "api": "running",
    "nlp_server": "connected",
    "database": "available"
  },
  "uptime": "2d 14h 32m",
  "last_test": "2025-07-26T09:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Service healthy
- `503 Service Unavailable` - Service degraded or unavailable

---

## 🧪 Testing Endpoints

### Get Testing Status

**Retrieve Current Testing Status**

```http
GET /api/test/status
```

**Response:**
```json
{
  "status": "idle",
  "last_test": {
    "type": "comprehensive",
    "started_at": "2025-07-26T09:00:00Z",
    "completed_at": "2025-07-26T09:12:35Z",
    "duration": "12m 35s",
    "total_phrases": 350,
    "passed": 298,
    "failed": 52,
    "pass_rate": 85.1
  },
  "next_scheduled": {
    "comprehensive": "2025-07-26T15:00:00Z",
    "quick_validation": "2025-07-26T11:00:00Z"
  },
  "goals_status": {
    "goals_met": 6,
    "total_goals": 7,
    "achievement_rate": 85.7,
    "overall_status": "⚠️ 6/7 GOALS MET"
  }
}
```

**Possible Status Values:**
- `idle` - No active testing
- `running` - Test currently in progress
- `scheduled` - Test scheduled but not started
- `error` - Error in testing system

### Trigger Test Execution

**Start a New Test**

```http
POST /api/test/run
Content-Type: application/json
```

**Request Body:**
```json
{
  "test_type": "comprehensive",
  "priority": "high",
  "categories": ["definite_high", "definite_none"],
  "notify_on_completion": true,
  "include_detailed_results": true
}
```

**Parameters:**
- `test_type` (string): `"comprehensive"` (350 phrases) or `"quick"` (10 phrases)
- `priority` (string): `"high"`, `"normal"`, or `"low"`
- `categories` (array): Specific categories to test (optional)
- `notify_on_completion` (boolean): Send notification when done
- `include_detailed_results` (boolean): Include individual phrase results

**Response:**
```json
{
  "test_id": "test_20250726_103045",
  "status": "started",
  "estimated_duration": "12-15 minutes",
  "total_phrases": 350,
  "categories": [
    "definite_high",
    "definite_medium", 
    "definite_low",
    "definite_none",
    "maybe_high_medium",
    "maybe_medium_low",
    "maybe_low_none"
  ],
  "progress_url": "/api/test/progress/test_20250726_103045"
}
```

**Status Codes:**
- `202 Accepted` - Test started successfully
- `400 Bad Request` - Invalid request parameters
- `409 Conflict` - Test already running
- `503 Service Unavailable` - NLP server unavailable

### Get Test Progress

**Monitor Active Test Progress**

```http
GET /api/test/progress/{test_id}
```

**Response:**
```json
{
  "test_id": "test_20250726_103045",
  "status": "running",
  "progress": {
    "completed": 127,
    "total": 350,
    "percentage": 36.3,
    "current_category": "definite_medium",
    "estimated_remaining": "8m 45s"
  },
  "current_results": {
    "passed": 108,
    "failed": 19,
    "current_pass_rate": 85.0
  },
  "category_progress": {
    "definite_high": "completed",
    "definite_medium": "in_progress",
    "definite_low": "pending"
  }
}
```

### Stop Running Test

**Cancel Active Test**

```http
DELETE /api/test/stop/{test_id}
```

**Response:**
```json
{
  "test_id": "test_20250726_103045",
  "status": "cancelled",
  "completed_phrases": 127,
  "partial_results_available": true,
  "partial_results_url": "/api/test/results/test_20250726_103045"
}
```

---

## 📈 Results Endpoints

### Get Latest Results

**Retrieve Most Recent Test Results**

```http
GET /api/test/results/latest
```

**Query Parameters:**
- `test_type` (optional): Filter by `comprehensive` or `quick`
- `include_details` (optional): Include individual phrase results (`true`/`false`)

**Response:**
```json
{
  "test_id": "test_20250726_090000",
  "test_type": "comprehensive",
  "started_at": "2025-07-26T09:00:00Z",
  "completed_at": "2025-07-26T09:12:35Z",
  "duration": "12m 35s",
  "summary": {
    "total_phrases": 350,
    "passed": 298,
    "failed": 52,
    "pass_rate": 85.1,
    "avg_response_time": 1.34,
    "avg_confidence": 0.847
  },
  "goals_assessment": {
    "goals_met": 6,
    "total_goals": 7,
    "achievement_rate": 85.7,
    "critical_failures": 1
  },
  "category_results": {
    "definite_high": {
      "passed": 49,
      "total": 50,
      "pass_rate": 98.0,
      "target_rate": 100.0,
      "goal_met": false,
      "avg_confidence": 0.891,
      "avg_response_time": 1.12
    },
    "definite_none": {
      "passed": 48,
      "total": 50,
      "pass_rate": 96.0,
      "target_rate": 95.0,
      "goal_met": true,
      "avg_confidence": 0.923,
      "avg_response_time": 0.98
    }
  }
}
```

### Get Specific Test Results

**Retrieve Results for Specific Test**

```http
GET /api/test/results/{test_id}
```

**Query Parameters:**
- `include_failures` (optional): Include detailed failure information
- `format` (optional): Response format (`json`, `csv`, `html`)

**Response:** Same format as latest results, plus:
```json
{
  "detailed_failures": [
    {
      "phrase": "I can't handle this anymore",
      "category": "definite_high",
      "expected": "high",
      "detected": "medium",
      "confidence": 0.623,
      "response_time": 1.45,
      "failure_type": "priority_mismatch"
    }
  ]
}
```

### Get Historical Results

**Retrieve Historical Test Data**

```http
GET /api/test/results/history
```

**Query Parameters:**
- `days` (optional): Number of days to retrieve (default: 7, max: 365)
- `test_type` (optional): Filter by test type
- `include_trends` (optional): Include trend analysis
- `limit` (optional): Maximum number of results

**Response:**
```json
{
  "period": {
    "start": "2025-07-19T00:00:00Z",
    "end": "2025-07-26T23:59:59Z",
    "days": 7
  },
  "summary": {
    "total_tests": 28,
    "comprehensive_tests": 24,
    "quick_tests": 4,
    "avg_pass_rate": 87.3,
    "trend": "improving"
  },
  "trends": {
    "pass_rate": {
      "current": 87.3,
      "previous_period": 84.1,
      "change": "+3.2%",
      "direction": "improving"
    },
    "response_time": {
      "current": 1.34,
      "previous_period": 1.52,
      "change": "-0.18s",
      "direction": "improving"
    }
  },
  "results": [
    {
      "test_id": "test_20250726_090000",
      "timestamp": "2025-07-26T09:00:00Z",
      "test_type": "comprehensive",
      "pass_rate": 85.1,
      "duration": "12m 35s"
    }
  ]
}
```

### Download Results

**Download Test Results File**

```http
GET /api/test/results/download/{test_id}
```

**Query Parameters:**
- `format`: File format (`json`, `csv`, `xlsx`, `pdf`)
- `include_details`: Include individual phrase results

**Response:** Binary file download

**Content-Type Headers:**
- JSON: `application/json`
- CSV: `text/csv`
- Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- PDF: `application/pdf`

---

## 📊 Analytics Endpoints

### Get Performance Metrics

**Retrieve Performance Analytics**

```http
GET /api/analytics/performance
```

**Query Parameters:**
- `period` (optional): Time period (`day`, `week`, `month`, `quarter`)
- `category` (optional): Specific category to analyze
- `metric` (optional): Specific metric (`pass_rate`, `response_time`, `confidence`)

**Response:**
```json
{
  "period": "week",
  "metrics": {
    "pass_rate": {
      "current": 87.3,
      "previous": 84.1,
      "change": "+3.2%",
      "trend": "improving",
      "data_points": [
        {"date": "2025-07-20", "value": 84.1},
        {"date": "2025-07-21", "value": 85.2},
        {"date": "2025-07-22", "value": 86.7},
        {"date": "2025-07-23", "value": 87.1},
        {"date": "2025-07-24", "value": 88.3},
        {"date": "2025-07-25", "value": 87.9},
        {"date": "2025-07-26", "value": 87.3}
      ]
    },
    "response_time": {
      "current": 1.34,
      "previous": 1.52,
      "change": "-0.18s",
      "trend": "improving",
      "data_points": [
        {"date": "2025-07-20", "value": 1.52},
        {"date": "2025-07-26", "value": 1.34}
      ]
    }
  }
}
```

### Get Category Analysis

**Analyze Performance by Category**

```http
GET /api/analytics/categories
```

**Response:**
```json
{
  "analysis_date": "2025-07-26T10:30:00Z",
  "categories": {
    "definite_high": {
      "target_rate": 100.0,
      "current_rate": 98.0,
      "30_day_avg": 97.8,
      "trend": "stable",
      "goal_met": false,
      "critical": true,
      "recent_failures": 2,
      "common_failures": [
        "ambiguous severity phrases",
        "context-dependent statements"
      ]
    },
    "definite_none": {
      "target_rate": 95.0,
      "current_rate": 96.0,
      "30_day_avg": 95.4,
      "trend": "stable",
      "goal_met": true,
      "critical": true,
      "recent_failures": 1,
      "common_failures": [
        "sarcastic statements"
      ]
    }
  },
  "recommendations": [
    "Review definite_high failed phrases for pattern analysis",
    "Consider lowering detection threshold for high-priority phrases",
    "Excellent performance on false positive prevention"
  ]
}
```

### Get Failure Analysis

**Analyze Common Failure Patterns**

```http
GET /api/analytics/failures
```

**Query Parameters:**
- `days` (optional): Analysis period in days
- `category` (optional): Specific category to analyze
- `limit` (optional): Maximum failures to return

**Response:**
```json
{
  "analysis_period": "30 days",
  "total_failures": 156,
  "failure_patterns": [
    {
      "pattern": "context_ambiguity",
      "count": 45,
      "percentage": 28.8,
      "description": "Phrases with multiple possible interpretations",
      "examples": [
        "I can't deal with this",
        "This is too much for me"
      ],
      "recommendation": "Improve context analysis in NLP model"
    },
    {
      "pattern": "severity_borderline",
      "count": 32,
      "percentage": 20.5,
      "description": "Phrases on boundary between priority levels",
      "examples": [
        "I feel hopeless sometimes",
        "Life is getting harder"
      ],
      "recommendation": "Review and refine priority thresholds"
    }
  ],
  "by_category": {
    "definite_high": {
      "failures": 12,
      "most_common": "severity_underestimation"
    },
    "definite_none": {
      "failures": 8,
      "most_common": "false_positive_detection"
    }
  }
}
```

---

## ⚙️ Configuration Endpoints

### Get System Configuration

**Retrieve Current Configuration**

```http
GET /api/config
```

**Response:**
```json
{
  "testing": {
    "max_concurrent_tests": 8,
    "test_timeout_seconds": 15,
    "results_retention_days": 90
  },
  "nlp_server": {
    "host": "10.20.30.16",
    "port": 8881,
    "url": "http://10.20.30.16:8881",
    "connection_timeout": 10,
    "read_timeout": 30
  },
  "api": {
    "port": 8884,
    "host": "0.0.0.0",
    "debug": false
  },
  "scheduling": {
    "enabled": true,
    "comprehensive_schedule": "0 */6 * * *",
    "quick_validation_schedule": "0 * * * *"
  },
  "goals": {
    "definite_high": 100.0,
    "definite_medium": 65.0,
    "definite_low": 65.0,
    "definite_none": 95.0,
    "maybe_high_medium": 90.0,
    "maybe_medium_low": 80.0,
    "maybe_low_none": 90.0
  }
}
```

### Update Configuration

**Update System Configuration**

```http
PUT /api/config
Content-Type: application/json
```

**Request Body:**
```json
{
  "testing": {
    "max_concurrent_tests": 10,
    "test_timeout_seconds": 20
  },
  "goals": {
    "definite_high": 100.0,
    "definite_none": 95.0
  }
}
```

**Response:**
```json
{
  "status": "updated",
  "changes": [
    "max_concurrent_tests: 8 → 10",
    "test_timeout_seconds: 15 → 20"
  ],
  "restart_required": false
}
```

---

## 🔄 Integration Endpoints

### Dashboard Integration

**Get Dashboard Data**

```http
GET /api/dashboard/data
```

**Response:**
```json
{
  "status_summary": {
    "overall_status": "healthy",
    "current_pass_rate": 87.3,
    "goals_met": 6,
    "total_goals": 7,
    "last_test": "2 hours ago"
  },
  "recent_activity": [
    {
      "timestamp": "2025-07-26T09:00:00Z",
      "type": "comprehensive_test",
      "result": "completed",
      "pass_rate": 85.1
    }
  ],
  "performance_chart": {
    "labels": ["Jul 20", "Jul 21", "Jul 22", "Jul 23", "Jul 24", "Jul 25", "Jul 26"],
    "pass_rates": [84.1, 85.2, 86.7, 87.1, 88.3, 87.9, 87.3],
    "response_times": [1.52, 1.48, 1.41, 1.39, 1.35, 1.33, 1.34]
  },
  "alerts": [
    {
      "level": "warning",
      "message": "Definite high priority detection at 98% (target: 100%)",
      "timestamp": "2025-07-26T09:12:35Z"
    }
  ]
}
```

### Webhook Integration

**Register Webhook**

```http
POST /api/webhooks/register
Content-Type: application/json
```

**Request Body:**
```json
{
  "url": "https://your-service.com/webhook",
  "events": ["test_completed", "critical_failure", "goal_missed"],
  "secret": "your_webhook_secret",
  "name": "Production Monitoring"
}
```

**Response:**
```json
{
  "webhook_id": "webhook_123456",
  "status": "registered",
  "events": ["test_completed", "critical_failure", "goal_missed"],
  "test_url": "/api/webhooks/test/webhook_123456"
}
```

---

## 📝 Response Formats

### Standard Response Structure

All API responses follow this structure:

```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "2025-07-26T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Error Response Structure

```json
{
  "success": false,
  "error": {
    "code": "TEST_ALREADY_RUNNING",
    "message": "A test is already in progress",
    "details": {
      "current_test_id": "test_20250726_103045",
      "estimated_completion": "2025-07-26T10:45:00Z"
    }
  },
  "timestamp": "2025-07-26T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Status Codes

**Success Codes:**
- `200 OK` - Request successful
- `202 Accepted` - Request accepted, processing
- `204 No Content` - Success, no response body

**Client Error Codes:**
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., test already running)
- `422 Unprocessable Entity` - Valid request, invalid data

**Server Error Codes:**
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable
- `504 Gateway Timeout` - NLP server timeout

---

## 🔧 SDK and Integration Examples

### Python SDK Example

```python
import requests
import json

class AshThrashAPI:
    def __init__(self, base_url="http://10.20.30.16:8884"):
        self.base_url = base_url
    
    def get_status(self):
        response = requests.get(f"{self.base_url}/api/test/status")
        return response.json()
    
    def run_comprehensive_test(self):
        data = {"test_type": "comprehensive", "priority": "high"}
        response = requests.post(
            f"{self.base_url}/api/test/run",
            json=data
        )
        return response.json()
    
    def get_latest_results(self):
        response = requests.get(f"{self.base_url}/api/test/results/latest")
        return response.json()

# Usage
api = AshThrashAPI()
status = api.get_status()
print(f"System status: {status['status']}")

if status['status'] == 'idle':
    test = api.run_comprehensive_test()
    print(f"Test started: {test['test_id']}")
```

### PowerShell Integration

```powershell
# PowerShell integration script
$apiBase = "http://10.20.30.16:8884"

# Get current status
function Get-AshThrashStatus {
    $response = Invoke-RestMethod -Uri "$apiBase/api/test/status" -Method GET
    return $response
}

# Run comprehensive test
function Start-ComprehensiveTest {
    $body = @{
        test_type = "comprehensive"
        priority = "high"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$apiBase/api/test/run" -Method POST -Body $body -ContentType "application/json"
    return $response
}

# Usage
$status = Get-AshThrashStatus
Write-Host "Current status: $($status.status)"

if ($status.status -eq "idle") {
    $test = Start-ComprehensiveTest
    Write-Host "Test started: $($test.test_id)"
}
```

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

class AshThrashAPI {
    constructor(baseUrl = 'http://10.20.30.16:8884') {
        this.baseUrl = baseUrl;
        this.client = axios.create({ baseURL: baseUrl });
    }
    
    async getStatus() {
        const response = await this.client.get('/api/test/status');
        return response.data;
    }
    
    async runComprehensiveTest() {
        const data = { test_type: 'comprehensive', priority: 'high' };
        const response = await this.client.post('/api/test/run', data);
        return response.data;
    }
    
    async getLatestResults() {
        const response = await this.client.get('/api/test/results/latest');
        return response.data;
    }
}

// Usage
const api = new AshThrashAPI();

async function checkAndTest() {
    const status = await api.getStatus();
    console.log(`System status: ${status.status}`);
    
    if (status.status === 'idle') {
        const test = await api.runComprehensiveTest();
        console.log(`Test started: ${test.test_id}`);
    }
}

checkAndTest().catch(console.error);
```

---

## 📚 Rate Limiting and Best Practices

### Rate Limits

**Current Limits:**
- **General API calls:** 100 requests per minute
- **Test execution:** 1 concurrent test at a time
- **Bulk downloads:** 5 requests per minute

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1690380000
```

### Best Practices

**Efficient API Usage:**
1. **Check status before starting tests** - Avoid conflicts
2. **Use webhooks for notifications** - Don't poll for completion
3. **Cache configuration data** - Config rarely changes
4. **Implement exponential backoff** - Handle temporary failures gracefully

**Error Handling:**
```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
```

---

## 📞 Support and Resources

### API Support

**Documentation Updates:**
- API documentation is updated with each release
- Check GitHub repository for latest changes
- Breaking changes will be announced in Discord

**Getting Help:**
- **GitHub Issues:** Technical problems and feature requests
- **Discord:** Real-time support and community help
- **Email:** Direct contact for urgent API issues

### Related Resources

- **Main Documentation:** README.md and team guides
- **OpenAPI Specification:** Available at `/api/docs`
- **Postman Collection:** Available in repository
- **SDK Examples:** See `/examples` directory

---

*Built with 🖤 for The Alphabet Cartel community*

**API Documentation v2.1**  
Last updated: July 26, 2025