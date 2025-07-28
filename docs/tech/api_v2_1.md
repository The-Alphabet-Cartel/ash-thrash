# Ash-Thrash API Documentation v2.1

**Complete REST API reference for the Ash-Thrash crisis detection testing suite.**

---

## 🎯 API Overview

### Base Configuration
- **Base URL:** `http://10.20.30.253:8884`
- **API Version:** v2.1
- **Protocol:** HTTP (internal network) / HTTPS (external access)
- **Authentication:** API Key (for administrative endpoints)
- **Content Type:** `application/json`
- **Rate Limiting:** 100 requests per minute per IP

### API Design Principles
- **RESTful Architecture:** Standard HTTP methods and status codes
- **JSON Communication:** All requests and responses use JSON format
- **Idempotent Operations:** Safe to retry GET, PUT, DELETE operations
- **Consistent Error Handling:** Standardized error response format
- **Comprehensive Monitoring:** All endpoints include performance metrics

---

## 🔐 Authentication

### API Key Authentication

**Administrative Endpoints Require Authentication:**
```bash
# Include API key in headers
curl -H "X-API-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     http://10.20.30.253:8884/api/admin/config
```

**Obtaining API Keys:**
```bash
# Generate new API key (requires admin access)
curl -X POST http://10.20.30.253:8884/api/admin/keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dashboard-integration",
    "permissions": ["read", "execute"],
    "expires_in_days": 365
  }'
```

**API Key Permissions:**
- **read:** Access to test results and system status
- **execute:** Permission to run tests and administrative commands
- **admin:** Full administrative access to configuration
- **monitor:** Health check and monitoring endpoints only

---

## 🏥 Health & Status Endpoints

### System Health

**GET /health**
```bash
curl http://10.20.30.253:8884/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-27T14:30:00Z",
  "version": "2.1.0",
  "uptime_seconds": 86400,
  "checks": {
    "api": "healthy",
    "database": "healthy",
    "nlp_server": "healthy",
    "redis": "healthy"
  }
}
```

**GET /api/health**
```bash
curl http://10.20.30.253:8884/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-27T14:30:00Z",
  "services": {
    "nlp_server": {
      "status": "healthy",
      "url": "http://10.20.30.253:8881",
      "response_time_ms": 45,
      "last_check": "2025-07-27T14:29:55Z"
    },
    "database": {
      "status": "healthy",
      "connection_pool": {
        "active": 3,
        "idle": 7,
        "max": 10
      },
      "last_check": "2025-07-27T14:29:58Z"
    },
    "redis": {
      "status": "healthy",
      "memory_usage": "45MB",
      "connected_clients": 2,
      "last_check": "2025-07-27T14:29:59Z"
    }
  },
  "performance": {
    "requests_per_minute": 12,
    "average_response_time_ms": 89,
    "error_rate_percent": 0.1
  }
}
```

### Service Status

**GET /api/status**
```bash
curl http://10.20.30.253:8884/api/status
```

**Response:**
```json
{
  "system": {
    "environment": "production",
    "version": "2.1.0",
    "build": "2025.07.27.001",
    "started_at": "2025-07-27T08:00:00Z"
  },
  "statistics": {
    "total_tests_executed": 1247,
    "tests_today": 15,
    "average_success_rate": 94.2,
    "last_comprehensive_test": "2025-07-27T02:00:00Z"
  },
  "configuration": {
    "test_categories": 7,
    "total_test_phrases": 350,
    "scheduled_tests_enabled": true,
    "backup_enabled": true
  }
}
```

---

## 🧪 Test Execution Endpoints

### Run Tests

**POST /api/test/quick**
*Execute quick validation test (10 phrases)*

```bash
curl -X POST http://10.20.30.253:8884/api/test/quick \
  -H "Content-Type: application/json" \
  -d '{
    "priority_filter": [1, 2],
    "include_metadata": true
  }'
```

**Request Body (Optional):**
```json
{
  "priority_filter": [1, 2, 3, 4, 5],
  "category_filter": ["immediate_crisis", "high_risk"],
  "include_metadata": true,
  "timeout_seconds": 60
}
```

**Response:**
```json
{
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "started_at": "2025-07-27T14:30:00Z",
  "completed_at": "2025-07-27T14:30:28Z",
  "execution_time_seconds": 28,
  "summary": {
    "total_phrases": 10,
    "successful_tests": 9,
    "failed_tests": 1,
    "success_rate": 90.0,
    "average_confidence": 0.87,
    "average_response_time_ms": 145
  },
  "results": [
    {
      "phrase_id": "immediate_001",
      "phrase_text": "I can't take this anymore, I'm done",
      "expected_category": "immediate_crisis",
      "expected_priority": 1,
      "detected_category": "immediate_crisis",
      "detected_priority": 1,
      "confidence_score": 0.95,
      "response_time_ms": 120,
      "success": true
    }
  ]
}
```

