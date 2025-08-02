# Ash-Thrash v3.0 API Documentation

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**API Version**: v3.0  
**Document Location**: `docs/tech/api_v3_0.md`  
**Base URL**: `http://localhost:8884`  
**Last Updated**: August 2025

---

## 📋 API Overview

The Ash-Thrash v3.0 API provides comprehensive REST endpoints for crisis detection testing, result retrieval, and system monitoring. Built with FastAPI, it offers automatic OpenAPI documentation, real-time testing capabilities, and seamless integration with the ash ecosystem.

### Key Features
- **🧪 Test Execution**: Trigger comprehensive, quick, and category-specific tests
- **📊 Result Management**: Retrieve, store, and analyze test results
- **🔍 System Monitoring**: Health checks and performance metrics
- **🔗 Integration Ready**: Designed for ash-dash and external system integration
- **📝 Auto Documentation**: Interactive Swagger UI at `/docs`

---

## 🚀 Quick Start

### **Base Configuration**
```bash
# Default API server
BASE_URL=http://localhost:8884

# Production server  
BASE_URL=http://10.20.30.253:8884
```

### **Health Check**
```bash
curl http://localhost:8884/health
```

### **Interactive Documentation**
Visit `http://localhost:8884/docs` for Swagger UI with live testing capabilities.

---

## 🔗 Core Endpoints

### **Root Information**
```http
GET /
```

Returns basic API information and available endpoints.

**Response:**
```json
{
  "goals": {
    "definite_high": {
      "target_pass_rate": 100.0,
      "description": "High Priority Crisis (Safety First!)",
      "critical": true,
      "allow_escalation": false,
      "allow_descalation": false,
      "min_confidence": 0.8,
      "alert_on_failure": true
    },
    "definite_medium": {
      "target_pass_rate": 65.0,
      "description": "Medium Priority Crisis",
      "critical": false,
      "allow_escalation": false,
      "allow_descalation": false,
      "min_confidence": 0.5,
      "alert_on_failure": false
    }
  },
  "current_achievement": {
    "definite_high": {
      "current_pass_rate": 100.0,
      "goal_met": true,
      "last_updated": "2025-08-01T15:03:15Z"
    },
    "definite_medium": {
      "current_pass_rate": 62.0,
      "goal_met": false,
      "last_updated": "2025-08-01T15:03:15Z"
    }
  },
  "summary": {
    "total_categories": 7,
    "categories_meeting_goals": 5,
    "overall_achievement_rate": 71.4
  }
}
```

---

## 🔧 Error Handling

### **Standard Error Response Format**

```json
{
  "error": "Internal server error",
  "message": "Detailed error description",
  "path": "/api/test/trigger",
  "timestamp": "2025-08-01T15:00:00Z"
}
```

### **Common Error Codes**

| **HTTP Status** | **Error Type** | **Description** | **Resolution** |
|-----------------|----------------|----------------|----------------|
| `400` | Bad Request | Invalid test_type or parameters | Check valid test types and parameter format |
| `404` | Not Found | Test ID not found | Verify test ID exists and is spelled correctly |
| `202` | Accepted | Test still running | Wait for completion, check status endpoint |
| `500` | Internal Server Error | API server error | Check logs, verify NLP server connectivity |
| `503` | Service Unavailable | NLP server unreachable | Verify NLP server is running and accessible |

### **Error Examples**

#### **Invalid Test Type**
```http
POST /api/test/trigger
{
  "test_type": "invalid_type"
}
```

**Response (400):**
```json
{
  "detail": "Invalid test_type. Valid options: ['comprehensive', 'quick', 'category_definite_high', ...]"
}
```

#### **Test Not Found**
```http
GET /api/test/status/nonexistent_test
```

**Response (404):**
```json
{
  "detail": "Test not found"
}
```

#### **Test Still Running**
```http
GET /api/test/results/running_test_id
```

**Response (202):**
```json
{
  "detail": "Test still running"
}
```

---

## 🔗 Integration Examples

### **Python SDK Example**

