# Ash-Thrash v5.0

**Crisis Detection Testing Suite for [The Alphabet Cartel](https://discord.gg/alphabetcartel) Discord Community**

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/the-alphabet-cartel/ash-thrash)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/alphabetcartel)

---

## 🎯 Mission

```
MISSION - NEVER TO BE VIOLATED:
    Validate  → Verify crisis detection accuracy through live Ash-NLP integration testing
    Challenge → Stress test the system with edge cases and adversarial scenarios
    Guard     → Prevent regressions that could compromise detection reliability
    Protect   → Safeguard our LGBTQIA+ community through rigorous quality assurance
```

---

## 📋 Overview

Ash-Thrash is the comprehensive testing suite for the Ash Crisis Detection Ecosystem. It validates the accuracy and reliability of Ash-NLP's crisis classification through extensive test scenarios, regression detection, and performance benchmarking.

### Key Capabilities

- **525+ Test Scenarios**: Comprehensive coverage across all crisis severity levels
- **Real API Testing**: Live integration with Ash-NLP (no mocks)
- **Flexible Tolerance System**: Accounts for human communication variability
- **Regression Detection**: Baseline comparison to catch accuracy degradation
- **Performance Benchmarking**: Latency and throughput validation
- **Detailed Reporting**: JSON, HTML, and Discord webhook notifications

---

## 🏗️ Architecture

Ash-Thrash is part of the larger Ash ecosystem:

| Component | Description | Repository |
|-----------|-------------|------------|
| **Ash** | Ecosystem coordination | [ash](https://github.com/the-alphabet-cartel/ash) |
| **Ash-NLP** | Crisis detection NLP server | [ash-nlp](https://github.com/the-alphabet-cartel/ash-nlp) |
| **Ash-Bot** | Discord bot frontend | [ash-bot](https://github.com/the-alphabet-cartel/ash-bot) |
| **Ash-Dash** | Admin dashboard | [ash-dash](https://github.com/the-alphabet-cartel/ash-dash) |
| **Ash-Thrash** | Testing suite (this repo) | [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash) |
| **Ash-Vault** | Archive & backup | [ash-vault](https://github.com/the-alphabet-cartel/ash-vault) |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Access to Ash-NLP server (default: 10.20.30.253:30880)
- (Optional) Discord webhook for notifications

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/the-alphabet-cartel/ash-thrash.git
   cd ash-thrash
   ```

2. **Configure environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Set up secrets** (optional):
   ```bash
   # Discord webhook for notifications
   echo "https://discord.com/api/webhooks/..." > secrets/ash_thrash_discord_alert_token
   chmod 600 secrets/ash_thrash_discord_alert_token
   ```

4. **Start the service**:
   ```bash
   docker compose up -d
   ```

5. **View logs**:
   ```bash
   docker compose logs -f ash-thrash
   ```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `THRASH_ENVIRONMENT` | `production` | Environment (production, testing, development) |
| `THRASH_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `THRASH_LOG_FORMAT` | `human` | Log format (human for colorized, json for structured) |
| `THRASH_NLP_HOST` | `10.20.30.253` | Ash-NLP server hostname |
| `THRASH_NLP_PORT` | `30880` | Ash-NLP server port |
| `THRASH_NLP_TIMEOUT` | `30` | Request timeout in seconds |

See [.env.template](.env.template) for the complete list.

### Accuracy Thresholds

| Category | Default Target | Description |
|----------|---------------|-------------|
| High/Critical | 95% | Immediate crisis detection |
| Medium | 85% | Moderate distress detection |
| Low | 85% | Mild distress detection |
| None | 95% | False positive prevention |
| Edge Cases | 70% | Ambiguous scenarios |
| Specialty | 75% | Context-specific tests |

---

## 📁 Project Structure

```
ash-thrash/
├── src/
│   ├── config/
│   │   ├── default.json          # Default configuration
│   │   ├── testing.json          # Testing overrides
│   │   ├── production.json       # Production overrides
│   │   └── phrases/              # Test phrase definitions
│   │       ├── critical_high_priority.json
│   │       ├── medium_priority.json
│   │       ├── low_priority.json
│   │       ├── none_priority.json
│   │       ├── edge_cases/
│   │       └── specialty/
│   ├── managers/
│   │   ├── config_manager.py     # Configuration loading
│   │   ├── secrets_manager.py    # Docker secrets handling
│   │   ├── logging_config_manager.py  # Colorized logging
│   │   ├── nlp_client_manager.py # Ash-NLP API client
│   │   └── phrase_loader_manager.py   # Test phrase loading
│   └── validators/               # (Phase 2)
├── tests/                        # Unit and integration tests
├── reports/                      # Generated test reports
├── logs/                         # Application logs
├── docs/                         # Documentation
├── main.py                       # Application entry point
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Orchestration
└── requirements.txt              # Python dependencies
```

---

## 📊 Development Status

### Phase Progress

| Phase | Name | Status |
|-------|------|--------|
| 1 | Foundation | ✅ Complete |
| 2 | Test Execution Engine | 📋 Planned |
| 3 | Analysis & Reporting | 📋 Planned |
| 4 | Test Data Population | 📋 Planned |
| 5 | Performance & Stress Testing | 📋 Planned |

### Phase 1 Deliverables

- ✅ ConfigManager with JSON + environment variable support
- ✅ SecretsManager for Docker secrets
- ✅ LoggingConfigManager with colorized output (Charter v5.2.1)
- ✅ NLPClientManager with retry logic
- ✅ PhraseLoaderManager for test data
- ✅ Docker deployment configuration
- ✅ Complete documentation

---

## 🧪 Testing

```bash
# Run unit tests
docker exec ash-thrash pytest tests/ -v

# Run with coverage
docker exec ash-thrash pytest tests/ --cov=src --cov-report=html
```

---

## 🏳️‍🌈 Community

**The Alphabet Cartel** is an LGBTQIA+ Discord community centered around gaming, political discourse, activism, and societal advocacy.

- 🌐 **Website**: [alphabetcartel.org](https://alphabetcartel.org)
- 💬 **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- 🐙 **GitHub**: [github.com/the-alphabet-cartel](https://github.com/the-alphabet-cartel)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- The Alphabet Cartel community for inspiration and support
- All contributors to the Ash ecosystem

---

**Built with care for chosen family** 🏳️‍🌈