**POST /api/test/comprehensive**
*Execute comprehensive test suite (350 phrases)*

```bash
curl -X POST http://10.20.30.253:8884/api/test/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "include_detailed_results": false,
    "generate_report": true
  }'
```

**Request Body (Optional):**
```json
{
  "include_detailed_results": false,
  "generate_report": true,
  "email_report": "admin@alphabetcartel.org",
  "timeout_seconds": 600
}
```

**Response:**
```json
{
  "test_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "running",
  "started_at": "2025-07-27T14:30:00Z",
  "estimated_completion": "2025-07-27T14:38:00Z",
  "progress": {
    "phrases_completed": 0,
    "phrases_total": 350,
    "current_category": "immediate_crisis",
    "percent_complete": 0
  },
  "monitor_url": "/api/test/status/550e8400-e29b-41d4-a716-446655440001"
}
```

**POST /api/test/category**
*Execute tests for specific category*

```bash
curl -X POST http://10.20.30.253:8884/api/test/category \
  -H "Content-Type: application/json" \
  -d '{
    "category": "immediate_crisis",
    "phrase_count": 50
  }'
```

**Request Body:**
```json
{
  "category": "immediate_crisis",
  "phrase_count": 50,
  "randomize": true,
  "include_metadata": true
}
```

### Test Monitoring

**GET /api/test/status**
*Get current test execution status*

```bash
curl http://10.20.30.253:8884/api/test/status
```

**Response:**
```json
{
  "current_test": {
    "test_id": "550e8400-e29b-41d4-a716-446655440001",
    "test_type": "comprehensive",
    "status": "running",
    "started_at": "2025-07-27T14:30:00Z",
    "progress": {
      "phrases_completed": 45,
      "phrases_total": 350,
      "current_category": "high_risk",
      "percent_complete": 12.9,
      "estimated_time_remaining_seconds": 420
    }
  },
  "queue": [],
  "last_completed": {
    "test_id": "550e8400-e29b-41d4-a716-446655440000",
    "test_type": "quick",
    "completed_at": "2025-07-27T14:25:00Z",
    "success_rate": 90.0
  }
}
```

**GET /api/test/status/{test_id}**
*Get specific test execution status*

```bash
curl http://10.20.30.253:8884/api/test/status/550e8400-e29b-41d4-a716-446655440001
```

**Response:**
```json
{
  "test_id": "550e8400-e29b-41d4-a716-446655440001",
  "test_type": "comprehensive",
  "status": "running",
  "started_at": "2025-07-27T14:30:00Z",
  "progress": {
    "phrases_completed": 45,
    "phrases_total": 350,
    "current_category": "high_risk",
    "percent_complete": 12.9,
    "categories_completed": ["immediate_crisis"],
    "categories_remaining": ["high_risk", "medium_risk", "low_risk", "general_support", "false_positives", "community_specific"]
  },
  "performance": {
    "average_response_time_ms": 145,
    "success_rate_so_far": 91.1,
    "estimated_completion": "2025-07-27T14:38:00Z"
  }
}
```

---

## 📊 Results & Analytics Endpoints

### Test Results

**GET /api/test/results/latest**
*Get most recent test results*

```bash
curl http://10.20.30.253:8884/api/test/results/latest
```

**Response:**
```json
{
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "test_type": "comprehensive",
  "completed_at": "2025-07-27T02:15:34Z",
  "summary": {
    "total_phrases": 350,
    "successful_tests": 329,
    "failed_tests": 21,
    "success_rate": 94.0,
    "execution_time_seconds": 487
  },
  "category_performance": {
    "immediate_crisis": {
      "total": 50,
      "successful": 48,
      "success_rate": 96.0,
      "avg_confidence": 0.93
    },
    "high_risk": {
      "total": 50,
      "successful": 46,
      "success_rate": 92.0,
      "avg_confidence": 0.89
    },
    "false_positives": {
      "total": 50,
      "successful": 47,
      "success_rate": 94.0,
      "avg_confidence": 0.12
    }
  }
}
```

**GET /api/test/results/{test_id}**
*Get specific test results*

```bash
curl http://10.20.30.253:8884/api/test/results/550e8400-e29b-41d4-a716-446655440000?include_details=true
```

**Query Parameters:**
- `include_details=true` - Include individual phrase results
- `format=json|csv|xlsx` - Response format (default: json)
- `category_filter=category1,category2` - Filter by categories

**GET /api/test/history**
*Get historical test results*

```bash
curl "http://10.20.30.253:8884/api/test/history?limit=50&test_type=comprehensive&since=2025-07-20"
```

