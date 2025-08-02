# Ash-Thrash v3.0 Team Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Team Guide**: Setup and Usage for The Alphabet Cartel Team  
**Document Location**: `docs/team/team_guide_v3_0.md`  
**Last Updated**: August 2025

---

## 👥 Welcome to Ash-Thrash v3.0

This guide helps Alphabet Cartel team members get up and running with Ash-Thrash v3.0 quickly and effectively. Whether you're a developer, administrator, or community moderator, this guide covers the persistent container workflow that keeps services running continuously.

---

## 🎯 Quick Start by Role

### **🧑‍💻 Developers**
```bash
# 1. Clone and setup
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Start persistent containers
docker compose up -d

# 3. Start testing immediately
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash python cli.py test quick
```

### **⚙️ System Administrators** 
```bash
# 1. Production deployment
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Configure for production
python main.py setup
# Edit .env with production settings

# 3. Deploy persistent services
docker compose up -d

# 4. Verify deployment
docker compose ps
docker compose exec ash-thrash python cli.py validate setup
```

### **👮‍♀️ Community Moderators**
```bash
# 1. Monitor test results via Discord webhooks
# 2. Access results via ash-dash integration
# 3. Request specific tests: docker compose exec ash-thrash python cli.py test category definite_high
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

#### **Persistent Container Workflow**
- **Always Running**: Containers remain active for immediate testing
- **No Orphan Containers**: Clean management via Docker Compose
- **Instant Testing**: Execute tests without container startup delays
- **Easy Management**: Single command to start/stop all services

#### **GitHub Integration**
- **Automated Builds**: Docker images build automatically on main branch pushes
- **Pull Requests**: All changes require PR review
- **Issues**: Use GitHub Issues for bug reports and feature requests

#### **Discord Integration**
- **Test Notifications**: Automated results posted to #ash-testing channel
- **Manual Testing**: Execute tests via persistent containers
- **Alerts**: Critical test failures alert @Crisis-Team role

---

## 🧪 Testing Workflows

### **Daily Testing Routine with Persistent Containers**

#### **Morning Validation (5 minutes)**
```bash
# 1. Ensure containers are running
docker compose ps

# 2. Quick health check
docker compose exec ash-thrash python cli.py validate setup

# 3. Quick test run
docker compose exec ash-thrash python cli.py test quick --sample-size 30

# 4. Check results in Discord
```

#### **Weekly Comprehensive Testing (15 minutes)**
```bash
# 1. Start containers if not running
docker compose up -d

# 2. Full comprehensive test
docker compose exec ash-thrash python cli.py test comprehensive

# 3. Review tuning suggestions
# Check output for NLP threshold recommendations

# 4. Document results
# Update team tracking spreadsheet

# 5. Apply tuning if needed
# Update ash-nlp .env with suggested values
```

### **Pre-Deployment Testing with Persistent Containers**

#### **Before NLP Updates**
```bash
# 1. Ensure containers are running
docker compose up -d

# 2. Baseline test
docker compose exec ash-thrash python cli.py test comprehensive --output file
docker compose cp ash-thrash:/app/results/comprehensive_*.json ./baseline_pre_update.json

# 3. Deploy NLP changes
# (Update ash-nlp)

# 4. Post-update test
docker compose exec ash-thrash python cli.py test comprehensive --output file
docker compose cp ash-thrash:/app/results/comprehensive_*.json ./post_update.json

# 5. Compare results
# Ensure no degradation in critical categories
```

#### **Before Bot Updates**
```bash
# 1. Validate integration from persistent container
docker compose exec ash-thrash python cli.py api health

# 2. Test category accuracy
docker compose exec ash-thrash python cli.py test category definite_high
docker compose exec ash-thrash python cli.py test category definite_none

# 3. Verify 100% accuracy on critical categories
```

### **Incident Response Testing with Persistent Containers**

#### **After Crisis Detection Issues**
```bash
# 1. Immediate validation from running container
docker compose exec ash-thrash python cli.py test category definite_high --output json

# 2. Check for false negatives
# Review failed high-crisis phrases