```python
import requests
import time
from typing import Dict, Optional

class AshThrashClient:
    def __init__(self, base_url: str = "http://localhost:8884"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def trigger_test(self, test_type: str, triggered_by: str = "sdk", 
                    parameters: Optional[Dict] = None) -> Dict:
        """Trigger a new test"""
        payload = {
            "test_type": test_type,
            "triggered_by": triggered_by,
            "parameters": parameters or {}
        }
        
        response = self.session.post(f"{self.base_url}/api/test/trigger", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_test_status(self, test_id: str) -> Dict:
        """Get test status"""
        response = self.session.get(f"{self.base_url}/api/test/status/{test_id}")
        response.raise_for_status()
        return response.json()
    
    def get_test_results(self, test_id: str) -> Dict:
        """Get test results"""
        response = self.session.get(f"{self.base_url}/api/test/results/{test_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_test_completion(self, test_id: str, timeout: int = 300) -> Dict:
        """Wait for test to complete and return results"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_test_status(test_id)
            
            if status['status'] == 'completed':
                return self.get_test_results(test_id)
            elif status['status'] == 'failed':
                raise Exception(f"Test failed: {status.get('error', 'Unknown error')}")
            
            time.sleep(10)
        
        raise TimeoutError(f"Test {test_id} did not complete within {timeout} seconds")
    
    def run_comprehensive_test(self) -> Dict:
        """Run comprehensive test and wait for results"""
        trigger_response = self.trigger_test("comprehensive", "sdk_comprehensive")
        test_id = trigger_response['test_id']
        return self.wait_for_test_completion(test_id)

# Usage example
client = AshThrashClient()

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Run comprehensive test
results = client.run_comprehensive_test()
print(f"Pass Rate: {results['overall_pass_rate']:.1f}%")
```

### **JavaScript/Node.js Example**