**Query Parameters:**
- `limit=50` - Number of results to return
- `test_type=quick|comprehensive|category` - Filter by test type  
- `since=2025-07-20` - Results since date (ISO format)
- `status=completed|failed|running` - Filter by status

**Response:**
```json
{
  "tests": [
    {
      "test_id": "550e8400-e29b-41d4-a716-446655440000",
      "test_type": "comprehensive", 
      "started_at": "2025-07-27T02:00:00Z",
      "completed_at": "2025-07-27T02:15:34Z",
      "status": "completed",
      "success_rate": 94.0,
      "execution_time_seconds": 487
    }
  ],
  "pagination": {
    "total": 247,
    "page": 1,
    "pages": 5,
    "limit": 50
  }
}
```

### Analytics

**GET /api/analytics/summary**
*Get performance analytics summary*

```bash
curl http://10.20.30.253:8884/api/analytics/summary?period=30d
```

**Query Parameters:**
- `period=7d|30d|90d|1y` - Analysis period

**Response:**
```json
{
  "period": "30d",
  "generated_at": "2025-07-27T14:30:00Z",
  "overall_performance": {
    "total_tests": 124,
    "average_success_rate": 93.8,
    "success_rate_trend": "+1.2%",
    "average_execution_time": 452,
    "execution_time_trend": "-5.3%"
  },
  "category_performance": {
    "immediate_crisis": {
      "success_rate": 95.8,
      "trend": "+0.8%",
      "total_tests": 1240
    },
    "false_positives": {
      "success_rate": 94.2,
      "trend": "+2.1%",
      "total_tests": 1240
    }
  },
  "system_health": {
    "uptime_percentage": 99.8,
    "average_response_time": 145,
    "error_rate": 0.2
  }
}
```

**GET /api/analytics/trends**
*Get performance trend data*

```bash
curl "http://10.20.30.253:8884/api/analytics/trends?metric=success_rate&period=30d&granularity=daily"
```

**Query Parameters:**
- `metric=success_rate|execution_time|error_rate` - Metric to analyze
- `period=7d|30d|90d` - Time period
- `granularity=hourly|daily|weekly` - Data granularity

**Response:**
```json
{
  "metric": "success_rate",
  "period": "30d",
  "granularity": "daily",
  "data_points": [
    {
      "date": "2025-07-01",
      "value": 92.5,
      "tests_count": 4
    },
    {
      "date": "2025-07-02", 
      "value": 94.1,
      "tests_count": 3
    }
  ],
  "statistics": {
    "mean": 93.8,
    "median": 94.0,
    "std_dev": 2.1,
    "min": 89.2,
    "max": 97.1
  }
}
```

**GET /api/analytics/failures**
*Get detailed failure analysis*

```bash
curl "http://10.20.30.253:8884/api/analytics/failures?period=7d&category=immediate_crisis"
```

**Response:**
```json
{
  "period": "7d",
  "total_failures": 23,
  "failure_rate": 6.2,
  "category_breakdown": {
    "immediate_crisis": {
      "failures": 8,
      "total_tests": 140,
      "failure_rate": 5.7
    }
  },
  "common_failure_patterns": [
    {
      "pattern": "Gaming context confusion",
      "frequency": 12,
      "example_phrases": ["This boss is killing me", "I'm dead from this level"]
    },
    {
      "pattern": "Metaphorical language",
      "frequency": 7,
      "example_phrases": ["I could die of embarrassment", "This waiting is torture"]
    }
  ],
  "improvement_recommendations": [
    "Add more gaming context training data",
    "Improve metaphorical language detection",
    "Enhance context window analysis"
  ]
}
```

---

## ⚙️ Configuration & Administration

### System Configuration

**GET /api/admin/config**
*Get current system configuration*

```bash
curl -H "X-API-Key: your-api-key" \
     http://10.20.30.253:8884/api/admin/config
```

**Response:**
```json
{
  "system": {
    "environment": "production",
    "debug_mode": false,
    "GLOBAL_LOG_LEVEL": "INFO"
  },
  "testing": {
    "default_timeout": 600,
    "max_concurrent_tests": 2,
    "scheduled_tests_enabled": true,
    "comprehensive_interval": "daily",
    "quick_interval": "hourly"
  },
  "nlp_server": {
    "url": "http://10.20.30.253:8881",
    "timeout": 30,
    "max_retries": 3,
    "health_check_interval": 60
  },
  "database": {
    "host": "ash-thrash-db",
    "port": 5432,
    "database": "ash_thrash_prod",
    "pool_size": 10
  },
  "storage": {
    "results_retention_days": 90,
    "backup_enabled": true,
    "backup_interval": "weekly"
  }
}
```

**PUT /api/admin/config**
*Update system configuration*

```bash
curl -X PUT http://10.20.30.253:8884/api/admin/config \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "testing": {
      "comprehensive_interval": "daily",
      "quick_interval": "30min"
    }
  }'
```

