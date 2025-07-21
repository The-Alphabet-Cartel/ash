# Ash Bot - Crisis Response Team Guide v1.1

## What is Ash?

Ash is our AI-powered mental health support bot for The Alphabet Cartel. Designed as a "Gothic counselor" and "Family Sage," Ash automatically detects when community members are struggling and provides immediate support while alerting our crisis response team when needed.

## How Ash Works

### 🔍 **Automatic Detection**
Ash monitors messages in configured channels for keywords indicating mental health struggles:
- **Depression symptoms**: "feel worthless," "hate myself," "so tired," "nobody cares"
- **Anxiety signs**: "panic attack," "can't breathe," "losing control"
- **Identity struggles**: "don't know who I am," "feel fake," "don't belong"
- **Crisis indicators**: "want to die," "kill myself," "end it all," "cut myself"
- **Custom keywords**: Team-managed phrases specific to our community

### 🎭 **Ash's Personality**
- **Voice**: Sardonic but caring, philosophical, uses dark humor appropriately
- **Approach**: Validates pain without toxic positivity, offers gentle insights
- **Style**: Makes supportive statements rather than asking lots of follow-up questions
- **Language**: Uses "we" instead of "you" to build connection
- **Model**: Powered by Claude 4 Sonnet for advanced reasoning and empathy

### 📊 **Three-Tier Crisis Response**

#### 🟢 **LOW CRISIS** (Depression, Anxiety, Identity Issues)
- **Ash Response**: Supportive reply only
- **Team Alert**: None
- **Examples**: "I feel empty," "hate myself," "so anxious"

#### 🟡 **MEDIUM CRISIS** (Severe Distress, Panic Attacks)
- **Ash Response**: Supportive reply
- **Team Alert**: Orange alert in crisis response channel
- **No Staff DM**: Team awareness only
- **Examples**: "can't take it anymore," "panic attack," "everything hurts"

#### 🔴 **HIGH CRISIS** (Suicidal Ideation, Self-Harm, Immediate Danger)
- **Ash Response**: Supportive reply + crisis resources
- **Team Alert**: Red alert in crisis response channel + role ping
- **Staff DM**: PapaBearDoes receives detailed private message
- **Examples**: "want to die," "kill myself," "have a plan," "cut myself"

### 🛠 **NEW: Custom Keyword Management**

Crisis Response team members can now manage custom keywords using slash commands:

#### Available Slash Commands (Crisis Response Role Only):

**`/add_keyword`**
- **Purpose**: Add custom keywords/phrases to any crisis level
- **Usage**: `/add_keyword crisis_level:High Crisis keyword:feeling hopeless about transition`
- **Effect**: Keyword immediately becomes active (no restart needed)

**`/remove_keyword`**
- **Purpose**: Remove custom keywords from detection
- **Usage**: `/remove_keyword crisis_level:Medium Crisis keyword:old phrase`
- **Effect**: Keyword immediately deactivated

**`/list_keywords`**
- **Purpose**: View all custom keywords for a specific crisis level
- **Usage**: `/list_keywords crisis_level:Low Crisis`
- **Shows**: All custom keywords, count, and last modification info

**`/keyword_stats`**
- **Purpose**: Overview statistics for all custom keywords
- **Usage**: `/keyword_stats`
- **Shows**: Counts by crisis level, total keywords, built-in vs custom breakdown

#### Custom Keyword Guidelines:

**✅ Good Keywords:**
- Community-specific language: "dysphoria hitting hard," "family rejected me"
- Phrases your community uses: "closet suffocating me," "transition doubts"
- LGBTQIA+ specific struggles: "internalized homophobia," "passing anxiety"

**❌ Avoid:**
- Single common words that might false-positive: "bad," "sad," "tired"
- Phrases that might be used in other contexts: "I'm dying" (could be hyperbolic)
- Very long phrases (100+ characters)

