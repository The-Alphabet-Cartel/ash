# Ash Bot v1.1 - Mental Health Support System

> *"Building chosen family, one conversation at a time."*

Ash is an AI-powered mental health support bot designed specifically for **The Alphabet Cartel** Discord community. Built with a three-tier crisis detection system and custom keyword management, Ash provides immediate support while alerting human crisis response teams when needed.

## 🎭 Character Overview

**Ash** is a Gothic counselor and "Family Sage" who survived depression, suicidal ideation, and found healing through art and chosen family. Their personality is:

- **Voice**: Sardonic but caring, philosophical, uses dark humor appropriately
- **Approach**: Validates pain without toxic positivity, offers gentle insights
- **Style**: Makes supportive statements rather than asking lots of follow-up questions
- **Language**: Uses "we" instead of "you" to build connection
- **AI Model**: Powered by Claude 4 Sonnet for advanced reasoning and empathy

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
- **Rate Limiting**: Prevents spam and abuse (10 responses per user per hour)
- **Custom Keywords**: Team-managed community-specific detection phrases
- **Hybrid Detection**: Combines keyword matching with ML analysis backup
- **Real-time Updates**: Custom keywords activate immediately without restart

## 🛠️ **NEW: Custom Keyword Management**

Crisis Response team members can manage detection keywords in real-time using slash commands:

### Available Slash Commands (Crisis Response Role Only):

- **`/add_keyword`** - Add custom crisis detection phrases
- **`/remove_keyword`** - Remove problematic keywords  
- **`/list_keywords`** - View current custom keywords
- **`/keyword_stats`** - See keyword statistics and counts

**Example Usage:**
```
/add_keyword crisis_level:High Crisis keyword:transition regret overwhelming
/list_keywords crisis_level:Medium Crisis
/keyword_stats
```

**Features:**
- ✅ Immediate activation (no restart needed)
- ✅ Role-based access control
- ✅ Complete audit trail with user/timestamp logging
- ✅ Persistent storage with backup
- ✅ False positive management

## 🏗️ Architecture

### File Structure
```
ash/
├── .env                        # Environment configuration
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Container orchestration
├── requirements.txt           # Python dependencies
└── bot/                       # Application code
    ├── main.py               # Main bot application
    ├── ash_character.py      # Character definition and prompts
    ├── claude_api.py         # Claude API integration
    ├── keyword_detector.py   # Detection logic
    ├── crisis_commands.py    # NEW: Slash command management
    ├── nlp_integration.py    # NEW: ML backup detection
    ├── startup.py            # Bot startup script
    ├── keywords/             # Modular keyword system
    │   ├── __init__.py
    │   ├── high_crisis.py    # 🔴 Critical keywords
    │   ├── medium_crisis.py  # 🟡 Concerning keywords
    │   └── low_crisis.py     # 🟢 Support keywords
    ├── logs/                 # Runtime logs
    └── data/                 # Data storage + custom keywords
        └── custom_keywords.json  # Team-managed keywords
```

### Technology Stack

- **Language**: Python 3.11
- **Discord**: discord.py 2.3.2
- **AI**: Claude 4 Sonnet (Anthropic API)
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions + GitHub Container Registry
- **Caching**: Redis (for session management)
- **ML Backup**: Remote NLP service integration
- **Commands**: Discord slash commands with role restrictions

## 🚀 Deployment

### Environment Variables

Create a `.env` file with:

```bash
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id

# Claude API (Updated to Claude 4)
CLAUDE_API_KEY=your_claude_api_key

# Channels
RESOURCES_CHANNEL_ID=your_resources_channel_id
CRISIS_RESPONSE_CHANNEL_ID=your_crisis_channel_id
ALLOWED_CHANNELS=channel1,channel2,channel3  # Optional

# Crisis Team
STAFF_PING_USER=staff_user_id
CRISIS_RESPONSE_ROLE_ID=crisis_team_role_id

# Display Names (for bot responses)
RESOURCES_CHANNEL_NAME=resources
CRISIS_RESPONSE_ROLE_NAME=CrisisResponse
STAFF_PING_NAME=StaffUserName

# Remote NLP Service (Optional)
NLP_SERVICE_HOST=your_ai_rig_ip
NLP_SERVICE_PORT=8001

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

# Monitor slash command sync
docker-compose logs ash | grep "Synced.*commands"
```

## 🔧 Configuration

### Adding Allowed Channels

1. Right-click channel → Copy Channel ID
2. Add to `ALLOWED_CHANNELS` in `.env`
3. Restart bot

### Managing Keywords

**Two methods available:**

#### 1. Slash Commands (Recommended for Crisis Team)
```
/add_keyword crisis_level:Low Crisis keyword:community specific phrase
/remove_keyword crisis_level:High Crisis keyword:old phrase
/list_keywords crisis_level:Medium Crisis
```

#### 2. Direct File Editing (For Developers)
Edit the modular keyword files:
- `keywords/high_crisis.py` - Critical situations
- `keywords/medium_crisis.py` - Concerning situations  
- `keywords/low_crisis.py` - Support situations

Changes auto-deploy via GitHub Actions.

### Setting Up Slash Commands

**Required Discord Developer Portal Configuration:**
- **Scopes**: `bot` + `applications.commands`
- **Permissions**: Send Messages, View Channels, Use Slash Commands, Embed Links, Add Reactions, Mention Everyone

**Bot Permissions Check:**
```bash
# Check logs for successful command sync
docker-compose logs ash | grep "Global sync successful"
```