# 3. Emergency tuning
# Apply immediate threshold adjustments

# 4. Re-test and validate from persistent container
docker compose exec ash-thrash python cli.py test category definite_high
```

---

## 👥 Team Roles & Responsibilities

### **🧑‍💻 Development Team**

#### **Responsibilities**
- Maintain and improve ash-thrash codebase
- Add new test phrases as community needs evolve
- Integrate with new ash ecosystem components
- Monitor and fix technical issues

#### **Daily Tasks with Persistent Containers**
```bash
# Code quality checks from running container
docker compose exec ash-thrash python cli.py validate setup

# Test new features immediately
docker compose exec ash-thrash python cli.py test quick

# Monitor API health
curl http://localhost:8884/health
docker compose exec ash-thrash python cli.py api health
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

#### **Daily Tasks with Persistent Containers**
```bash
# Production health monitoring
docker compose ps
docker compose exec ash-thrash python cli.py validate setup

# Check service logs
docker compose logs ash-thrash-api
docker compose logs ash-thrash

# Validate NLP connectivity from container
docker compose exec ash-thrash python cli.py api health
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

#### **Daily Tasks with Persistent Containers**
- Review Discord test notifications
- Monitor ash-dash for test results
- Check for false positive/negative alerts
- Run ad-hoc tests: `docker compose exec ash-thrash python cli.py test category definite_high`

#### **Weekly Tasks**
- Analyze comprehensive test trends
- Review and approve new test phrases
- Provide feedback on tuning suggestions
- Document any safety concerns

---

## 🔧 Common Team Workflows

### **Adding New Test Phrases with Persistent Containers**

#### **Process**
1. **Identify Need**: Community feedback or incident analysis
2. **Propose Addition**: Create GitHub issue with phrase and category
3. **Team Review**: Safety team and developers review
4. **Implementation**: Add to `src/test_data.py`
5. **Validation**: Test with new phrases from persistent container
6. **Deployment**: Merge to main and deploy

#### **Example Workflow**
```bash
# 1. Create feature branch
git checkout -b add-new-crisis-phrases

# 2. Edit test data
vim src/test_data.py
# Add phrases to appropriate category

# 3. Validate changes from persistent container
docker compose up -d
docker compose exec ash-thrash python cli.py validate data

# 4. Test new phrases immediately
docker compose exec ash-thrash python cli.py test category definite_high

# 5. Create PR
git add src/test_data.py
git commit -m "feat: add new high-crisis phrases"
git push origin add-new-crisis-phrases
```

### **Tuning NLP Thresholds with Persistent Containers**

#### **Process**
1. **Run Comprehensive Test**: Get current performance baseline from persistent container
2. **Review Suggestions**: Analyze ash-thrash tuning recommendations
3. **Team Discussion**: Discuss changes in #ash-development
4. **Apply Changes**: Update ash-nlp environment variables
5. **Validate**: Re-run tests from persistent container to confirm improvements
6. **Monitor**: Watch for 24-48 hours to ensure stability

#### **Example Workflow**
```bash
# 1. Baseline test from persistent container
docker compose up -d
docker compose exec ash-thrash python cli.py test comprehensive

# 2. Review suggestions
# Example output:
# 🚨 HIGH PRIORITY: definite_high only 85.0% (need 100.0%). 
#    Consider lowering NLP_HIGH_CRISIS_THRESHOLD from 0.8 to 0.7

# 3. Apply suggestion to ash-nlp
# Edit ash-nlp/.env:
# NLP_HIGH_CRISIS_THRESHOLD=0.7

# 4. Restart ash-nlp
# (In ash-nlp directory)
# docker compose restart ash-nlp

# 5. Validate improvement immediately from persistent container
docker compose exec ash-thrash python cli.py test category definite_high
```

### **Incident Response with Persistent Containers**

#### **False Negative (Missed Crisis)**
```bash
# 1. Immediate test from running container
docker compose exec ash-thrash python cli.py test category definite_high --output json

# 2. Check specific phrase
# Add problematic phrase to test data if needed

