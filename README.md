<!-- ash-thrash/README.md -->
<!--
README for Ash-Thrash Service
FILE VERSION: v3.1-3a-1
LAST MODIFIED: 2025-09-01
CLEAN ARCHITECTURE: v3.1
-->
# Ash-Thrash v3.1 - Comprehensive Crisis Detection Testing Suite

**Advanced testing system for tuning Ash NLP crisis detection accuracy**

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da)](https://discord.gg/alphabetcartel)
[![Website](https://img.shields.io/badge/Website-alphabetcartel.org-blue)](http://alphabetcartel.org)
[![GitHub](https://img.shields.io/badge/Version-v3.1-green)](https://github.com/the-alphabet-cartel/ash-thrash)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io-blue)](https://github.com/orgs/the-alphabet-cartel/packages/container/package/ash-thrash)

## 🚀 What is Ash-Thrash v3.1?

Ash-Thrash v3.1 is a **production-ready comprehensive testing suite** designed to validate and tune the Ash NLP crisis detection system with advanced tuning intelligence and automated threshold recommendations.

### ✨ Key Features

- **🧪 345 Test Phrases**: Carefully curated phrases across 7 crisis categories
- **🧠 Advanced Tuning Intelligence**: AI-driven threshold recommendations with confidence levels
- **📊 Automated Reporting**: Persistent markdown reports and JSON analysis files
- **🎯 Safety-First Design**: False negative weighting prioritizes community safety
- **🔄 Bidirectional Testing**: Flexible acceptance criteria for edge cases
- **⚡ Production Ready**: Clean Architecture v3.1 compliant with comprehensive logging

## 🎯 Testing Categories & Goals

### Definite Categories (Exact Match Required)
- **🚨 Definite High Crisis** (50 phrases) - **98% target** - Safety critical suicidal ideation
- **⚠️ Definite Medium Crisis** (50 phrases) - **85% target** - Severe mental health episodes  
- **⚡ Definite Low Crisis** (50 phrases) - **85% target** - Mild to moderate distress
- **✅ Definite None** (50 phrases) - **95% target** - Normal conversation (prevent false positives)

### Maybe Categories (Bidirectional Acceptable)
- **🔄 Maybe High/Medium** (50 phrases) - **90% target** - Either high OR medium acceptable
- **🔄 Maybe Medium/Low** (50 phrases) - **85% target** - Either medium OR low acceptable  
- **🔄 Maybe Low/None** (45 phrases) - **90% target** - Either low OR none acceptable

## 🏗️ System Architecture

### Core Components
```
ash-thrash/
├── main.py                       # Primary execution entry point
├── analyze.py                    # Standalone analysis script
├── managers/                     # Clean Architecture v3.1 managers
|   ├── unified_config.py         # Centralized configuration
|   ├── test_engine.py            # Core testing engine
|   ├── nlp_client.py             # NLP server integration
|   ├── results_manager.py        # Test results handling
|   ├── analyze_results.py        # Results analysis & reporting
|   └── tuning_suggestions.py     # Advanced tuning intelligence
└── config/                       # JSON configuration files
    ├── test_phrases/             # Test phrase datasets
    ├── results/                  # Test results and analysis
    └── reports/                  # Generated markdown reports
```

### 🎭 Execution Methods

#### Comprehensive Testing
```bash
# Run all categories with full reporting and tuning intelligence
docker compose exec ash-thrash python main.py
```

#### Category-Specific Testing
```bash
# Test specific categories
docker compose exec ash-thrash python main.py --categories definite_high definite_medium

# Single category analysis
docker compose exec ash-thrash python analyze.py --category definite_high
```

## 🧠 Advanced Tuning Intelligence

Ash-Thrash v3.1 provides **intelligent threshold recommendations** based on test results:

### Automated Analysis Features
- **🎯 Threshold Mapping**: Maps failures to specific NLP environment variables
- **📈 Confidence Levels**: HIGH/MEDIUM/LOW confidence recommendations
- **⚠️ Risk Assessment**: CRITICAL/MODERATE/LOW risk classifications
- **🔄 Boundary Testing**: Suggests test points for optimal threshold discovery
- **📋 Implementation Priority**: Ordered recommendations with rollback plans

### Example Tuning Output
```
🔧 INTELLIGENT TUNING RECOMMENDATIONS:

🚨 PRIORITY 1 (CRITICAL RISK): definite_high 74.0% → 98.0% target
   Recommendation: NLP_THRESHOLD_MAJORITY_ENSEMBLE_CRITICAL: 0.650 → 0.656
   Confidence: HIGH | Risk: CRITICAL | Test Points: [0.654, 0.656, 0.658]

⚠️ PRIORITY 2 (MODERATE RISK): definite_medium 58.0% → 85.0% target
   Recommendation: NLP_THRESHOLD_MAJORITY_CRISIS_TO_HIGH: 0.450 → 0.475  
   Confidence: MEDIUM | Risk: MODERATE | Test Points: [0.470, 0.475, 0.480]

📊 Generated Files:
   • recommended_thresholds_2025-08-31_12-05-28.env
   • tuning_analysis_2025-08-31_12-05-28.json
   • latest_run_summary.md
```

### Applying Tuning Recommendations

1. **Review Generated Files**: Check `/app/reports/` for recommendation files
2. **Backup Current Settings**: Save existing NLP server configuration
3. **Implement Priority Changes**: Start with CRITICAL and MODERATE risk items
4. **Iterative Testing**: Re-run Ash-Thrash after each change
5. **Monitor Performance**: Track improvements across test runs

## 📊 Comprehensive Reporting

### Automated Report Generation
- **📈 Latest Run Summary**: Complete test results with visual indicators
- **🎯 Threshold Recommendations**: Specific implementation guidance
- **📋 Historical Performance**: Trend analysis across multiple runs
- **🔍 JSON Analysis Files**: Detailed data for programmatic access

### Report Locations
```
reports/
    ├── latest_run_summary.md          # Latest comprehensive results
    ├── threshold_recommendations.md    # Implementation guidance
    ├── historical_performance.md       # Trend analysis
    └── recommended_thresholds_*.env   # Generated environment files
```

## 🔌 Integration with Ash Ecosystem

### Ash-Bot Integration
Ash-Thrash uses the **exact same API calls** that ash-bot makes to ash-nlp, ensuring test results accurately reflect real-world Discord behavior.

### Ash-NLP Integration
- **Direct Communication**: Uses identical message preprocessing and analysis pipeline
- **Environment Mapping**: Maps test results to specific NLP threshold variables
- **Ensemble Mode Support**: Handles consensus, majority, and weighted ensemble modes

## ⚡ Performance & Safety

### Safety-First Principles
- **False Negative Weighting**: False negatives weighted 3x false positives
- **Early Termination**: Configurable halt on performance degradation
- **Community Focus**: LGBTQIA+ community mental health safety prioritized

### Performance Expectations
- **Test Duration**: ~2-3 minutes for comprehensive suite (345 phrases)
- **Category Testing**: ~30-45 seconds per category
- **Concurrent Execution**: Configurable concurrent test limits
- **Resource Efficient**: Minimal memory footprint with intelligent caching

## 🚀 Quick Start Guide

### Prerequisites
- Docker and Docker Compose
- Ash-NLP server running at `172.20.0.11:8881`
- Proper environment configuration

### Basic Usage
```bash
# 1. Start the service
docker compose up -d ash-thrash

# 2. Run comprehensive testing
docker compose exec ash-thrash python main.py

# 3. View results
docker compose exec ash-thrash cat reports/latest_run_summary.md

# 4. Apply tuning recommendations
# Review generated .env files and implement changes to NLP server
```

### Environment Configuration
Key environment variables (see `.env.template` for complete list):
```bash
GLOBAL_NLP_API_URL=http://172.20.0.11:8881
GLOBAL_LEARNING_SYSTEM_ENABLED=false  # Disable during testing
THRASH_MAX_CONCURRENT_TESTS=3
THRASH_ENABLE_EARLY_TERMINATION=true
```

## 📞 Support & Community

### Getting Help
- **Technical Issues**: [GitHub Issues](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Community Support**: [Discord Server](https://discord.gg/alphabetcartel)
- **Documentation**: Check `/docs/` directory for technical and team guides

### Community Guidelines
- **Safety First**: Crisis detection accuracy is paramount
- **Inclusive Language**: LGBTQIA+ friendly community
- **Collaborative Development**: Clean Architecture v3.1 standards
- **Respectful Communication**: Treat everyone with dignity

## 🎯 System Status

### Current Version: v3.1 (Production Ready)
- ✅ **Complete Testing Suite**: All 345 test phrases across 7 categories
- ✅ **Advanced Tuning Intelligence**: AI-driven threshold recommendations
- ✅ **Comprehensive Reporting**: Automated analysis and persistent files
- ✅ **Clean Architecture Compliance**: Professional-grade codebase
- ✅ **Production Deployment**: Ready for NLP server optimization

### Ready for Production Use
- **Testing**: Comprehensive validation of crisis detection accuracy
- **Tuning**: Intelligent threshold optimization recommendations
- **Monitoring**: Historical performance tracking and trend analysis
- **Integration**: Seamless compatibility with existing Ash ecosystem

## 📄 License

This project is part of The Alphabet Cartel's open-source Ash Bot ecosystem.
Licensed under GNU GENERAL PUBLIC LICENSE version 3.

## 🙏 Acknowledgments

**Built with ❤️ for chosen family by The Alphabet Cartel**

- **Community**: Our LGBTQIA+ Discord members who help test and improve the system
- **Contributors**: Developers who contribute code, documentation, and feedback  
- **Mental Health Advocates**: Professionals who guide our safety-first approach
- **Open Source**: The amazing Python and FastAPI communities

---

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Crisis detection testing and tuning, powered by advanced AI intelligence.* 🧪🧠✨