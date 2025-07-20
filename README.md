# Ash Bot v1.0 - Mental Health Support System

> *"Building chosen family, one conversation at a time."*

Ash is an AI-powered mental health support bot designed specifically for **The Alphabet Cartel** Discord community. Built with a three-tier crisis detection system, Ash provides immediate support while alerting human crisis response teams when needed.

## 🎭 Character Overview

**Ash** is a Gothic counselor and "Family Sage" who survived depression, suicidal ideation, and found healing through art and chosen family. Their personality is:

- **Voice**: Sardonic but caring, philosophical, uses dark humor appropriately
- **Approach**: Validates pain without toxic positivity, offers gentle insights
- **Style**: Makes supportive statements rather than asking lots of follow-up questions
- **Language**: Uses "we" instead of "you" to build connection

## 🚨 Crisis Response System

### Three-Tier Detection

#### 🟢 **LOW CRISIS** (Depression, Anxiety, Identity Issues)
- **Response**: Ash provides supportive reply only
- **Team Alert**: None
- **Examples**: "I feel empty," "hate myself," "so anxious"

#### 🟡 **MEDIUM CRISIS** (Severe Distress, Panic Attacks)
- **Response**: Ash provides supportive reply
- **Team Alert**: Orange alert in crisis response channel (no staff DM)
- **Examples**: "can't take it anymore," "panic attack," "everything hurts"

#### 🔴 **HIGH CRISIS** (Suicidal Ideation, Self-Harm, Immediate Danger)
- **Response**: Ash provides supportive reply + crisis resources
- **Team Alert**: Red alert in crisis response channel + role ping + staff DM
- **Examples**: "want to die," "kill myself," "have a plan," "cut myself"

### Smart Features

- **Conversation Tracking**: 5-minute follow-up windows for continued support
- **Crisis Escalation**: Detects if crisis level increases during conversations
- **Channel Restrictions**: Only responds in configured allowed channels
- **Rate Limiting**: Prevents spam and abuse

## 🏗️ Architecture

### File Structure
```
ash/
├── .env                        # Environment configuration
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Container orchestration
├── requirements.txt           # Python dependencies
├── .github/workflows/         # GitHub Actions CI/CD
│   └── ash-build.yml
└── bot/                       # Application code
    ├── main.py               # Main bot application
    ├── ash_character.py      # Character definition and prompts
    ├── claude_api.py         # Claude API integration
    ├── keyword_detector.py   # Detection logic
    ├── startup.py            # Bot startup script
    ├── keywords/             # Modular keyword system
    │   ├── __init__.py
    │   ├── high_crisis.py    # 🔴 Critical keywords
    │   ├── medium_crisis.py  # 🟡 Concerning keywords
    │   └── low_crisis.py     # 🟢 Support keywords
    ├── logs/                 # Runtime logs
    └── data/                 # Data storage
```

### Technology Stack

- **Language**: Python 3.11
- **Discord**: discord.py
- **AI**: Claude 3.5 Sonnet (Anthropic API)
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions + GitHub Container Registry
- **Database**: Redis (for future features)

## 🚀 Deployment

### Environment Variables

Create a `.env` file with:

```bash
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id

# Claude API
CLAUDE_API_KEY=your_claude_api_key

# Channels
RESOURCES_CHANNEL_ID=your_resources_channel_id
CRISIS_RESPONSE_CHANNEL_ID=your_crisis_channel_id
ALLOWED_CHANNELS=channel1,channel2,channel3  # Optional

# Crisis Team
STAFF_PING_USER=staff_user_id
CRISIS_RESPONSE_ROLE_ID=crisis_team_role_id

# Optional Settings
LOG_LEVEL=INFO
MAX_DAILY_CALLS=1000
RATE_LIMIT_PER_USER=10
```

### Local Development

```bash
# Create virtual environment
python3 -m venv ash-env
source ash-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
cd bot
python startup.py
```

### Production Deployment

```bash
# Pull latest image
docker-compose pull

# Start services
docker-compose up -d

# View logs
docker-compose logs -f ash
```

## 🔧 Configuration

### Adding Allowed Channels

1. Right-click channel → Copy Channel ID
2. Add to `ALLOWED_CHANNELS` in `.env`
3. Restart bot

### Updating Keywords

Edit the modular keyword files:
- `keywords/high_crisis.py` - Critical situations
- `keywords/medium_crisis.py` - Concerning situations  
- `keywords/low_crisis.py` - Support situations

Changes auto-deploy via GitHub Actions.

## 📊 Monitoring

### Logs
- **Startup**: `bot/logs/ash_startup.log`
- **Runtime**: `bot/logs/ash.log`
- **Docker**: `docker-compose logs ash`

### Key Metrics
- Daily API call count
- Crisis detection statistics
- Response times
- Error rates

## 🛡️ Security

- **Non-root container**: Runs as UID 1001
- **Environment isolation**: Secrets in `.env` only
- **Rate limiting**: Per-user and daily limits
- **Channel restrictions**: Configurable allowed channels
- **Clean shutdowns**: Proper resource cleanup

## 💰 Cost Management

**Estimated Monthly Costs**:
- **Low usage**: $15-25 (10-20 responses/day)
- **Medium usage**: $25-45 (30-50 responses/day)  
- **High usage**: $45-80 (75+ responses/day)

**Cost controls**:
- Daily API call limits
- Per-user rate limiting
- 5-minute conversation windows (no reset)

## 🔄 Maintenance

### Updating Keywords
1. Edit keyword files in `keywords/` directory
2. Commit and push to GitHub
3. GitHub Actions builds new image automatically
4. Run `docker-compose pull && docker-compose up -d`

### Bot Updates
1. Modify code files
2. Test locally with `python startup.py`
3. Commit and push to GitHub
4. Deploy updated container

### Health Checks
- Container health check via Claude API test
- Startup connection validation
- Automatic restart on failure

## 🆘 Crisis Response Integration

### For Crisis Response Team

**When you receive alerts:**

**Medium Crisis (🟡)**:
- Monitor the situation
- Provide additional support if needed
- Watch for escalation

**High Crisis (🔴)**:
- **Immediate response required**
- Check crisis response channel for coordination
- One team member should reach out directly
- Escalate to professional resources if needed

### Staff Notifications

High crisis situations trigger:
1. **Private DM** to configured staff member with full details
2. **Public alert** in crisis response channel for team coordination

## 🤝 Contributing

### Adding Features
1. Create feature branch
2. Test thoroughly with local environment
3. Update documentation
4. Submit pull request

### Reporting Issues
1. Check logs for error details
2. Include reproduction steps
3. Note crisis level and keywords involved
4. Provide relevant log excerpts

## 📝 License

Built for **The Alphabet Cartel** Discord community. Internal use only.

## 🙏 Acknowledgments

- **Anthropic** for Claude API
- **Discord.py** community
- **The Alphabet Cartel** members for testing and feedback

---

## Version History

### v1.0 (Current)
- ✅ Three-tier crisis detection system
- ✅ Modular keyword architecture  
- ✅ Conversation tracking with escalation
- ✅ Channel restrictions
- ✅ GitHub Actions CI/CD
- ✅ Production Docker deployment
- ✅ Comprehensive crisis team integration

---

*Remember: Ash provides initial support and alerts, but human connection and care remain the heart of crisis response.*