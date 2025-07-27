# 🧪 Ash-Thrash Team Member Guide

> **Comprehensive Crisis Detection Testing Suite for The Alphabet Cartel**

**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Discord:** https://discord.gg/alphabetcartel  
**Version:** 1.0+  
**Last Updated:** July 26, 2025

---

## 📋 Overview

Ash-Thrash is our comprehensive testing framework that ensures **Ash's crisis detection system** works reliably when community members need help most. It systematically tests **350 carefully crafted phrases** against our NLP server to validate detection accuracy and speed.

### Why This Matters

Crisis detection systems save lives, but they must be thoroughly validated to ensure they catch real emergencies while avoiding alert fatigue from false positives. Ash-Thrash provides continuous automated testing to maintain system reliability.

---

## 🎯 What Ash-Thrash Tests

### Testing Categories & Goals

| Priority Level | Phrases | Target Rate | Critical? | Purpose |
|---|---|---|---|---|
| **🚨 Definite High** | 50 | **100%** | ✅ CRITICAL | Life-threatening situations |
| **⚠️ Definite Medium** | 50 | **65%** | - | Support needed situations |
| **🔍 Definite Low** | 50 | **65%** | - | General wellness checks |
| **✅ Definite None** | 50 | **95%** | ✅ CRITICAL | Prevent false alerts |
| **📈 Maybe High/Medium** | 50 | **90%** | - | Edge cases (escalation OK) |
| **📊 Maybe Medium/Low** | 50 | **80%** | - | Borderline situations |
| **📉 Maybe Low/None** | 50 | **90%** | ✅ CRITICAL | Prevent false positives |

### Safety-First Design

- **100% catch rate** for high-priority crises (lives depend on this)
- **95% accuracy** for non-crisis messages (prevent alert fatigue)
- **Allow escalation** in "maybe" categories (better safe than sorry)
- **Real-world phrases** based on actual community language

---

## 🚀 Getting Started

### For Crisis Response Team Members

**What You Need to Know:**
- Ash-Thrash runs automatically in the background
- Results appear in the ash-dash dashboard
- Failed tests indicate potential detection issues
- No manual intervention needed for routine operation

**Key Locations:**
- **Dashboard:** http://10.20.30.16:8883 (via ash-dash)
- **API:** http://10.20.30.16:8884
- **Results Storage:** Server at 10.20.30.16:/opt/ash-thrash/results/

### For Technical Team Members

**System Architecture:**
```
Ash-Thrash (10.20.30.16:8884) 
    ↓ Sends test phrases
Ash NLP Server (10.20.30.16:8881)
    ↓ Returns analysis
Ash-Thrash validates results
    ↓ Stores data
Ash-Dash (10.20.30.16:8883) displays metrics
```

---

## 📊 Understanding Test Results

### Reading the Dashboard

**Overall Status Indicators:**
- 🟢 **All Goals Met** - System performing optimally
- 🟡 **Minor Issues** - Some targets missed but not critical
- 🔴 **Critical Failure** - High-priority detection below 100%

**Key Metrics:**
- **Pass Rate** - Percentage of correct detections
- **Response Time** - How fast the NLP server responds
- **Confidence Scores** - How certain the AI is about classifications
- **Failure Analysis** - Which specific phrases failed and why

### When to Take Action

**🚨 Immediate Action Required:**
- High-priority detection below 95%
- None-priority false positive rate above 10%
- System completely unreachable

**⚠️ Investigation Needed:**
- Consistent decline in performance over time
- New patterns of failures appearing
- Response times significantly increasing

**✅ Normal Operations:**
- Minor fluctuations in medium/low priority rates
- Occasional single phrase failures
- Response times under 2 seconds

---

## 🔧 Running Tests Manually

### Quick Validation (10 phrases)

**Via Docker (Recommended):**
```bash
docker-compose exec ash-thrash python src/quick_validation.py
```

**Locally:**
```bash
cd /opt/ash-thrash
python src/quick_validation.py
```

