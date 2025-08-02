# Ash-Thrash v3.0 Team Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Team Guide**: Setup and Usage for The Alphabet Cartel Team  
**Document Location**: `docs/team/team_guide_v3_0.md`  
**Last Updated**: August 2025

---

## 👥 Welcome to Ash-Thrash v3.0

This guide helps Alphabet Cartel team members get up and running with Ash-Thrash v3.0 quickly and effectively. Whether you're a developer, administrator, or community moderator, this guide has you covered.

---

## 🎯 Quick Start by Role

### **🧑‍💻 Developers**
```bash
# 1. Clone and setup
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Local development setup
pip install -r requirements.txt
python main.py setup

# 3. Start testing
python cli.py validate setup
python cli.py test quick
```

### **⚙️ System Administrators** 
```bash
# 1. Production deployment
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Configure for production
python main.py setup
# Edit .env with production settings

# 3. Deploy services
python main.py start
python main.py status
```

### **👮‍♀️ Community Moderators**
```bash
# 1. Monitor test results via Discord webhooks
# 2. Access results via ash-dash integration
# 3. Request specific tests via team Discord channel
```

---

## 🚀 Team Setup Guide

### **Step 1: Repository Access**

Ensure you have access to:
- **Main Repository**: https://github.com/the-alphabet-cartel/ash-thrash
- **Container Registry**: GitHub Container Registry (automatic with repo access)
- **Discord Webhooks**: Team Discord channels for notifications

### **Step 2: Environment Configuration**

#### **Development Environment (.env)**
```bash
# Core Configuration
GLOBAL_NLP_API_URL=http://10.20.30.253:8881
GLOBAL_THRASH_API_PORT=8884

# Team Discord Integration
THRASH_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_TEAM_WEBHOOK
DISCORD_NOTIFICATIONS_ENABLED=true
NOTIFY_ON_COMPREHENSIVE_TESTS=true

# Development Settings
GLOBAL_LOG_LEVEL=INFO
THRASH_ENABLE_API_DOCS=true
```

#### **Production Environment (.env)**
```bash
# Production NLP Server
GLOBAL_NLP_API_URL=http://10.20.30.253:8881

# Production Discord Webhook
THRASH_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/PRODUCTION_WEBHOOK
NOTIFY_ON_COMPREHENSIVE_TESTS=true
NOTIFY_ON_QUICK_TESTS=false

# Production Settings  
GLOBAL_LOG_LEVEL=WARNING
THRASH_ENABLE_API_DOCS=false
THRASH_ENABLE_CORS=false
```

### **Step 3: Team Workflow Integration**

#### **GitHub Integration**
- **Automated Builds**: Docker images build automatically on main branch pushes
- **Pull Requests**: All changes require PR review
- **Issues**: Use GitHub Issues for bug reports and feature requests

#### **Discord Integration**
- **Test Notifications**: Automated results posted to #ash-testing channel
- **Manual Testing**: Use `/test comprehensive` bot command (when implemented)
- **Alerts**: Critical test failures alert @Crisis-Team role

---

## 🧪 Testing Workflows

### **Daily Testing Routine**

#### **Morning Validation (10 minutes)**
```bash
# 1. Quick health check
python main.py status

# 2. Validate system
python cli.py validate setup

# 3. Quick test run
python cli.py test quick --sample-size 30

# 4. Check results in Discord
```

#### **Weekly Comprehensive Testing (30 minutes)**
```bash
# 1. Full comprehensive test
python cli.py test comprehensive

# 2. Review tuning suggestions
# Check output for NLP threshold recommendations

# 3. Document results
# Update team tracking spreadsheet

# 4. Apply tuning if needed
# Update ash-nlp .env with suggested values
```

### **Pre-Deployment Testing**