### Test Categories Management

**GET /api/admin/categories**
*Get test categories configuration*

```bash
curl -H "X-API-Key: your-api-key" \
     http://10.20.30.253:8884/api/admin/categories
```

**Response:**
```json
{
  "categories": [
    {
      "id": "immediate_crisis",
      "name": "Immediate Crisis",
      "description": "Active suicidal ideation requiring immediate intervention",
      "priority": 1,
      "target_success_rate": 95.0,
      "phrase_count": 50,
      "enabled": true
    },
    {
      "id": "false_positives", 
      "name": "False Positives",
      "description": "Phrases that should NOT trigger crisis alerts",
      "priority": 6,
      "target_success_rate": 95.0,
      "phrase_count": 50,
      "enabled": true
    }
  ]
}
```

**POST /api/admin/categories**
*Add new test category*

```bash
curl -X POST http://10.20.30.253:8884/api/admin/categories \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "gaming_specific",
    "name": "Gaming Context",
    "description": "Gaming-specific language patterns",
    "priority": 4,
    "target_success_rate": 85.0,
    "enabled": true
  }'
```

### Test Phrases Management

**GET /api/admin/phrases**
*Get test phrases*

```bash
curl "http://10.20.30.253:8884/api/admin/phrases?category=immediate_crisis&limit=10" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "phrases": [
    {
      "id": "immediate_001",
      "text": "I can't take this anymore, I'm done with everything",
      "category": "immediate_crisis",
      "priority": 1,
      "enabled": true,
      "created_at": "2025-07-01T00:00:00Z",
      "success_rate": 96.2
    }
  ],
  "total": 50,
  "category": "immediate_crisis"
}
```

**POST /api/admin/phrases**
*Add new test phrase*

```bash
curl -X POST http://10.20.30.253:8884/api/admin/phrases \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This situation feels hopeless and overwhelming",
    "category": "high_risk",
    "priority": 2,
    "metadata": {
      "source": "community_feedback",
      "date_added": "2025-07-27"
    }
  }'
```

---

## 📅 Scheduling & Automation

### Scheduled Tests

**GET /api/schedule**
*Get current test schedule*

```bash
curl http://10.20.30.253:8884/api/schedule
```

**Response:**
```json
{
  "scheduled_tests": [
    {
      "id": "comprehensive_daily",
      "test_type": "comprehensive",
      "schedule": "0 2 * * *",
      "timezone": "UTC",
      "enabled": true,
      "last_run": "2025-07-27T02:00:00Z",
      "next_run": "2025-07-28T02:00:00Z",
      "status": "active"
    },
    {
      "id": "quick_hourly",
      "test_type": "quick",
      "schedule": "0 * * * *",
      "timezone": "UTC", 
      "enabled": true,
      "last_run": "2025-07-27T14:00:00Z",
      "next_run": "2025-07-27T15:00:00Z",
      "status": "active"
    }
  ]
}
```

**POST /api/schedule**
*Create new scheduled test*

```bash
curl -X POST http://10.20.30.253:8884/api/schedule \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "weekend_comprehensive",
    "test_type": "comprehensive",
    "schedule": "0 10 * * 6,0",
    "timezone": "America/New_York",
    "enabled": true,
    "notification_channels": ["#tech-support"]
  }'
```

**PUT /api/schedule/{schedule_id}**
*Update scheduled test*

```bash
curl -X PUT http://10.20.30.253:8884/api/schedule/comprehensive_daily \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": "0 3 * * *",
    "enabled": false
  }'
```

### Automation Controls

**POST /api/automation/pause**
*Pause all automated testing*

```bash
curl -X POST http://10.20.30.253:8884/api/automation/pause \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "duration_hours": 2,
    "reason": "System maintenance"
  }'
```

**POST /api/automation/resume**
*Resume automated testing*

```bash
curl -X POST http://10.20.30.253:8884/api/automation/resume \
  -H "X-API-Key: your-api-key"
```

---

## 🔧 Maintenance & Utilities

### Database Operations

**POST /api/maintenance/cleanup**
*Clean up old test data*

```bash
curl -X POST http://10.20.30.253:8884/api/maintenance/cleanup \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "older_than_days": 90,
    "dry_run": false
  }'
```

**Response:**
```json
{
  "cleanup_id": "cleanup_2025_07_27_001",
  "started_at": "2025-07-27T14:30:00Z",
  "parameters": {
    "older_than_days": 90,
    "dry_run": false
  },
  "estimated_records": 1247,
  "status": "running"
}
```

**POST /api/maintenance/backup**
*Create system backup*

```bash
curl -X POST http://10.20.30.253:8884/api/maintenance/backup \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "include_test_data": true,
    "include_configuration": true,
    "compression": "gzip"
  }'
```