**🎯 Best Practices:**
- **Start conservatively**: Add keywords gradually and monitor effectiveness
- **Test thoroughly**: Check for false positives after adding
- **Document reasoning**: Use descriptive keywords that make sense to the team
- **Regular review**: Periodically review and clean up keyword lists

### 💬 **Conversation Tracking**

After Ash responds to someone, they're tracked for **5 minutes** to allow follow-up conversation:
- User can continue talking to Ash for 5 minutes after initial response
- Timer does NOT reset with each response (prevents abuse)
- Conversations are contained to the original channel
- **Crisis escalation**: If someone escalates during conversation (low → medium → high), Ash responds accordingly and triggers appropriate alerts

### 🚨 **Alert System Details**

#### Medium Crisis Alerts
- **Where**: Crisis response channel only
- **Who**: Crisis response team role pinged
- **Info**: User, location, message link, "monitor situation" guidance
- **Color**: Orange embed

#### High Crisis Alerts
- **Where**: 
  - Crisis response channel (team coordination)
  - Private DM to PapaBearDoes (leadership notification)
- **Who**: Crisis response team + staff lead
- **Info**: Full details including original message content, user info, jump links
- **Color**: Red embed

### 🔧 **Technical Features**
- **Always Available**: Runs 24/7 in Docker containers
- **Channel Restricted**: Only responds in configured allowed channels
- **Rate Limited**: Prevents spam/abuse (10 responses per user per hour)
- **Auto-Updates**: Code changes automatically deploy via GitHub
- **Logging**: All interactions logged for monitoring and improvement
- **Backup Detection**: Hybrid system with both keyword matching and ML analysis
- **Data Persistence**: Custom keywords saved permanently with audit trail

## What This Means for Crisis Response Team

### ✅ **What Ash Handles Automatically**
- Immediate support responses to people in crisis
- Keyword detection and crisis level assessment (built-in + custom)
- Initial validation and comfort for community members
- Automatic team notifications for medium/high crisis
- Real-time keyword updates when team adds/removes custom phrases

### 👥 **What the Team Still Does**
- **Keyword Management**: Add community-specific crisis language using slash commands
- **Medium Crisis**: Monitor situation, provide additional support if needed
- **High Crisis**: Immediate response required - check on the person, coordinate care
- **Follow-up**: Ash provides initial support, team provides ongoing human care
- **Complex situations**: Ash handles detection, team handles complex interventions

### 🎯 **Response Guidelines**

#### When you get a Medium Crisis alert (🟡):
1. **Review** the situation in the linked message
2. **Monitor** for escalation
3. **Provide additional support** if the person needs more than Ash can offer
4. **Coordinate** with other team members to avoid overwhelming the person