# 3. Emergency threshold adjustment
# Lower detection thresholds immediately

# 4. Validate fix from persistent container
docker compose exec ash-thrash python cli.py test category definite_high

# 5. Monitor production
# Watch Discord for continued issues
```

#### **False Positive (Normal Message Flagged)**
```bash
# 1. Test normal conversation detection from persistent container
docker compose exec ash-thrash python cli.py test category definite_none --output json

# 2. Review failed phrases
# Identify problematic detection patterns

# 3. Adjust thresholds
# Raise thresholds to reduce false positives

# 4. Re-test from persistent container
docker compose exec ash-thrash python cli.py test category definite_none

# 5. Balance check
# Ensure high-crisis detection still works
docker compose exec ash-thrash python cli.py test category definite_high
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

### **Performance Tracking with Persistent Containers**

#### **Weekly Team Metrics**
- **Test Coverage**: Number of tests run per week via persistent containers
- **Accuracy Trends**: Pass rate trends over time
- **Issue Resolution**: Time to fix critical failures
- **System Uptime**: API and service availability

#### **Monthly Team Review**
- **Goal Achievement**: Progress toward 100% accuracy targets
- **Test Phrase Effectiveness**: Review and update phrases
- **Team Workflow**: Process improvements with persistent containers
- **Community Impact**: Crisis detection effectiveness

---

## 🛠️ Development & Contribution Guidelines

### **Code Contribution Process with Persistent Containers**

#### **1. Issue Creation**
- Use GitHub Issues for all changes
- Tag with appropriate labels (bug, feature, enhancement)
- Get team consensus before major changes

#### **2. Development Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Start persistent containers for immediate testing
docker compose up -d

# Make changes
# Edit code, update tests, update documentation

# Validate changes immediately
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash python cli.py test quick

# Commit and push
git add .
git commit -m "feat: descriptive commit message"
git push origin feature/your-feature-name

# Create Pull Request
# Request review from at least one team member
```

#### **3. Code Review Requirements**
- At least one team member approval
- All tests must pass from persistent containers
- Documentation must be updated
- No breaking changes without team discussion

### **Testing Standards with Persistent Containers**

#### **Before Committing**
```bash
# Ensure containers are running
docker compose up -d

# Validate test data
docker compose exec ash-thrash python cli.py validate data

# Run quick test
docker compose exec ash-thrash python cli.py test quick

# Check API functionality
docker compose exec ash-thrash python cli.py api health
```

#### **Before Releasing**
```bash
# Full comprehensive test from persistent container
docker compose exec ash-thrash python cli.py test comprehensive

# Docker build test
docker compose down
docker compose build
docker compose up -d
docker compose exec ash-thrash python cli.py test comprehensive
```

### **Documentation Standards**

- Update README.md for user-facing changes
- Update team guide for workflow changes
- Update API documentation for API changes
- Include examples for new features

---

## 🆘 Team Support & Escalation

### **Support Channels**

#### **Level 1: Self-Service with Persistent Containers**
- Check this team guide
- Review troubleshooting documentation
- Search GitHub Issues
- Test from persistent containers: `docker compose exec ash-thrash python cli.py validate setup`

#### **Level 2: Team Discussion**
- Post in #ash-development Discord channel
- Tag relevant team members
- Provide logs: `docker compose logs`

#### **Level 3: Escalation**
- Create GitHub Issue for bugs
- Tag @Crisis-Team for safety issues
- Emergency: Direct message team leads

### **Common Team Issues with Persistent Containers**

#### **"Tests Failing After NLP Update"**
```bash
# 1. Check NLP connectivity from persistent container
docker compose exec ash-thrash python cli.py api health

# 2. Run baseline test
docker compose exec ash-thrash python cli.py test category definite_high

# 3. If failing, revert NLP changes temporarily
# 4. Investigate tuning requirements
# 5. Apply gradual threshold adjustments
```

#### **"Containers Won't Start or Keep Restarting"**
```bash
# 1. Check container status
docker compose ps
docker compose logs

# 2. Check system resources
docker stats
free -h