## 📊 Monitoring

### Logs
- **Startup**: `bot/logs/ash_startup.log`
- **Runtime**: `bot/logs/ash.log`
- **Docker**: `docker-compose logs ash`
- **Command Usage**: All slash command usage logged with user ID

### Key Metrics
- Daily API call count
- Crisis detection statistics (built-in vs custom keywords)
- Response times
- Custom keyword effectiveness
- Slash command usage statistics
- Error rates

### Custom Keyword Analytics
```bash
# View keyword statistics
/keyword_stats

# Check keyword distribution
/list_keywords crisis_level:High Crisis
```

## 🛡️ Security

- **Non-root container**: Runs as UID 1001
- **Environment isolation**: Secrets in `.env` only
- **Rate limiting**: Per-user and daily limits
- **Channel restrictions**: Configurable allowed channels
- **Role-based access**: Slash commands restricted to CrisisResponse role
- **Command logging**: Full audit trail of keyword modifications
- **Clean shutdowns**: Proper resource cleanup
- **Input validation**: Keyword length limits and sanitization

## 💰 Cost Management

**Estimated Monthly Costs** (with Claude 4 Sonnet):
- **Low usage**: $20-35 (10-20 responses/day)
- **Medium usage**: $35-55 (30-50 responses/day)  
- **High usage**: $55-95 (75+ responses/day)

**Cost controls**:
- Daily API call limits (`MAX_DAILY_CALLS=1000`)
- Per-user rate limiting (`RATE_LIMIT_PER_USER=10`)
- 5-minute conversation windows (no reset)
- Efficient token usage with optimized prompts

**Cost monitoring**:
- Daily API usage tracking
- Response length optimization
- Token usage statistics in logs

## 🔄 Maintenance

### Updating Custom Keywords (Real-time)
**Crisis Response Team:**
1. Use `/add_keyword` or `/remove_keyword` slash commands
2. Changes are immediately active
3. View `/keyword_stats` for monitoring

### Updating Built-in Keywords
**Developers:**
1. Edit keyword files in `keywords/` directory
2. Commit and push to GitHub
3. GitHub Actions builds new image automatically
4. Run `docker-compose pull && docker-compose up -d`

### Bot Updates
1. Modify code files
2. Test locally with `python startup.py`
3. Verify slash commands sync: `📋 Found X commands in tree`
4. Commit and push to GitHub
5. Deploy updated container

### Health Checks
- Container health check via Claude API test
- Startup connection validation
- Slash command sync verification
- NLP service connectivity (if enabled)
- Automatic restart on failure

## 🆘 Crisis Response Integration

### For Crisis Response Team

**When you receive alerts:**

**Medium Crisis (🟡)**:
- Monitor the situation
- Provide additional support if needed
- Watch for escalation
- Consider adding custom keywords if new language patterns emerge

**High Crisis (🔴)**:
- **Immediate response required**
- Check crisis response channel for coordination
- One team member should reach out directly
- Escalate to professional resources if needed

**Keyword Management:**
- **Add keywords** for community-specific crisis language
- **Remove keywords** causing false positives
- **Monitor effectiveness** with `/keyword_stats`
- **Document changes** in team meetings

### Staff Notifications

High crisis situations trigger:
1. **Private DM** to configured staff member with full details
2. **Public alert** in crisis response channel for team coordination
3. **Audit log** entry with timestamp and context

## 🤝 Contributing

### Adding Features
1. Create feature branch
2. Test thoroughly with local environment
3. Test slash command functionality if applicable
4. Update documentation (README + team guide)
5. Submit pull request

### Reporting Issues
1. Check logs for error details
2. Include reproduction steps
3. Note crisis level and keywords involved
4. For slash commands: include command used and error response
5. Provide relevant log excerpts

### Testing Slash Commands
```bash
# Check command registration
docker-compose logs ash | grep "commands in tree"

# Test role permissions
# (Try commands with/without CrisisResponse role)

# Verify immediate activation
# (Add keyword, test detection immediately)
```

## 📝 License

Built for **The Alphabet Cartel** Discord community. Internal use only.

## 🙏 Acknowledgments

- **Anthropic** for Claude 4 Sonnet API
- **Discord.py** community for excellent library
- **The Alphabet Cartel** members for testing and feedback
- **Crisis Response Team** for keyword management and community insights

---

## Version History

### v1.1 (Current) - July 21, 2025
- ✅ **Custom keyword management** via slash commands
- ✅ **Claude 4 Sonnet** integration for improved responses
- ✅ **Role-based access control** for Crisis Response team
- ✅ **Real-time keyword updates** without restart
- ✅ **Comprehensive audit trail** with user/timestamp logging
- ✅ **Hybrid detection system** (keywords + ML backup)
- ✅ **Enhanced error handling** and logging
- ✅ **Global slash command sync** for reliability

### v1.0 - Initial Release
- ✅ Three-tier crisis detection system
- ✅ Modular keyword architecture  
- ✅ Conversation tracking with escalation
- ✅ Channel restrictions
- ✅ GitHub Actions CI/CD
- ✅ Production Docker deployment
- ✅ Comprehensive crisis team integration

---

## 🚀 What's Next

**Planned Features:**
- Advanced ML models for context understanding
- Analytics dashboard for team performance
- Integration with external crisis resources
- Multi-language support
- Enhanced conversation memory
- Automated keyword suggestions

---

*Remember: Ash provides initial support and alerts, but human connection and care remain the heart of crisis response. Now with the power to adapt detection to your community's unique language in real-time.*