### Comprehensive Testing (350 phrases)

**Via Docker:**
```bash
docker-compose exec ash-thrash python src/comprehensive_testing.py
```

**Locally:**
```bash
cd /opt/ash-thrash
python src/comprehensive_testing.py
```

### Viewing Results

**Latest Results:**
```bash
# View most recent comprehensive test
cat results/comprehensive/comprehensive_test_$(date +%Y%m%d)*.json | jq '.'

# View quick validation
cat results/quick_validation/quick_validation_$(date +%Y%m%d)*.json | jq '.'
```

**Via API:**
```bash
# Get current status
curl http://10.20.30.16:8884/api/test/status

# Get latest results
curl http://10.20.30.16:8884/api/test/results/latest
```

---

## 🚨 Troubleshooting Common Issues

### "NLP Server Unreachable"

**Check NLP Server Status:**
```bash
curl http://10.20.30.16:8881/health
```

**If NLP server is down:**
1. Check if ash-nlp container is running
2. Verify Windows 11 server (10.20.30.16) is accessible
3. Check Docker logs: `docker logs ash-nlp`
4. Restart if needed: `docker-compose restart ash-nlp`

### "Tests Timing Out"

**Increase timeout in .env:**
```bash
TEST_TIMEOUT_SECONDS=15  # Increase from default 10
MAX_CONCURRENT_TESTS=3   # Reduce from default 5
```

**Check server load:**
```bash
# On Windows 11 server (10.20.30.16)
docker stats ash-nlp
```

### "High Failure Rates"

**Check specific failures:**
```bash
# View failed phrases
curl http://10.20.30.16:8884/api/test/results/latest | jq '.category_results.definite_high.failures'
```

**Common causes:**
- NLP model needs retraining
- New crisis language patterns not recognized
- Server resource constraints
- Network latency issues

### "API Not Responding"

**Restart ash-thrash services:**
```bash
cd /opt/ash-thrash
docker-compose restart ash-thrash-api
```

**Check logs:**
```bash
docker-compose logs ash-thrash-api
```

---

## 📈 Monitoring & Maintenance

### Automated Monitoring

**Scheduled Tests:**
- **Comprehensive:** Every 6 hours
- **Quick Validation:** Every hour
- **Results Cleanup:** Daily at 2 AM

**Alert Thresholds:**
- High-priority detection < 95%
- False positive rate > 10%
- Response time > 5 seconds
- System unavailable > 5 minutes

### Manual Maintenance Tasks

**Weekly:**
- Review dashboard trends
- Check for new failure patterns
- Verify integration with ash-dash

**Monthly:**
- Archive old test results
- Review testing goals and targets
- Update test phrases if needed

**Quarterly:**
- Full system performance review
- Update documentation
- Team training refresh

---

## 🔗 Integration with Other Systems

### Ash-Dash Dashboard

**Setup Integration:**
1. Dashboard automatically connects to ash-thrash API
2. Testing metrics appear in main dashboard
3. Real-time status updates every 2 minutes
4. Historical charts show performance trends

**Dashboard Sections:**
- **Testing Overview** - Current status and recent results
- **Performance Trends** - Charts showing detection rates over time
- **Failure Analysis** - Detailed breakdown of missed detections
- **System Health** - API response times and availability

### Ash Main Bot

**Connection:**
- Ash bot and ash-thrash both test the same NLP server
- No direct integration needed
- Results validate the same detection system used by the bot
- Performance issues in testing indicate potential bot issues

### NLP Server (Ash-NLP)

**Communication:**
- Ash-thrash sends HTTP requests to port 8881
- Same API endpoints used by the main bot
- Testing validates actual production detection pipeline
- No special testing mode required

---

## 📚 Best Practices

### For Crisis Response Teams

1. **Monitor Daily** - Check dashboard for any red indicators
2. **Investigate Patterns** - Look for trends in failures, not just individual misses
3. **Report Issues Early** - Don't wait for critical failures to report concerns
4. **Understand Context** - Remember testing validates the same system protecting community members