# 3. Restart services cleanly
docker compose down
docker compose up -d

# 4. If still failing, rebuild
docker compose down
docker compose build
docker compose up -d
```

#### **"Cannot Execute Commands in Containers"**
```bash
# 1. Check if containers are running
docker compose ps

# 2. Ensure containers are healthy
docker compose exec ash-thrash echo "Container accessible"

# 3. Restart if needed
docker compose restart ash-thrash

# 4. Check logs for startup issues
docker compose logs ash-thrash
```

---

## 📋 Team Checklists

### **New Team Member Onboarding**

- [ ] Repository access granted
- [ ] Discord channels joined (#ash-testing, #ash-development)
- [ ] Persistent container environment setup: `docker compose up -d`
- [ ] First successful test run: `docker compose exec ash-thrash python cli.py test quick`
- [ ] Team workflow training completed
- [ ] Emergency procedures understood

### **Weekly Team Tasks with Persistent Containers**

- [ ] Containers running and healthy: `docker compose ps`
- [ ] Comprehensive test run: `docker compose exec ash-thrash python cli.py test comprehensive`
- [ ] Results reviewed and documented
- [ ] Discord notifications monitored
- [ ] GitHub Issues triaged
- [ ] Performance metrics reviewed
- [ ] Any tuning applied and validated

### **Pre-Deployment Checklist**

- [ ] All tests passing from persistent containers
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Docker images built successfully
- [ ] Staging environment validated with persistent containers
- [ ] Team notification sent
- [ ] Rollback plan confirmed

### **Incident Response Checklist**

- [ ] Issue severity assessed
- [ ] Team leads notified
- [ ] Immediate mitigation applied
- [ ] Root cause investigation started from persistent containers
- [ ] Community impact evaluated
- [ ] Fix implemented and tested: `docker compose exec ash-thrash python cli.py test comprehensive`
- [ ] Post-incident review scheduled

---

## 🎯 Team Goals & Metrics

### **Primary Goals**

1. **100% High Crisis Detection**: Never miss suicidal ideation
2. **95% False Positive Prevention**: Minimize normal conversation flags
3. **<5 Minute Response Time**: Quick issue resolution with persistent containers
4. **Daily Testing Coverage**: Consistent validation schedule

### **Team KPIs with Persistent Containers**

- **Test Execution**: 7+ comprehensive tests per week from persistent containers
- **Issue Resolution**: <24 hours for critical issues
- **Accuracy Improvement**: Monthly trending upward
- **Community Safety**: Zero missed crisis incidents

### **Success Metrics**

- **Technical Excellence**: Clean code, comprehensive tests, good documentation
- **Team Collaboration**: Effective communication, shared responsibility
- **Community Impact**: Safer Discord environment, effective crisis response
- **Continuous Improvement**: Regular process refinement, learning culture

---

## 🔄 Persistent Container Best Practices

### **Container Lifecycle Management**

#### **Starting Your Work Session**
```bash
# 1. Always check container status first
docker compose ps

# 2. Start containers if not running
docker compose up -d

# 3. Verify health before proceeding
docker compose exec ash-thrash python cli.py validate setup
```

#### **During Development**
```bash
# Test changes immediately without container restarts
docker compose exec ash-thrash python cli.py test quick

# Check logs in real-time
docker compose logs -f ash-thrash

# Execute multiple commands efficiently
docker compose exec ash-thrash bash
# Now you're inside the container for multiple commands
```

#### **Ending Your Work Session**
```bash
# Leave containers running for team members
# Only stop if you're the last person working
docker compose ps  # Check if others might be using

# Optional: Stop containers if needed
docker compose down
```

### **Resource Management**

#### **Monitoring Container Health**
```bash
# Check resource usage
docker stats ash-thrash ash-thrash-api

# Monitor disk usage
docker system df

# Clean up if needed (containers will restart automatically)
docker system prune -f
```

#### **Troubleshooting Container Issues**
```bash
# Quick container restart (preserves volumes)
docker compose restart ash-thrash

