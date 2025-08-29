# Ash-Thrash v3.1 - Comprehensive Crisis Detection Testing Suite

**Advanced testing system for tuning Ash NLP crisis detection accuracy**

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da)](https://discord.gg/alphabetcartel)
[![Website](https://img.shields.io/badge/Website-alphabetcartel.org-blue)](http://alphabetcartel.org)
[![GitHub](https://img.shields.io/badge/Version-v3.0-green)](https://github.com/the-alphabet-cartel/ash-thrash)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io-blue)](https://github.com/orgs/the-alphabet-cartel/packages/container/package/ash-thrash)

## 🚀 What is Ash-Thrash v3.1?

Ash-Thrash v3.1 is a **comprehensive testing suite** designed to validate and tune the Ash NLP crisis detection system.

### Key Features

- **🧪 350 Test Phrases**: Carefully curated phrases across 7 crisis categories
- **🔧 NLP Tuning Suggestions**: Automated recommendations for improving detection accuracy
- **🎯 Goal-Based Testing**: Pass/fail criteria based on safety-first principles

## 🎯 Testing Categories & Goals

### Definite Categories (Exact Match Required)
- **🚨 Definite High Crisis** (50 phrases) - **98% target** - Safety critical suicidal ideation
- **⚠️ Definite Medium Crisis** (50 phrases) - **80% target** - Severe mental health episodes  
- **ℹ️ Definite Low Crisis** (50 phrases) - **80% target** - Mild to moderate distress
- **✅ Definite None** (50 phrases) - **90% target** - Normal conversation (prevent false positives)

### Maybe Categories (Bidirectional Acceptable)
- **🔄 Maybe High/Medium** (50 phrases) - **90% target** - Either high OR medium acceptable
- **🔄 Maybe Medium/Low** (50 phrases) - **80% target** - Either medium OR low acceptable  
- **🔄 Maybe Low/None** (50 phrases) - **90% target** - Either low OR none acceptable

## 🏗️ Architecture Overview

### Core Components
- **Testing Engine**: 350 phrase validation with bidirectional category support

## 🔧 NLP Tuning Integration

Ash-Thrash automatically generates tuning suggestions based on test results:

### Example Tuning Output
```
🔧 TUNING SUGGESTIONS:
🚨 HIGH PRIORITY: definite_high only 85.0% (need 100.0%). 
   Consider lowering NLP_HIGH_CRISIS_THRESHOLD from 0.8 to 0.7

⚠️ FALSE POSITIVE ISSUE: definite_none only 88.0% (need 95.0%). 
   Consider raising NLP_NONE_THRESHOLD from 0.3 to 0.4

📈 TUNING NEEDED: maybe_high_medium only 75.0% (need 90.0%). 
   Review threshold settings
```

### Applying Suggestions

1. **Manual Tuning**: Update ash-nlp's `.env` file with suggested threshold values
2. **Iterative Testing**: Re-run tests after adjustments to validate improvements
3. **Performance Tracking**: Use historical data to track tuning effectiveness

## 🔌 Integration with Ash Ecosystem

### Ash-Bot Integration
Ash-Thrash uses the **exact same API calls** that ash-bot makes to ash-nlp, ensuring test results reflect real-world Discord behavior.

### Ash-NLP Integration
Direct communication with ash-nlp using identical message preprocessing and analysis pipeline.

## 📈 Performance Expectations

### Test Duration Estimates
- **Comprehensive Test**: ~3 minutes (350 phrases)
- **Quick Validation**: ~30 seconds (50 phrases)  
- **Category Test**: ~25 seconds (50 phrases)

## 🤝 Contributing

We welcome contributions to improve Ash-Thrash! Here's how to help:

## 📞 Support & Community

### Getting Help
- **Technical Issues**: [GitHub Issues](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Community Support**: [Discord Server](https://discord.gg/alphabetcartel)

### Community Guidelines
- **Safety First**: Crisis detection accuracy is paramount
- **Inclusive Language**: LGBTQIA+ friendly community
- **Collaborative**: Help others and share knowledge
- **Respectful**: Treat everyone with dignity

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

*Crisis detection testing, one phrase at a time.* 🧪✨