```javascript
class AshThrashClient {
    constructor(baseUrl = 'http://localhost:8884') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) throw new Error(`Health check failed: ${response.status}`);
        return response.json();
    }
    
    async triggerTest(testType, triggeredBy = 'javascript', parameters = {}) {
        const response = await fetch(`${this.baseUrl}/api/test/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                test_type: testType,
                triggered_by: triggeredBy,
                parameters
            })
        });
        
        if (!response.ok) throw new Error(`Test trigger failed: ${response.status}`);
        return response.json();
    }
    
    async getTestStatus(testId) {
        const response = await fetch(`${this.baseUrl}/api/test/status/${testId}`);
        if (!response.ok) throw new Error(`Status check failed: ${response.status}`);
        return response.json();
    }
    
    async getTestResults(testId) {
        const response = await fetch(`${this.baseUrl}/api/test/results/${testId}`);
        if (!response.ok) throw new Error(`Results fetch failed: ${response.status}`);
        return response.json();
    }
    
    async waitForTestCompletion(testId, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const status = await this.getTestStatus(testId);
            
            if (status.status === 'completed') {
                return await this.getTestResults(testId);
            } else if (status.status === 'failed') {
                throw new Error(`Test failed: ${status.error || 'Unknown error'}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 10000));
        }
        
        throw new Error(`Test ${testId} did not complete within ${timeout}ms`);
    }
}

// Usage example
const client = new AshThrashClient();

async function runTest() {
    try {
        // Check health
        const health = await client.healthCheck();
        console.log(`API Status: ${health.status}`);
        
        // Trigger test
        const trigger = await client.triggerTest('quick');
        console.log(`Test triggered: ${trigger.test_id}`);
        
        // Wait for results
        const results = await client.waitForTestCompletion(trigger.test_id);
        console.log(`Pass Rate: ${results.overall_pass_rate.toFixed(1)}%`);
        
    } catch (error) {
        console.error('Test failed:', error.message);
    }
}

runTest();
```

### **cURL Examples**

#### **Comprehensive Test Workflow**
```bash
#!/bin/bash

# 1. Check API health
echo "Checking API health..."
curl -s http://localhost:8884/health | jq '.status'

# 2. Trigger comprehensive test
echo "Triggering comprehensive test..."
RESPONSE=$(curl -s -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "comprehensive", "triggered_by": "bash_script"}')

TEST_ID=$(echo $RESPONSE | jq -r '.test_id')
echo "Test ID: $TEST_ID"

# 3. Monitor progress
echo "Monitoring test progress..."
while true; do
    STATUS=$(curl -s http://localhost:8884/api/test/status/$TEST_ID | jq -r '.status')
    echo "Status: $STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "Test failed!"
        exit 1
    fi
    
    sleep 10
done

# 4. Get results
echo "Retrieving results..."
curl -s http://localhost:8884/api/test/results/$TEST_ID | jq '{
    test_id: .test_id,
    overall_pass_rate: .overall_pass_rate,
    goal_achievement_rate: .goal_achievement_rate,
    suggestions: .suggestions
}'
```

#### **Quick Category Test**
```bash
# Test specific category
curl -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "category_definite_high", "triggered_by": "manual_test"}' | jq '.'
```

#### **Health Monitoring Script**
```bash
#!/bin/bash

# Continuous health monitoring
while true; do
    HEALTH=$(curl -s http://localhost:8884/health)
    STATUS=$(echo $HEALTH | jq -r '.status')
    NLP_STATUS=$(echo $HEALTH | jq -r '.nlp_server_status')
    
    echo "$(date): API=$STATUS, NLP=$NLP_STATUS"
    
    if [ "$STATUS" != "healthy" ] || [ "$NLP_STATUS" != "healthy" ]; then
        echo "⚠️ System degraded - check logs"
    fi
    
    sleep 60
done
```

---

## 🔐 Authentication & Security

### **Current Security Model**

The v3.0 API currently operates with **no authentication** for development and internal use. This is suitable for:
- Internal team usage
- Docker network isolation
- Development environments

### **Production Security Considerations**

For production deployment, consider implementing:

#### **API Key Authentication**
```bash
# Example future implementation
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:8884/api/test/trigger
```

#### **Network Security**
- Deploy behind reverse proxy (nginx, traefik)
- Use Docker network isolation
- Implement rate limiting
- Enable HTTPS with proper certificates

#### **Access Control**
```yaml
# Example nginx configuration
location /api/ {
    allow 10.20.30.0/24;    # Internal network only
    deny all;
    proxy_pass http://ash-thrash-api:8884;
}
```

---

## 📈 Performance & Rate Limiting

### **Performance Characteristics**

| **Endpoint** | **Typical Response Time** | **Concurrent Requests** |
|-------------|---------------------------|------------------------|
| `/health` | <50ms | High (100+) |
| `/api/test/trigger` | <100ms | Medium (10) |
| `/api/test/status/*` | <50ms | High (50+) |
| `/api/test/results/*` | <200ms | Medium (20) |
| `/api/test/data` | <100ms | High (50+) |

### **Rate Limiting (Future Implementation)**

Planned rate limits for production:
- **General API**: 100 requests per minute per IP
- **Test Triggers**: 5 requests per minute per IP
- **Health Checks**: Unlimited

### **Performance Optimization**

#### **Client-Side Best Practices**
```python
# Use connection pooling
session = requests.Session()

# Implement client-side caching for static data
@functools.lru_cache(maxsize=1)
def get_test_data_info():
    return session.get(f"{base_url}/api/test/data").json()

# Use async for multiple requests
async def check_multiple_tests(test_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [get_test_status(session, test_id) for test_id in test_ids]
        return await asyncio.gather(*tasks)
```

#### **Server-Side Optimizations**
- Result caching for completed tests
- Background task processing for test execution
- Database connection pooling (when implemented)
- Async request handling with FastAPI

---

## 🔍 Monitoring & Observability

### **Health Monitoring Endpoints**

#### **Detailed Health Check**
```http
GET /health
```

Returns comprehensive health information including:
- API server status
- NLP server connectivity
- Test data validation status
- System uptime
- Resource usage (future)

#### **Service Dependencies**
```http
GET /api/test/data
```

Validates:
- Test phrase count and structure
- Category configuration
- NLP server URL configuration

### **Logging & Debugging**

#### **Log Levels**
- **ERROR**: Critical failures requiring immediate attention
- **WARNING**: Issues that may impact functionality
- **INFO**: Normal operational messages
- **DEBUG**: Detailed debugging information

#### **Key Log Events**
```
INFO: Test comprehensive_1693526400 started by api_user
INFO: Test comprehensive_1693526400 completed in 195.3s (87.4% pass rate)
ERROR: NLP server unreachable at http://10.20.30.253:8881
WARNING: Test definite_high failed 2/50 phrases - review thresholds
```

### **Metrics Collection**

Current metrics available:
- Test execution frequency
- Pass rates by category
- API response times
- NLP server connectivity status

Future metrics planned:
- Resource usage (CPU, memory)
- Request volume and patterns
- Error rates and types
- Test result trends over time

---

## 🚀 Future API Enhancements

### **Planned v3.1 Features**

#### **Enhanced Authentication**
```http
POST /auth/login
GET /auth/verify
POST /auth/refresh
```

#### **Advanced Test Configuration**
```http
POST /api/test/custom
{
  "phrases": ["custom phrase 1", "custom phrase 2"],
  "expected_category": "high",
  "test_name": "emergency_validation"
}
```

#### **Real-time Updates**
```http
GET /api/test/status/{test_id}/stream
# Server-Sent Events for real-time progress
```

#### **Batch Operations**
```http
POST /api/test/batch
{
  "tests": [
    {"test_type": "category_definite_high"},
    {"test_type": "category_definite_none"}
  ]
}
```

### **Integration Roadmap**

- **Webhook Support**: Configurable HTTP callbacks for test completion
- **GraphQL API**: Alternative query interface for complex data fetching
- **OpenAPI 3.1**: Enhanced schema documentation with examples
- **gRPC Support**: High-performance binary protocol for internal services

---

## 📞 API Support

### **Getting Help**

- **Interactive Documentation**: http://localhost:8884/docs
- **GitHub Issues**: [Report API bugs](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Discord Support**: [#ash-development channel](https://discord.gg/alphabetcartel)
- **Team Guide**: [Internal team documentation](../team/team_guide_v3_0.md)

### **API Changelog**

- **v3.0.0**: Initial API release with comprehensive testing endpoints
- **v3.0.1**: FastAPI lifespan events, improved error handling
- **v3.1.0**: Authentication and advanced features (planned)

---

## 🎯 Best Practices

### **Client Implementation**

1. **Always check health** before running tests
2. **Implement retry logic** for network failures
3. **Use connection pooling** for multiple requests
4. **Cache static data** (test data info, goals)
5. **Handle async operations** properly with status polling

### **Error Handling**

1. **Check HTTP status codes** before processing responses
2. **Implement exponential backoff** for retries
3. **Log API errors** with sufficient detail for debugging
4. **Gracefully handle test failures** vs API failures

### **Performance**

1. **Batch related requests** when possible
2. **Use appropriate timeouts** for long-running tests
3. **Monitor API response times** in production
4. **Implement client-side rate limiting** to avoid overwhelming the API

---

**The Ash-Thrash API v3.0 provides comprehensive testing capabilities with a focus on reliability, performance, and ease of integration. This API enables automated crisis detection validation and continuous improvement of mental health safety systems.**

**Base URL**: `http://localhost:8884`  
**Documentation**: `http://localhost:8884/docs`  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Accurate testing for safer communities.* 🔗🧪json
{
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
```

---

## 🏥 Health & Monitoring

### **Health Check**
```http
GET /health
```

Comprehensive system health check including NLP connectivity and test data validation.

**Response:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "nlp_server_status": "healthy",
  "nlp_server_url": "http://10.20.30.253:8881",
  "test_data_status": "valid",
  "total_phrases": 350,
  "uptime_seconds": 3600.5
}
```

**Status Values:**
- `healthy`: All systems operational
- `degraded`: Some issues detected but service functional
- `unhealthy`: Critical issues requiring attention

**Example Usage:**
```python
import requests

def check_api_health():
    response = requests.get('http://localhost:8884/health')
    health = response.json()
    
    if health['status'] == 'healthy':
        print("✅ API is healthy")
        print(f"NLP Server: {health['nlp_server_status']}")
        print(f"Test Data: {health['test_data_status']}")
        return True
    else:
        print(f"⚠️ API status: {health['status']}")
        return False
```

---

## 🧪 Test Management

### **Trigger Test**
```http
POST /api/test/trigger
```

Triggers a new test run with specified parameters.

**Request Body:**
```json
{
  "test_type": "comprehensive",
  "triggered_by": "api_user",
  "parameters": {
    "sample_size": 50,
    "custom_setting": "value"
  }
}
```

**Parameters:**
- `test_type` (string, required): Test type to run
  - `comprehensive`: All 350 phrases
  - `quick`: Quick validation subset
  - `category_definite_high`: Specific category test
  - `category_definite_medium`: Specific category test
  - `category_definite_low`: Specific category test
  - `category_definite_none`: Specific category test
  - `category_maybe_high_medium`: Specific category test
  - `category_maybe_medium_low`: Specific category test
  - `category_maybe_low_none`: Specific category test
- `triggered_by` (string, optional): Identifier for who/what triggered the test
- `parameters` (object, optional): Additional test parameters

**Response:**
```json
{
  "success": true,
  "message": "comprehensive test triggered successfully",
  "test_id": "comprehensive_1693526400",
  "estimated_duration_seconds": 180,
  "status_endpoint": "/api/test/status/comprehensive_1693526400"
}
```

**Example Usage:**
```python
import requests
import time

def trigger_and_wait_for_test(test_type="comprehensive"):
    # Trigger test
    response = requests.post('http://localhost:8884/api/test/trigger', json={
        'test_type': test_type,
        'triggered_by': 'python_script'
    })
    
    test_info = response.json()
    test_id = test_info['test_id']
    print(f"Test triggered: {test_id}")
    
    # Wait for completion
    while True:
        status_response = requests.get(f'http://localhost:8884/api/test/status/{test_id}')
        status = status_response.json()
        
        if status['status'] == 'completed':
            print("✅ Test completed!")
            break
        elif status['status'] == 'failed':
            print("❌ Test failed!")
            break
        else:
            print(f"⏳ Status: {status['status']}")
            time.sleep(10)
    
    # Get results
    results_response = requests.get(f'http://localhost:8884/api/test/results/{test_id}')
    return results_response.json()
```

### **Test Status**
```http
GET /api/test/status/{test_id}
```

Retrieves current status of a running or completed test.

**Response:**
```json
{
  "test_id": "comprehensive_1693526400",
  "status": "running",
  "progress": {
    "current_category": "definite_medium",
    "percent_complete": 45
  },
  "estimated_completion": "2025-08-01T15:30:00Z"
}
```

**Status Values:**
- `starting`: Test initialization
- `running`: Test in progress
- `completed`: Test finished successfully
- `failed`: Test encountered error

### **Test Results**
```http
GET /api/test/results/{test_id}
```

Retrieves complete results for a specific test.

**Response:**
```json
{
  "test_id": "comprehensive_1693526400",
  "test_type": "comprehensive",
  "started_at": "2025-08-01T15:00:00Z",
  "completed_at": "2025-08-01T15:03:15Z",
  "total_duration_seconds": 195.3,
  "overall_pass_rate": 87.4,
  "goal_achievement_rate": 71.4,
  "total_tests": 350,
  "total_passed": 306,
  "total_failed": 44,
  "category_results": {
    "definite_high": {
      "category_name": "definite_high",
      "target_pass_rate": 100.0,
      "total_tests": 50,
      "passed_tests": 50,
      "failed_tests": 0,
      "pass_rate": 100.0,
      "goal_met": true,
      "avg_confidence": 0.89,
      "avg_processing_time": 25.4,
      "failed_phrases": []
    }
  },
  "suggestions": [
    "🚨 HIGH PRIORITY: definite_none only 88.0% (need 95.0%). Consider raising NLP_NONE_THRESHOLD from 0.3 to 0.4"
  ]
}
```

### **Latest Results**
```http
GET /api/test/latest
```

Retrieves the most recent test results.

**Response:** Same format as individual test results.

### **Test History**
```http
GET /api/test/history?limit=10
```

Retrieves recent test history.

**Query Parameters:**
- `limit` (integer, optional): Number of results to return (default: 10)

**Response:**
```json
{
  "history": [
    {
      "test_id": "comprehensive_1693526400",
      "test_type": "comprehensive", 
      "started_at": "2025-08-01T15:00:00Z",
      "completed_at": "2025-08-01T15:03:15Z",
      "overall_pass_rate": 87.4,
      "goal_achievement_rate": 71.4,
      "total_tests": 350,
      "total_duration_seconds": 195.3
    }
  ],
  "total_count": 25
}
```

---

## 📊 Data & Configuration

### **Test Data Information**
```http
GET /api/test/data
```

Retrieves information about test phrases and validation status.

**Response:**
```json
{
  "validation": {
    "total_phrases": 350,
    "expected_total": 350,
    "correct_total": true,
    "category_counts": {
      "definite_high": 50,
      "definite_medium": 50,
      "definite_low": 50,
      "definite_none": 50,
      "maybe_high_medium": 50,
      "maybe_medium_low": 50,
      "maybe_low_none": 50
    },
    "categories_with_50": 7,
    "all_categories_have_50": true
  },
  "categories": {
    "definite_high": {
      "display_name": "Definite High Crisis",
      "description": "Explicit suicidal ideation and immediate danger",
      "target_pass_rate": 100.0,
      "critical": true,
      "phrase_count": 50
    }
  },
  "phrase_counts": {
    "definite_high": 50,
    "total": 350
  },
  "nlp_server_url": "http://10.20.30.253:8881"
}
```

### **Testing Goals**
```http
GET /api/test/goals
```

Retrieves testing goals and current achievement status.

**Response:**
```