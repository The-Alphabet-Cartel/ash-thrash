<!-- ash-thrash/docs/team/team_guide.md -->
<!--
Team Guide for Ash-Thrash Service
FILE VERSION: v3.1-3a-1
LAST MODIFIED: 2025-09-01
CLEAN ARCHITECTURE: v3.1
-->
# Ash-Thrash v3.1 Team Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Project**: Ash-Thrash v3.1  
**Community**: The Alphabet Cartel - [Discord](https://discord.gg/alphabetcartel) | [Website](http://alphabetcartel.org)  
**FILE VERSION**: v3.1-3a-1  
**LAST UPDATED**: 2025-09-01  
**CLEAN ARCHITECTURE**: v3.1

---

## 🎯 Team Guide Purpose

This guide provides The Alphabet Cartel team members with everything needed to effectively use, maintain, and contribute to the Ash-Thrash crisis detection testing system.

## 🌟 What is Ash-Thrash?

Ash-Thrash v3.1 is our **production-ready comprehensive testing suite** that validates and tunes the Ash NLP crisis detection system. It ensures our community receives accurate mental health crisis detection while providing intelligent recommendations for system optimization.

### Why It Matters
- **Community Safety**: Validates crisis detection accuracy for LGBTQIA+ community members
- **System Optimization**: Provides AI-driven tuning recommendations
- **Quality Assurance**: Maintains high standards for mental health support systems
- **Transparency**: Offers clear reporting on system performance

## 👥 Team Roles & Responsibilities

### 🏛️ Project Maintainers
- **Responsibility**: Overall project direction, architectural decisions, and code reviews
- **Access Level**: Full repository access, deployment permissions
- **Key Tasks**: 
  - Review and approve Pull Requests
  - Manage releases and versioning
  - Coordinate with other Ash ecosystem projects

### 🔧 Developers & Contributors
- **Responsibility**: Feature development, bug fixes, documentation updates
- **Access Level**: Repository contributor access
- **Key Tasks**:
  - Follow Clean Architecture v3.1 standards
  - Implement new test categories or features
  - Maintain and improve existing functionality

### 🧪 QA & Testing Team
- **Responsibility**: System validation, test phrase curation, and result analysis
- **Access Level**: Read access + testing reports
- **Key Tasks**:
  - Review test results and reports
  - Suggest new test phrases
  - Validate tuning recommendations

### 🏥 Mental Health Advisors
- **Responsibility**: Guide safety-first principles and validate test phrases
- **Access Level**: Consultation and review
- **Key Tasks**:
  - Review test phrase content for accuracy
  - Validate safety-first approaches
  - Provide guidance on crisis detection priorities

## 🚀 Daily Usage Guide

### 📊 Running Regular Tests

#### Comprehensive Testing (Weekly Recommended)
```bash
# Start the container
docker compose up -d ash-thrash

# Run comprehensive test suite
docker compose exec ash-thrash python main.py

# View the results
docker compose exec ash-thrash cat reports/latest_run_summary.md
```

#### Quick Category Testing (Daily/As Needed)
```bash
# Test high-priority categories only
docker compose exec ash-thrash python main.py --categories definite_high definite_medium

# Analyze specific category performance
docker compose exec ash-thrash python analyze.py --category definite_high
```

### 📈 Understanding Results

#### Pass/Fail Criteria
- **Definite Categories**: Exact match required (high=high, medium=medium, etc.)
- **Maybe Categories**: Bidirectional acceptance (high/medium accepts either)
- **Target Thresholds**: Each category has specific pass rate targets

#### Key Metrics to Monitor
- **Overall Pass Rate**: Should be >85% for production readiness
- **False Negatives**: Critical for safety - weighted 3x more heavily
- **Category-Specific Performance**: Monitor trends over time

#### Reading Reports
```
📊 COMPREHENSIVE TEST RESULTS - 2025-09-01 12:05:28

🎯 OVERALL PERFORMANCE: 62.9% (217/345 passed, 128 failed)

📈 CATEGORY BREAKDOWN:
✅ maybe_high_medium: 100.0% (50/50) [Target: 90.0%] - EXCELLENT
✅ maybe_medium_low: 98.0% (49/50) [Target: 85.0%] - EXCELLENT  
⚠️ definite_high: 74.0% (37/50) [Target: 98.0%] - NEEDS ATTENTION
❌ definite_low: 4.0% (2/50) [Target: 85.0%] - CRITICAL ISSUE
```

### 🔧 Applying Tuning Recommendations

#### Step-by-Step Process
1. **Review Generated Files**: Check `/app/reports/` after test completion
2. **Understand Recommendations**: Read confidence levels and risk assessments
3. **Backup Current Settings**: Save existing NLP server configuration
4. **Implement Changes**: Apply recommendations in priority order
5. **Test & Validate**: Re-run Ash-Thrash to verify improvements

#### Example Implementation
```bash
# 1. Review recommendations
docker compose exec ash-thrash cat reports/threshold_recommendations.md

# 2. Apply recommended settings to NLP server
# Copy values from generated .env files to ash-nlp server

# 3. Restart NLP server with new settings
docker compose restart ash-nlp

# 4. Validate changes
docker compose exec ash-thrash python main.py

# 5. Compare results
docker compose exec ash-thrash cat reports/historical_performance.md
```

## 📋 Team Workflows

### 🔄 Weekly Testing Routine

#### Monday: Comprehensive Testing
- Run full test suite after weekend changes
- Review overall system performance
- Document any significant performance changes

#### Wednesday: Category Focus Testing
- Test specific categories showing issues
- Validate recent tuning changes
- Update test phrases if needed

#### Friday: Performance Review
- Analyze weekly performance trends
- Plan any needed improvements
- Coordinate with development team

### 🚨 Issue Response Workflow

#### Performance Degradation (Pass rate <70%)
1. **Immediate Action**: Document current performance
2. **Investigation**: Check recent NLP server changes
3. **Communication**: Alert team via Discord
4. **Resolution**: Apply tuning recommendations or rollback
5. **Validation**: Confirm resolution with follow-up testing

#### Critical Safety Issues (High false negatives)
1. **Emergency Response**: Prioritize immediately
2. **Analysis**: Focus on `definite_high` category failures
3. **Tuning**: Apply CRITICAL priority recommendations
4. **Validation**: Continuous testing until resolved
5. **Documentation**: Record incident and resolution

### 📝 Documentation Updates

#### When to Update Documentation
- New features added to the system
- Changes in testing procedures
- Updates to tuning recommendations
- Community feedback incorporation

#### Documentation Standards
- Follow Clean Architecture v3.1 file versioning
- Include version headers in all files
- Use inclusive language throughout
- Link to Discord and website in all public docs

## 🛠️ Maintenance Guidelines

### 🔍 Regular System Health Checks

#### Weekly Health Check Checklist
- [ ] Comprehensive test run completed successfully
- [ ] All categories meeting target thresholds
- [ ] No critical safety issues identified
- [ ] Reports generating correctly
- [ ] Docker containers running properly

#### Monthly Deep Review
- [ ] Analyze historical performance trends
- [ ] Review and update test phrases as needed
- [ ] Validate tuning recommendation accuracy
- [ ] Update documentation for any process changes
- [ ] Coordinate with broader Ash ecosystem updates

### 🔄 Test Phrase Management

#### Adding New Test Phrases
1. **Category Selection**: Choose appropriate category file
2. **Content Review**: Ensure phrases are appropriate and realistic
3. **Mental Health Validation**: Get advisor approval for crisis-related content
4. **Testing**: Validate new phrases work correctly
5. **Documentation**: Update totals and category descriptions

#### Updating Existing Phrases
1. **Performance Analysis**: Identify consistently problematic phrases
2. **Content Review**: Ensure updates maintain testing validity
3. **Change Tracking**: Document modifications for historical tracking
4. **Validation Testing**: Confirm updates improve testing accuracy

## 🔐 Security & Safety Considerations

### 🛡️ Data Security
- **Test Phrases**: No real user data in test phrases
- **Results**: Test results contain no personal information
- **Server Access**: Limited to team members with appropriate access

### 🏥 Mental Health Safety
- **Test Content**: All test phrases reviewed by mental health advisors
- **False Negative Priority**: System weighted to avoid missing real crises
- **Community Focus**: Specialized attention to LGBTQIA+ community needs
- **Regular Review**: Ongoing validation of safety-first principles

### 🔒 Access Control
- **Repository Access**: Managed through GitHub organization permissions
- **Server Access**: Docker container access limited to authorized users
- **Report Access**: Results available to appropriate team members

## 📞 Getting Help & Support

### 🆘 Emergency Issues
**Critical system failures or safety concerns**
- **Discord**: Post in #tech-emergencies channel
- **Direct Contact**: Message project maintainers directly
- **Response Time**: Within 2 hours during business hours

### 🐛 Bug Reports & Issues
**Non-critical problems or improvement suggestions**
- **GitHub Issues**: [Create detailed issue](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Discord**: Post in #ash-development channel
- **Response Time**: Within 24-48 hours

### ❓ Questions & Discussion
**General questions or collaboration**
- **Discord**: #ash-development channel
- **Team Meetings**: Weekly development sync
- **Documentation**: Check `/docs/` directory first

### 📚 Learning Resources
- **Clean Architecture Charter**: `/docs/clean_architecture_charter.md`
- **Technical Guide**: `/docs/tech/technical_guide.md`
- **Implementation Plan**: `/docs/implementation_plan.md`

## 🎯 Best Practices

### 💡 Testing Best Practices
- **Regular Schedule**: Maintain consistent testing routine
- **Document Changes**: Record all tuning modifications
- **Monitor Trends**: Watch for performance patterns over time
- **Safety First**: Prioritize false negative reduction

### 🤝 Collaboration Best Practices
- **Inclusive Language**: Use "we" and "our" in all communications
- **Clear Communication**: Provide context and details in reports
- **Respectful Feedback**: Constructive and supportive approach
- **Community Focus**: Remember we serve LGBTQIA+ community needs

### 📈 Development Best Practices
- **Clean Architecture**: Follow v3.1 standards strictly
- **Version Control**: Use proper file versioning and Git practices
- **Testing**: Validate all changes with comprehensive testing
- **Documentation**: Keep all docs current and accessible

---

## 🌈 Community Impact

The Alphabet Cartel's Ash-Thrash system directly supports our LGBTQIA+ community by ensuring accurate, reliable mental health crisis detection. Every test we run, every improvement we make, and every tuning recommendation we implement contributes to potentially life-saving support for chosen family members.

**Remember**: We're not just testing software - we're validating systems that support real people during their most vulnerable moments. Our work matters, and our community depends on our diligence and care.

---

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Built with ❤️ for chosen family by The Alphabet Cartel* 🌈✨