### For Technical Teams

1. **Test Before Deployment** - Run comprehensive tests before NLP updates
2. **Monitor Resource Usage** - Ensure testing doesn't impact production performance
3. **Archive Results** - Keep historical data for trend analysis
4. **Document Changes** - Log any modifications to test phrases or thresholds

### For System Administrators

1. **Backup Configurations** - Regularly backup test phrases and settings
2. **Monitor Disk Space** - Test results can accumulate over time
3. **Check Dependencies** - Ensure Docker, Python, and network connectivity
4. **Plan Maintenance** - Schedule updates during low-activity periods

---

## 🆘 Emergency Procedures

### Critical System Failure

**If ash-thrash shows critical detection failures:**

1. **Immediate Actions:**
   - Verify main Ash bot is still responding
   - Check ash-nlp server status and resources
   - Alert Crisis Response team leads

2. **Investigation Steps:**
   - Run manual comprehensive test
   - Check NLP server logs for errors
   - Compare against previous successful results
   - Test with known working phrases

3. **Escalation Process:**
   - If main bot detection is affected, consider temporary manual monitoring
   - Contact technical leads immediately
   - Document timeline and symptoms
   - Prepare for potential system restart

### Communication During Issues

**Internal Team:**
- Use #crisis-response Discord channel for coordination
- Post status updates every 30 minutes during active issues
- Document resolution steps for future reference

**Community Communication:**
- Only communicate outages if main bot functionality is impacted
- Focus on resolution timeline, not technical details
- Emphasize commitment to community safety

---

## 📞 Support & Resources

### Getting Help

**Technical Issues:**
- **GitHub Issues:** https://github.com/The-Alphabet-Cartel/ash-thrash/issues
- **Discord:** #tech-support in https://discord.gg/alphabetcartel
- **Direct Contact:** Technical team leads

**Team Training:**
- **Documentation:** This guide and README.md
- **Video Walkthroughs:** Available in Discord resources channel
- **One-on-One Training:** Contact Crisis Response leads

### Quick Reference

**Key URLs:**
- Testing Dashboard: http://10.20.30.16:8883
- API Status: http://10.20.30.16:8884/health
- NLP Server: http://10.20.30.16:8881/health

**Important Files:**
- Test Results: `/opt/ash-thrash/results/`
- Configuration: `/opt/ash-thrash/.env`
- Logs: `docker-compose logs ash-thrash`

**Emergency Contacts:**
- Technical Lead: [Contact info]
- Crisis Response Lead: [Contact info]
- System Administrator: [Contact info]

---

## 📝 Appendix

### Testing Categories Explained

**Definite Categories:**
- Clear, unambiguous examples
- Must detect exact priority level
- Used to validate core detection accuracy

**Maybe Categories:**
- Ambiguous or context-dependent phrases
- Allow priority escalation (but not de-escalation)
- Test edge case handling and safety margins

### Sample Test Phrases

**Definite High (must detect as high priority):**
- "I can't take this anymore"
- "I want to end it all"
- "I'm thinking about suicide"

**Definite None (must detect as no priority):**
- "Having a great day today!"
- "Love this new movie"
- "Working on my coding project"

**Maybe High/Medium (can escalate, cannot de-escalate):**
- "Everything feels hopeless"
- "I don't see the point anymore"
- "Life is just too hard"

### Performance Benchmarks

**Typical Response Times:**
- Quick Validation (10 phrases): 30-60 seconds
- Comprehensive Test (350 phrases): 8-15 minutes
- Individual phrase analysis: 0.5-2 seconds

**Target Accuracy Rates:**
- Overall system accuracy: 85-90%
- High-priority catch rate: 100%
- False positive rate: <5%

---

*Built with 🖤 for chosen family support*

**The Alphabet Cartel** - Crisis Detection Testing Team  
Last updated: July 26, 2025