# Full restart with clean state
docker compose down
docker compose up -d

# View startup logs
docker compose logs ash-thrash
```

---

## 📚 Advanced Team Workflows

### **Collaborative Testing Sessions**

#### **Team Testing Sprint**
```bash
# Coordinator starts session
docker compose up -d

# Team members can immediately join
docker compose exec ash-thrash python cli.py test category definite_high

# Real-time results sharing via Discord webhooks
# No waiting for container startups
```

#### **Parallel Testing Workflow**
```bash
# Developer 1: Test new features
docker compose exec ash-thrash python cli.py test quick

# Developer 2: Validate existing functionality  
docker compose exec ash-thrash python cli.py test category definite_none

# Operations: Monitor system health
docker compose exec ash-thrash python cli.py api health
```

### **Emergency Response Procedures**

#### **Critical Bug Hotfix Workflow**
```bash
# 1. Immediate assessment (containers already running)
docker compose exec ash-thrash python cli.py test category definite_high

# 2. Apply emergency fix
# Edit code files

# 3. Test fix immediately (no container rebuild needed)
docker compose exec ash-thrash python cli.py test category definite_high

# 4. Deploy to production if tests pass
```

#### **Performance Issue Investigation**
```bash
# 1. Real-time monitoring
docker stats ash-thrash ash-thrash-api

# 2. Test performance from container
docker compose exec ash-thrash time python cli.py test quick

# 3. Check network connectivity
docker compose exec ash-thrash ping 10.20.30.253

# 4. Review logs without stopping services
docker compose logs ash-thrash | grep -i error
```

---

## 📊 Team Metrics and Reporting

### **Weekly Team Standup Data**

#### **Gathering Metrics**
```bash
# Get test execution count for the week
docker compose exec ash-thrash python cli.py results history --days 7

# Check system uptime
docker compose exec ash-thrash python cli.py api health

# Review error rates
docker compose logs ash-thrash | grep -i error | wc -l
```

#### **Performance Trends**
```bash
# Compare this week vs last week
docker compose exec ash-thrash python cli.py results compare --week-over-week

# Check accuracy trends
docker compose exec ash-thrash python cli.py test comprehensive --output json > this_week.json
```

### **Monthly Team Review**

#### **Comprehensive Analysis**
```bash
# Generate monthly report
docker compose exec ash-thrash python cli.py results report --month

# Export data for analysis
docker compose cp ash-thrash:/app/results ./monthly_backup/

# Review and document findings
# Update team processes based on insights
```

---

## 🎓 Training and Knowledge Sharing

### **New Developer Onboarding Session**

#### **Hands-on Training Agenda**
1. **Environment Setup** (10 minutes)
   ```bash
   docker compose up -d
   docker compose exec ash-thrash python cli.py validate setup
   ```

2. **Basic Testing** (15 minutes)
   ```bash
   docker compose exec ash-thrash python cli.py test quick
   docker compose exec ash-thrash python cli.py test category definite_high
   ```

3. **API Integration** (10 minutes)
   ```bash
   curl http://localhost:8884/health
   docker compose exec ash-thrash python cli.py api health
   ```

4. **Troubleshooting Practice** (15 minutes)
   ```bash
   docker compose logs ash-thrash
   docker compose exec ash-thrash python cli.py validate data
   ```

### **Knowledge Transfer Sessions**

#### **Monthly Technical Deep Dive**
- **Topic**: Advanced testing strategies
- **Demo**: Live testing with persistent containers
- **Hands-on**: Each team member runs tests
- **Discussion**: Results analysis and improvement ideas

#### **Quarterly Process Review**
- **Evaluate**: Current persistent container workflow
- **Identify**: Pain points and inefficiencies
- **Implement**: Process improvements
- **Document**: Updated procedures

---

**The Alphabet Cartel team's dedication to crisis detection accuracy directly protects our community members. Every test run, every tuning adjustment, and every code improvement contributes to saving lives. With persistent containers, we can respond faster and test more efficiently than ever before.**

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Building safer communities together with always-ready testing infrastructure.* 👥🛡️🐳