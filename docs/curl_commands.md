```python
curl -X POST http://localhost:8881/analyze -H "Content-Type: application/json" -d '{"message": "${MESSAGE}", "user_id": "test_user", "channel_id": "test_channel"}' | jq
```