#### When you get a High Crisis alert (🔴):
1. **Immediate response required**
2. **Check crisis response channel** for team coordination
3. **One team member should reach out** directly to the person
4. **Coordinate with other responders** to avoid overwhelming
5. **Escalate to professional resources** if needed (#resources channel)
6. **Staff lead (PapaBearDoes) will have received detailed DM** with full context

### 🔧 **Managing Custom Keywords**

#### Adding Keywords:
1. **Notice patterns**: Community members using phrases Ash doesn't catch
2. **Use slash command**: `/add_keyword crisis_level:Medium Crisis keyword:new phrase`
3. **Test effectiveness**: Monitor if the keyword triggers appropriately
4. **Document decision**: Note why the keyword was added

#### Removing Keywords:
1. **Identify problems**: Keywords causing false positives
2. **Use slash command**: `/remove_keyword crisis_level:Low Crisis keyword:problematic phrase`
3. **Monitor impact**: Ensure no legitimate crises are missed

#### Regular Maintenance:
- **Monthly review**: `/keyword_stats` to see overall counts
- **Check each level**: `/list_keywords` for each crisis level
- **Team discussion**: Coordinate keyword management during team meetings
- **Track changes**: All additions/removals are logged with user and timestamp

### 📈 **Benefits for Our Community**
- **24/7 Coverage**: Immediate response even when team isn't online
- **Consistent Support**: Every crisis gets acknowledged and supported
- **Team Efficiency**: Alerts help us respond faster and more effectively
- **Community Care**: Shows our commitment to mental health support
- **Channel Focused**: Only active in appropriate channels for mental health discussions
- **Customizable**: Team can adapt detection to community-specific language
- **Audit Trail**: Full tracking of who modified what keywords when

### 🔧 **Channel Configuration**

Ash currently responds in these configured channels:
- [List will depend on your ALLOWED_CHANNELS configuration]

If you need Ash added to additional channels, contact server administration.

### 📊 **Understanding the Alerts**

#### Medium Crisis Alert Format:
```
⚠️ Medium Crisis Alert
Significant distress detected - team awareness needed

Location: #channel-name in The Alphabet Cartel
User: @username
Crisis Level: Medium - Monitor situation
Jump to Message: [Click here]
```

#### High Crisis Alert Format:
```
🚨 Crisis Response Team Alert
High-crisis situation detected requiring team response

Location: #channel-name in The Alphabet Cartel  
User: @username
Action Needed: Please respond to provide crisis support
Jump to Message: [Click here]
```

### 🚫 **What NOT to Do**
- **Don't ignore medium crisis alerts** - even if no immediate action needed, awareness is important
- **Don't assume someone else will handle it** - coordinate in crisis channel
- **Don't overwhelm the person** - one primary responder, others support
- **Don't panic** - Ash has already provided initial support
- **Don't add keywords hastily** - consider false positive potential
- **Don't remove keywords without team discussion** - might miss legitimate crises

### ✅ **Best Practices**
- **Acknowledge alerts quickly** - even if just "I see this, monitoring"
- **Coordinate in crisis channel** - "I'm reaching out to them now"
- **Follow up privately** - check on team members handling difficult cases
- **Use Ash as backup** - if you're not available, Ash provides continuity
- **Trust the system** - Ash's detection is quite accurate
- **Manage keywords thoughtfully** - add gradually, test thoroughly
- **Document keyword decisions** - help team understand additions/removals

### 🆘 **Escalation Paths**

1. **Ash detects crisis** → Immediate support + alerts
2. **Team member responds** → Provides human connection
3. **If situation is beyond team capacity** → Professional resources in #resources
4. **If immediate danger** → Encourage calling emergency services

### 📞 **Emergency Contacts**

Always available in #resources channel:
- Crisis Text Line
- National Suicide Prevention Lifeline  
- Local emergency services
- LGBTQIA+ specific crisis resources

### 🤔 **Questions or Concerns?**

If you have questions about:
- How Ash works
- Alert procedures
- Keyword detection and management
- Slash command usage
- Technical issues
- Suggestions for improvements

Contact [your contact information] or discuss in the crisis team channel.

### 📝 **Feedback and Improvements**

Ash is continuously evolving. If you notice:
- **False positives**: Keywords that shouldn't trigger alerts (use `/remove_keyword`)
- **Missed crises**: Situations Ash should have caught (use `/add_keyword`)
- **Inappropriate responses**: Times when Ash's tone was off
- **New community language**: Phrases your community uses that aren't detected

You can now directly manage most keyword issues using the slash commands!

### 🔍 **Monitoring and Statistics**

Regular monitoring includes:
- Daily crisis detection counts
- Response accuracy rates
- API usage and costs
- Team response times
- Community feedback
- Custom keyword effectiveness

Use `/keyword_stats` to see current keyword distribution and help identify areas needing attention.

### 🎯 **Success Metrics**

We measure success by:
- **Faster crisis response times** compared to human-only detection
- **Increased crisis intervention rates** (catching more situations)
- **Community feedback** on feeling supported
- **Team efficiency** in coordinating responses
- **Reduced burnout** from 24/7 monitoring burden
- **Improved detection accuracy** through custom keyword refinement

### 🚀 **Recent Updates (v1.1)**

**New Features:**
- **Custom keyword management** via slash commands
- **Claude 4 Sonnet** integration for better responses
- **Enhanced logging** with audit trails
- **Real-time keyword updates** (no restart needed)
- **Hybrid detection system** (keywords + ML analysis)

**Improved:**
- Crisis level accuracy
- Response quality and empathy
- Team coordination workflows
- Technical reliability

### 🧠 **Understanding Ash's Limitations**

Ash is designed to **enhance** human crisis response, not replace it:

**What Ash does well:**
- Immediate keyword detection (built-in + custom)
- Consistent initial support
- Reliable team alerting
- 24/7 availability
- Emotion validation
- Adapting to community-specific language

**What Ash cannot do:**
- Understand complex context like humans
- Provide ongoing therapy or counseling
- Handle nuanced relationship issues
- Make clinical assessments
- Replace professional mental health care

**Remember**: Ash provides the bridge to human care, not the destination.

### 📋 **Quick Reference Card**

**For Medium Crisis (🟡):**
- Monitor situation
- Provide additional support if needed
- Watch for escalation
- Coordinate with team

**For High Crisis (🔴):**
- Immediate response required
- Check crisis channel for coordination
- Direct outreach to person in crisis
- Escalate to professional help if needed
- Staff lead has detailed information

**For Keyword Management:**
- `/add_keyword` - Add community-specific crisis language
- `/remove_keyword` - Remove problematic keywords
- `/list_keywords` - Review current custom keywords
- `/keyword_stats` - See overall keyword statistics

**Always remember:**
- You're not alone - the team supports each other
- It's okay to ask for help with difficult cases
- Self-care is crucial for crisis responders
- Every intervention matters, even small ones
- Custom keywords help Ash better serve our community

---

## Emergency Protocols

### If Ash is Down
1. Monitor channels manually for crisis language
2. Report technical issues immediately
3. Maintain normal crisis response procedures
4. Use backup communication methods

### If Crisis Channel is Unavailable
1. Use direct messages for coordination
2. Alert staff lead directly
3. Document responses for later review
4. Continue crisis response protocols

### If Team Member is Overwhelmed
1. Request backup in crisis channel
2. Tag additional team members
3. Consider professional resource referral
4. Follow up with self-care

### If Slash Commands Aren't Working
1. Check that you have the CrisisResponse role
2. Try the command again (global commands can be slow)
3. Report technical issues to administration
4. Use manual keyword management temporarily

---

## Slash Commands Reference

### `/add_keyword`
**Purpose**: Add custom crisis detection keyword
**Required Parameters**: 
- `crisis_level`: Low Crisis, Medium Crisis, or High Crisis
- `keyword`: The phrase to detect (can contain spaces)
**Example**: `/add_keyword crisis_level:High Crisis keyword:transition regret overwhelming`

### `/remove_keyword`
**Purpose**: Remove custom crisis detection keyword
**Required Parameters**:
- `crisis_level`: Low Crisis, Medium Crisis, or High Crisis  
- `keyword`: The exact phrase to remove
**Example**: `/remove_keyword crisis_level:Medium Crisis keyword:old phrase`

### `/list_keywords`
**Purpose**: View all custom keywords for a crisis level
**Required Parameters**:
- `crisis_level`: Low Crisis, Medium Crisis, or High Crisis
**Example**: `/list_keywords crisis_level:Low Crisis`

### `/keyword_stats`
**Purpose**: See statistics for all custom keywords
**No Parameters Required**
**Example**: `/keyword_stats`

**Notes**: 
- All commands are restricted to Crisis Response role members
- Changes take effect immediately
- All modifications are logged with user and timestamp
- Commands are private (only you see the response)

---

**Remember: We're building chosen family, one conversation at a time. Ash helps us do that more effectively, but the heart of our response is human connection and care. Now with the power to customize Ash's detection to our community's unique language.**

---

*Last updated: July 21, 2025*
*Version: 1.1*
*Next review: Monthly team meeting*