**POST /api/maintenance/optimize**
*Optimize database performance*

```bash
curl -X POST http://10.20.30.253:8884/api/maintenance/optimize \
  -H "X-API-Key: your-api-key"
```

### System Diagnostics

**GET /api/diagnostics**
*Run comprehensive system diagnostics*

```bash
curl http://10.20.30.253:8884/api/diagnostics
```

**Response:**
```json
{
  "timestamp": "2025-07-27T14:30:00Z",
  "overall_status": "healthy",
  "checks": {
    "api_server": {
      "status": "healthy",
      "response_time_ms": 12,
      "memory_usage_mb": 245,
      "cpu_usage_percent": 15.2
    },
    "database_connectivity": {
      "status": "healthy",
      "connection_time_ms": 8,
      "active_connections": 3,
      "query_performance": "optimal"
    },
    "nlp_server_connectivity": {
      "status": "healthy",
      "endpoint": "http://10.20.30.253:8881",
      "response_time_ms": 45,
      "last_successful_test": "2025-07-27T14:25:00Z"
    },
    "redis_connectivity": {
      "status": "healthy",
      "response_time_ms": 2,
      "memory_usage": "45MB",
      "key_count": 127
    },
    "disk_space": {
      "status": "healthy",
      "available_gb": 856,
      "used_percent": 12.4,
      "results_directory_mb": 2847
    },
    "test_data_integrity": {
      "status": "healthy",
      "total_phrases": 350,
      "categories_verified": 7,
      "last_validation": "2025-07-27T02:00:00Z"
    }
  },
  "recommendations": [
    "Consider archiving test results older than 6 months",
    "Update test phrases based on recent community language evolution"
  ]
}
```

**GET /api/diagnostics/performance**
*Get detailed performance metrics*

```bash
curl http://10.20.30.253:8884/api/diagnostics/performance
```

**Response:**
```json
{
  "timestamp": "2025-07-27T14:30:00Z",
  "api_performance": {
    "requests_per_minute": 12,
    "average_response_time_ms": 89,
    "95th_percentile_response_time_ms": 245,
    "error_rate_percent": 0.1,
    "slow_endpoints": []
  },
  "test_execution_performance": {
    "average_test_duration_seconds": {
      "quick": 28,
      "comprehensive": 487
    },
    "phrase_processing_rate": 0.72,
    "nlp_server_performance": {
      "average_response_time_ms": 145,
      "timeout_rate_percent": 0.0,
      "error_rate_percent": 0.2
    }
  },
  "resource_utilization": {
    "cpu_usage_percent": 15.2,
    "memory_usage_mb": 245,
    "disk_io_mb_per_second": 2.1,
    "network_throughput_mbps": 0.8
  }
}
```

---

## 📤 Data Export & Reporting

### Export Test Results

**GET /api/export/results**
*Export test results in various formats*

```bash
# Export as JSON
curl "http://10.20.30.253:8884/api/export/results?format=json&period=30d" \
  -H "X-API-Key: your-api-key"

# Export as CSV
curl "http://10.20.30.253:8884/api/export/results?format=csv&period=30d" \
  -H "X-API-Key: your-api-key" \
  -o test_results_30d.csv

# Export as Excel
curl "http://10.20.30.253:8884/api/export/results?format=xlsx&period=30d" \
  -H "X-API-Key: your-api-key" \
  -o test_results_30d.xlsx
```

**Query Parameters:**
- `format=json|csv|xlsx` - Export format
- `period=7d|30d|90d|all` - Time period
- `test_type=quick|comprehensive|category` - Filter by test type
- `include_details=true|false` - Include individual phrase results
- `category_filter=cat1,cat2` - Filter by categories

### Generate Reports

**POST /api/reports/performance**
*Generate performance report*

```bash
curl -X POST http://10.20.30.253:8884/api/reports/performance \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "period": "30d",
    "format": "pdf",
    "include_charts": true,
    "include_recommendations": true,
    "email_to": "admin@alphabetcartel.org"
  }'
```

**Response:**
```json
{
  "report_id": "perf_report_2025_07_27_001",
  "status": "generating",
  "estimated_completion": "2025-07-27T14:35:00Z",
  "download_url": "/api/reports/download/perf_report_2025_07_27_001",
  "parameters": {
    "period": "30d",
    "format": "pdf",
    "include_charts": true
  }
}
```

**GET /api/reports/download/{report_id}**
*Download generated report*

```bash
curl http://10.20.30.253:8884/api/reports/download/perf_report_2025_07_27_001 \
  -H "X-API-Key: your-api-key" \
  -o performance_report.pdf
```

---

## 🔔 Webhooks & Notifications

### Webhook Configuration

**GET /api/webhooks**
*Get configured webhooks*