#### **Before NLP Updates**
```bash
# 1. Baseline test
python cli.py test comprehensive --output file
mv results/comprehensive_*.json results/baseline_pre_update.json

# 2. Deploy NLP changes
# (Update ash-nlp)

# 3. Post-update test
python cli.py test comprehensive --output file
mv results/comprehensive_*.json results/post_update.json

# 4. Compare results
# Ensure no degradation in critical categories
```

#### **Before Bot Updates**
```bash
# 1. Validate integration
python cli.py api health

# 2. Test category accuracy
python cli.py test category definite_high
python cli.py test category definite_none

# 3. Verify 100% accuracy on critical categories
```

### **Incident Response Testing**

#### **After Crisis Detection Issues**
```bash
# 1. Immediate validation
python cli.py test category definite_high --output json

# 2. Check for false negatives
# Review failed high-crisis phrases

# 3. Emergency tuning
# Apply immediate threshold adjustments

# 4. Re-test and validate
python cli.py test category definite_high
```

---

## 👥 Team Roles & Responsibilities

### **🧑‍💻 Development Team**

#### **Responsibilities**
- Maintain and improve ash-thrash codebase
- Add new test phrases as community needs evolve
- Integrate with new ash ecosystem components
- Monitor and fix technical issues

#### **Daily Tasks**
```bash
# Code quality checks
python cli.py validate setup

# Test new features
python cli.py test quick

# Monitor API health
curl http://localhost:8884/health
```

#### **Weekly Tasks**
- Review comprehensive test results
- Update test phrases based on community feedback
- Monitor Docker image builds and deployments
- Update documentation as needed

### **⚙️ Operations Team**

#### **Responsibilities**
- Deploy and maintain ash-thrash in production
- Monitor system performance and health
- Manage Docker container orchestration
- Ensure integration with ash ecosystem

#### **Daily Tasks**
```bash
# Production health monitoring
python main.py status

# Check service logs
python main.py logs --follow ash-thrash-api

# Validate NLP connectivity
python cli.py api health
```

#### **Weekly Tasks**
- Analyze test performance trends
- Scale services based on load
- Update production configurations
- Backup test results and configurations

### **👮‍♀️ Community Safety Team**

#### **Responsibilities**
- Monitor crisis detection accuracy
- Review test results for safety implications
- Provide input on test phrase categories
- Escalate critical detection failures

#### **Daily Tasks**
- Review Discord test notifications
- Monitor ash-dash for test results
- Check for false positive/negative alerts

#### **Weekly Tasks**
- Analyze comprehensive test trends
- Review and approve new test phrases
- Provide feedback on tuning suggestions
- Document any safety concerns

---

## 🔧 Common Team Workflows

### **Adding New Test Phrases**

#### **Process**
1. **Identify Need**: Community feedback or incident analysis
2. **Propose Addition**: Create GitHub issue with phrase and category
3. **Team Review**: Safety team and developers review
4. **Implementation**: Add to `src/test_data.py`
5. **Validation**: Test with new phrases
6. **Deployment**: Merge to main and deploy

#### **Example Workflow**
```bash
# 1. Create feature branch
git checkout -b add-new-crisis-phrases

# 2. Edit test data
vim src/test_data.py
# Add phrases to appropriate category

# 3. Validate changes
python cli.py validate data

# 4. Test new phrases
python cli.py test category definite_high

# 5. Create PR
git add src/test_data.py
git commit -m "feat: add new high-crisis phrases"
git push origin add-new-crisis-phrases
```

### **Tuning NLP Thresholds**

#### **Process**
1. **Run Comprehensive Test**: Get current performance baseline
2. **Review Suggestions**: Analyze ash-thrash tuning recommendations
3. **Team Discussion**: Discuss changes in #ash-development
4. **Apply Changes**: Update ash-nlp environment variables
5. **Validate**: Re-run tests to confirm improvements
6. **Monitor**: Watch for 24-48 hours to ensure stability