```bash
curl http://10.20.30.253:8884/api/webhooks \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "webhooks": [
    {
      "id": "dashboard_integration",
      "url": "http://10.20.30.253:8883/api/ash-thrash/webhook",
      "events": ["test_completed", "test_failed", "system_alert"],
      "enabled": true,
      "secret": "webhook_secret_key",
      "last_success": "2025-07-27T14:25:00Z",
      "failure_count": 0
    },
    {
      "id": "discord_alerts",
      "url": "https://discord.com/api/webhooks/...",
      "events": ["system_alert", "test_failure"],
      "enabled": true,
      "last_success": "2025-07-27T13:45:00Z",
      "failure_count": 0
    }
  ]
}
```

**POST /api/webhooks**
*Create new webhook*

```bash
curl -X POST http://10.20.30.253:8884/api/webhooks \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "slack_integration",
    "url": "https://hooks.slack.com/services/...",
    "events": ["test_completed", "system_alert"],
    "secret": "slack_webhook_secret",
    "enabled": true
  }'
```

### Webhook Events

**Available Events:**
- `test_started` - Test execution begins
- `test_completed` - Test execution completes successfully
- `test_failed` - Test execution fails or times out
- `system_alert` - System health issues detected
- `performance_degradation` - Performance below thresholds
- `maintenance_required` - System maintenance needed

**Webhook Payload Example:**
```json
{
  "event": "test_completed",
  "timestamp": "2025-07-27T14:30:00Z",
  "data": {
    "test_id": "550e8400-e29b-41d4-a716-446655440000",
    "test_type": "comprehensive",
    "success_rate": 94.0,
    "execution_time_seconds": 487,
    "summary": {
      "total_phrases": 350,
      "successful_tests": 329,
      "failed_tests": 21
    }
  },
  "signature": "sha256=webhook_signature_here"
}
```

---

## 📊 Metrics & Monitoring

### Prometheus Metrics

**GET /metrics**
*Prometheus-compatible metrics endpoint*

```bash
curl http://10.20.30.253:8884/metrics
```

**Sample Metrics:**
```
# HELP ash_thrash_tests_total Total number of tests executed
# TYPE ash_thrash_tests_total counter
ash_thrash_tests_total{test_type="quick"} 247
ash_thrash_tests_total{test_type="comprehensive"} 124

# HELP ash_thrash_test_success_rate Current test success rate
# TYPE ash_thrash_test_success_rate gauge
ash_thrash_test_success_rate{category="immediate_crisis"} 0.958
ash_thrash_test_success_rate{category="false_positives"} 0.942

# HELP ash_thrash_api_requests_total Total API requests
# TYPE ash_thrash_api_requests_total counter
ash_thrash_api_requests_total{method="GET",endpoint="/health"} 1247
ash_thrash_api_requests_total{method="POST",endpoint="/api/test/quick"} 89

# HELP ash_thrash_nlp_response_time_seconds NLP server response time
# TYPE ash_thrash_nlp_response_time_seconds histogram
ash_thrash_nlp_response_time_seconds_bucket{le="0.1"} 45
ash_thrash_nlp_response_time_seconds_bucket{le="0.5"} 234
ash_thrash_nlp_response_time_seconds_bucket{le="1.0"} 247
```

### Custom Metrics

**GET /api/metrics/custom**
*Application-specific metrics*

```bash
curl http://10.20.30.253:8884/api/metrics/custom
```

**Response:**
```json
{
  "timestamp": "2025-07-27T14:30:00Z",
  "test_execution": {
    "tests_per_hour": 4.2,
    "average_success_rate": 94.0,
    "success_rate_trend": "+1.2%",
    "fastest_test_time": 23,
    "slowest_test_time": 612
  },
  "phrase_analysis": {
    "most_successful_category": "immediate_crisis",
    "least_successful_category": "community_specific",
    "most_problematic_phrases": [
      "This raid boss is literally killing me",
      "I'm dying from laughter at this meme"
    ]
  },
  "system_performance": {
    "api_requests_per_minute": 12,
    "database_query_time_ms": 8.5,
    "nlp_server_uptime_percent": 99.8,
    "memory_usage_trend": "-2.1%"
  }
}
```

---

## ⚠️ Error Handling

### Standard Error Response Format

**Error Response Structure:**
```json
{
  "error": {
    "code": "TEST_ALREADY_RUNNING",
    "message": "A comprehensive test is already in progress",
    "details": {
      "current_test_id": "550e8400-e29b-41d4-a716-446655440001",
      "started_at": "2025-07-27T14:30:00Z",
      "estimated_completion": "2025-07-27T14:38:00Z"
    },
    "documentation": "https://github.com/the-alphabet-cartel/ash-thrash/docs/api.md#concurrent-tests"
  },
  "request_id": "req_2025_07_27_14_30_00_001",
  "timestamp": "2025-07-27T14:30:00Z"
}
```

### HTTP Status Codes

**Success Codes:**
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for processing
- `204 No Content` - Request successful, no content returned

**Client Error Codes:**
- `400 Bad Request` - Invalid request format or parameters
- `401 Unauthorized` - Authentication required or invalid
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Requested resource not found
- `409 Conflict` - Request conflicts with current state
- `422 Unprocessable Entity` - Valid request, invalid data
- `429 Too Many Requests` - Rate limit exceeded

**Server Error Codes:**
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - NLP server unavailable
- `503 Service Unavailable` - System temporarily unavailable
- `504 Gateway Timeout` - Request timeout

### Common Error Codes

**TEST_ALREADY_RUNNING**
```json
{
  "error": {
    "code": "TEST_ALREADY_RUNNING",
    "message": "Cannot start new test while another is in progress",
    "details": {
      "current_test_id": "550e8400-e29b-41d4-a716-446655440001"
    }
  }
}
```

**NLP_SERVER_UNAVAILABLE**
```json
{
  "error": {
    "code": "NLP_SERVER_UNAVAILABLE", 
    "message": "Cannot connect to NLP server",
    "details": {
      "GLOBAL_NLP_API_URL": "http://10.20.30.253:8881",
      "last_successful_connection": "2025-07-27T14:25:00Z"
    }
  }
}
```

**INVALID_TEST_CATEGORY**
```json
{
  "error": {
    "code": "INVALID_TEST_CATEGORY",
    "message": "Unknown test category specified",
    "details": {
      "provided_category": "invalid_category",
      "valid_categories": ["immediate_crisis", "high_risk", "medium_risk", "low_risk", "general_support", "false_positives", "community_specific"]
    }
  }
}
```

**RATE_LIMIT_EXCEEDED**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "60 seconds",
      "retry_after": 45
    }
  }
}
```

---

## 🔧 SDK & Integration Examples

### Python SDK Example

```python
import requests
import json
from typing import Dict, List, Optional