#### **Example Workflow**
```bash
# 1. Baseline test
python cli.py test comprehensive

# 2. Review suggestions
# Example output:
# 🚨 HIGH PRIORITY: definite_high only 85.0% (need 100.0%). 
#    Consider lowering NLP_HIGH_CRISIS_THRESHOLD from 0.8 to 0.7

# 3. Apply suggestion to ash-nlp
# Edit ash-nlp/.env:
# NLP_HIGH_CRISIS_THRESHOLD=0.7

# 4. Restart ash-nlp
# (In ash-nlp directory)
# docker-compose restart ash-nlp

# 5. Validate improvement
python cli.py test category definite_high
```

### **Incident Response**

#### **False Negative (Missed Crisis)**
```bash
# 1. Immediate test
python cli.py test category definite_high --output json

# 2. Check specific phrase
# Add problematic phrase to test data if needed

# 3. Emergency threshold adjustment
# Lower detection thresholds immediately

# 4. Validate fix
python cli.py test category definite_high

# 5. Monitor production
# Watch Discord for continued issues
```

#### **False Positive (Normal Message Flagged)**
```bash
# 1. Test normal conversation detection
python cli.py test category definite_none --output json

# 2. Review failed phrases
# Identify problematic detection patterns

# 3. Adjust thresholds
# Raise thresholds to reduce false positives

# 4. Re-test
python cli.py test category definite_none

# 5. Balance check
# Ensure high-crisis detection still works
python cli.py test category definite_high
```

---

## 📊 Team Dashboards & Monitoring

### **Ash-Dashboard Integration**

#### **Key Metrics to Monitor**
- **Overall Pass Rate**: Should stay above 85%
- **Critical Category Performance**: definite_high (100%), definite_none (95%)
- **Test Frequency**: Ensure regular testing schedule
- **Response Times**: API and NLP server performance

#### **Dashboard URLs**
- **Main Dashboard**: https://ashdash.alphabetcartel.net/testing
- **API Health**: http://10.20.30.253:8884/health
- **Historical Results**: http://10.20.30.253:8884/api/test/history

### **Discord Monitoring**

#### **Channel Setup**
- **#ash-testing**: Automated test result notifications
- **#ash-alerts**: Critical test failures and system issues
- **#ash-development**: Team discussion and planning

#### **Notification Examples**
```
🧪 Ash-Thrash Test Completed: Comprehensive
📊 Overall Results: 87.4% pass rate
🎯 Goal Achievement: 71.4%
⚠️ Issues Found:
  ❌ definite_medium: 62.0% (need 65.0%)
  ❌ definite_none: 88.0% (need 95.0%)
🔧 Tuning Suggestions Available
```

### **Performance Tracking**

#### **Weekly Team Metrics**
- **Test Coverage**: Number of tests run per week
- **Accuracy Trends**: Pass rate trends over time
- **Issue Resolution**: Time to fix critical failures
- **System Uptime**: API and service availability

#### **Monthly Team Review**
- **Goal Achievement**: Progress toward 100% accuracy targets
- **Test Phrase Effectiveness**: Review and update phrases
- **Team Workflow**: Process improvements
- **Community Impact**: Crisis detection effectiveness

---

## 🛠️ Development & Contribution Guidelines

### **Code Contribution Process**

#### **1. Issue Creation**
- Use GitHub Issues for all changes
- Tag with appropriate labels (bug, feature, enhancement)
- Get team consensus before major changes

#### **2. Development Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Edit code, update tests, update documentation

# Validate changes
python cli.py validate setup
python cli.py test quick

# Commit and push
git add .
git commit -m "feat: descriptive commit message"
git push origin feature/your-feature-name

# Create Pull Request
# Request review from at least one team member
```

#### **3. Code Review Requirements**
- At least one team member approval
- All tests must pass
- Documentation must be updated
- No breaking changes without team discussion

### **Testing Standards**

#### **Before Committing**
```bash
# Validate test data
python cli.py validate data

# Run quick test
python cli.py test quick