class AshThrashClient:
    def __init__(self, base_url: str = "http://10.20.30.253:8884", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def health_check(self) -> Dict:
        """Check system health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def run_quick_test(self, **kwargs) -> Dict:
        """Run quick validation test"""
        response = self.session.post(
            f"{self.base_url}/api/test/quick",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def run_comprehensive_test(self, **kwargs) -> Dict:
        """Run comprehensive test suite"""
        response = self.session.post(
            f"{self.base_url}/api/test/comprehensive", 
            json=kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def get_test_status(self, test_id: str) -> Dict:
        """Get test execution status"""
        response = self.session.get(
            f"{self.base_url}/api/test/status/{test_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_results(self) -> Dict:
        """Get latest test results"""
        response = self.session.get(
            f"{self.base_url}/api/test/results/latest"
        )
        response.raise_for_status()
        return response.json()

# Usage example
client = AshThrashClient(api_key="your-api-key")

# Check system health
health = client.health_check()
print(f"System status: {health['status']}")

# Run quick test
test_result = client.run_quick_test(include_metadata=True)
print(f"Test ID: {test_result['test_id']}")
print(f"Success rate: {test_result['summary']['success_rate']}%")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class AshThrashClient {
    constructor(baseUrl = 'http://10.20.30.253:8884', apiKey = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.client = axios.create({
            baseURL: this.baseUrl,
            headers: apiKey ? { 'X-API-Key': apiKey } : {}
        });
    }

    async healthCheck() {
        const response = await this.client.get('/health');
        return response.data;
    }

    async runQuickTest(options = {}) {
        const response = await this.client.post('/api/test/quick', options);
        return response.data;
    }

    async getTestStatus(testId) {
        const response = await this.client.get(`/api/test/status/${testId}`);
        return response.data;
    }

    async getAnalyticsSummary(period = '30d') {
        const response = await this.client.get('/api/analytics/summary', {
            params: { period }
        });
        return response.data;
    }
}

// Usage example
const client = new AshThrashClient('http://10.20.30.253:8884', 'your-api-key');

async function monitorSystem() {
    try {
        const health = await client.healthCheck();
        console.log(`System status: ${health.status}`);
        
        if (health.status === 'healthy') {
            const testResult = await client.runQuickTest({
                include_metadata: true
            });
            console.log(`Test success rate: ${testResult.summary.success_rate}%`);
        }
    } catch (error) {
        console.error('Error monitoring system:', error.response?.data || error.message);
    }
}

// Run monitoring every hour
setInterval(monitorSystem, 60 * 60 * 1000);
```

### cURL Scripts

**Health Monitoring Script:**
```bash
#!/bin/bash
# health_monitor.sh - Monitor Ash-Thrash system health

BASE_URL="http://10.20.30.253:8884"
LOG_FILE="/var/log/ash-thrash-monitor.log"

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check system health
health_response=$(curl -s "$BASE_URL/health")
health_status=$(echo "$health_response" | jq -r '.status')

if [ "$health_status" = "healthy" ]; then
    log_message "✅ System healthy"
    
    # Run quick test if system is healthy
    test_response=$(curl -s -X POST "$BASE_URL/api/test/quick" \
        -H "Content-Type: application/json" \
        -d '{"include_metadata": true}')
    
    success_rate=$(echo "$test_response" | jq -r '.summary.success_rate')
    log_message "📊 Quick test success rate: ${success_rate}%"
    
    if (( $(echo "$success_rate < 90" | bc -l) )); then
        log_message "⚠️ WARNING: Success rate below 90%"
        # Send alert here
    fi
else
    log_message "❌ System unhealthy: $health_status"
    # Send critical alert here
fi
```

**Automated Testing Script:**
```bash
#!/bin/bash
# comprehensive_test.sh - Run comprehensive test and report results

BASE_URL="http://10.20.30.253:8884"
API_KEY="your-api-key"

# Start comprehensive test
echo "Starting comprehensive test..."
test_response=$(curl -s -X POST "$BASE_URL/api/test/comprehensive" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{
        "include_detailed_results": false,
        "generate_report": true
    }')

test_id=$(echo "$test_response" | jq -r '.test_id')
echo "Test ID: $test_id"

# Monitor test progress
while true; do
    status_response=$(curl -s "$BASE_URL/api/test/status/$test_id")
    status=$(echo "$status_response" | jq -r '.status')
    
    if [ "$status" = "completed" ]; then
        echo "✅ Test completed successfully"
        
        # Get results
        results=$(curl -s "$BASE_URL/api/test/results/$test_id")
        success_rate=$(echo "$results" | jq -r '.summary.success_rate')
        echo "📊 Overall success rate: ${success_rate}%"
        
        # Display category performance
        echo "📋 Category Performance:"
        echo "$results" | jq -r '.category_performance | to_entries[] | "  \(.key): \(.value.success_rate)%"'
        break
        
    elif [ "$status" = "failed" ]; then
        echo "❌ Test failed"
        echo "$status_response" | jq -r '.error.message'
        exit 1
        
    else
        progress=$(echo "$status_response" | jq -r '.progress.percent_complete')
        echo "⏳ Test in progress: ${progress}% complete"
        sleep 30
    fi
done
```

---

## 📚 Additional Resources

### Integration Guides

**Dashboard Integration:**
- **Ash-Dashboard Widgets:** Custom components for real-time monitoring
- **Grafana Dashboards:** Pre-built dashboards for metrics visualization
- **Discord Bot Integration:** Commands for team coordination
- **Slack Integration:** Alerts and status updates in Slack channels

**Monitoring Integration:**
- **Prometheus:** Metrics collection and alerting
- **Datadog:** Application performance monitoring
- **New Relic:** Full-stack observability
- **PagerDuty:** Incident management and escalation

### Documentation Links

**Technical Documentation:**
- **[Main README](https://github.com/the-alphabet-cartel/ash-thrash/blob/main/README.md)** - Project overview and setup
- **[Deployment Guide](./deployment_v2_1.md)** - Production deployment procedures
- **[Team Guide](../team/team_guide_v2_1.md)** - User-focused operation guide
- **[Troubleshooting Guide](./troubleshooting_v2_1.md)** - Problem resolution

**Community Resources:**
- **[The Alphabet Cartel Discord](https://discord.gg/alphabetcartel)** - Community support
- **[GitHub Repository](https://github.com/the-alphabet-cartel/ash-thrash)** - Source code and issues
- **[Website](https://alphabetcartel.org)** - Organization information

### Support Channels

**Technical Support:**
- **GitHub Issues:** Bug reports and feature requests
- **Discord #tech-support:** Community technical assistance
- **Email:** tech-support@alphabetcartel.org
- **Emergency:** emergency@alphabetcartel.org

**API Support:**
- **Documentation Issues:** Report inaccuracies or missing information
- **Integration Help:** Assistance with API integration
- **Rate Limit Increases:** Request higher rate limits for production use
- **Custom Endpoints:** Discuss custom API endpoints for specific needs

---

**Built with 🖤 for chosen family everywhere.**

This comprehensive API enables seamless integration of crisis detection testing into workflows, monitoring systems, and community tools. The Ash-Thrash API provides the foundation for maintaining accurate, reliable crisis detection while supporting the broader ecosystem of safety and support tools.

**The Alphabet Cartel** - Building inclusive gaming communities through technology.

**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org | **GitHub:** https://github.com/the-alphabet-cartel

---

**Document Version:** 2.1  
**Last Updated:** July 27, 2025  
**API Version:** v2.1.0  
**Next Review:** August 27, 2025