# Check API functionality
python cli.py api health
```

#### **Before Releasing**
```bash
# Full comprehensive test
python cli.py test comprehensive

# Docker build test
python main.py build
python main.py start
python main.py test-all comprehensive
```

### **Documentation Standards**

- Update README.md for user-facing changes
- Update team guide for workflow changes
- Update API documentation for API changes
- Include examples for new features

---

## 🆘 Team Support & Escalation

### **Support Channels**

#### **Level 1: Self-Service**
- Check this team guide
- Review troubleshooting documentation
- Search GitHub Issues

#### **Level 2: Team Discussion**
- Post in #ash-development Discord channel
- Tag relevant team members
- Provide logs and error details

#### **Level 3: Escalation**
- Create GitHub Issue for bugs
- Tag @Crisis-Team for safety issues
- Emergency: Direct message team leads

### **Common Team Issues**

#### **"Tests Failing After NLP Update"**
```bash
# 1. Check NLP connectivity
python cli.py api health

# 2. Run baseline test
python cli.py test category definite_high

# 3. If failing, revert NLP changes temporarily
# 4. Investigate tuning requirements
# 5. Apply gradual threshold adjustments
```

#### **"Docker Containers Won't Start"**
```bash
# 1. Check system resources
docker system df
docker system prune

# 2. Restart services
python main.py stop
python main.py start

# 3. Check logs
python main.py logs --follow

# 4. If still failing, rebuild
python main.py clean --force
python main.py build
python main.py start
```

#### **"API Not Responding"**
```bash
# 1. Check service status
python main.py status

# 2. Check port availability
netstat -tulpn | grep 8884

# 3. Restart API service
docker-compose restart ash-thrash-api

# 4. Check logs for errors
python main.py logs ash-thrash-api
```

---

## 📋 Team Checklists

### **New Team Member Onboarding**

- [ ] Repository access granted
- [ ] Discord channels joined (#ash-testing, #ash-development)
- [ ] Local development environment setup
- [ ] First successful test run completed
- [ ] Team workflow training completed
- [ ] Emergency procedures understood

### **Weekly Team Tasks**

- [ ] Comprehensive test run completed
- [ ] Results reviewed and documented
- [ ] Discord notifications monitored
- [ ] GitHub Issues triaged
- [ ] Performance metrics reviewed
- [ ] Any tuning applied and validated

### **Pre-Deployment Checklist**

- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Docker images built successfully
- [ ] Staging environment validated
- [ ] Team notification sent
- [ ] Rollback plan confirmed

### **Incident Response Checklist**

- [ ] Issue severity assessed
- [ ] Team leads notified
- [ ] Immediate mitigation applied
- [ ] Root cause investigation started
- [ ] Community impact evaluated
- [ ] Fix implemented and tested
- [ ] Post-incident review scheduled

---

## 🎯 Team Goals & Metrics

### **Primary Goals**

1. **100% High Crisis Detection**: Never miss suicidal ideation
2. **95% False Positive Prevention**: Minimize normal conversation flags
3. **<5 Minute Response Time**: Quick issue resolution
4. **Daily Testing Coverage**: Consistent validation schedule

### **Team KPIs**

- **Test Execution**: 7+ comprehensive tests per week
- **Issue Resolution**: <24 hours for critical issues
- **Accuracy Improvement**: Monthly trending upward
- **Community Safety**: Zero missed crisis incidents

### **Success Metrics**

- **Technical Excellence**: Clean code, comprehensive tests, good documentation
- **Team Collaboration**: Effective communication, shared responsibility
- **Community Impact**: Safer Discord environment, effective crisis response
- **Continuous Improvement**: Regular process refinement, learning culture

---

**The Alphabet Cartel team's dedication to crisis detection accuracy directly protects our community members. Every test run, every tuning adjustment, and every code improvement contributes to saving lives.**

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Building safer communities together.* 👥🛡️