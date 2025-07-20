# Ash Bot - Crisis Response Team Guide v1.0

## What is Ash?

Ash is our AI-powered mental health support bot for The Alphabet Cartel. Designed as a "Gothic counselor" and "Family Sage," Ash automatically detects when community members are struggling and provides immediate support while alerting our crisis response team when needed.

## How Ash Works

### 🔍 **Automatic Detection**
Ash monitors messages in configured channels for keywords indicating mental health struggles:
- **Depression symptoms**: "feel worthless," "hate myself," "so tired," "nobody cares"
- **Anxiety signs**: "panic attack," "can't breathe," "losing control"
- **Identity struggles**: "don't know who I am," "feel fake," "don't belong"
- **Crisis indicators**: "want to die," "kill myself," "end it all," "cut myself"

### 🎭 **Ash's Personality**
- **Voice**: Sardonic but caring, philosophical, uses dark humor appropriately
- **Approach**: Validates pain without toxic positivity, offers gentle insights
- **Style**: Makes supportive statements rather than asking lots of follow-up questions
- **Language**: Uses "we" instead of "you" to build connection

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

### 🛠 **Technical Features**
- **Always Available**: Runs 24/7 in Docker containers
- **Channel Restricted**: Only responds in configured allowed channels
- **Rate Limited**: Prevents spam/abuse
- **Auto-Updates**: Code changes automatically deploy via GitHub
- **Logging**: All interactions logged for monitoring and improvement

## What This Means for Crisis Response Team

### ✅ **What Ash Handles Automatically**
- Immediate support responses to people in crisis
- Keyword detection and crisis level assessment
- Initial validation and comfort for community members
- Automatic team notifications for medium/high crisis

### 👥 **What the Team Still Does**
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

### 📈 **Benefits for Our Community**
- **24/7 Coverage**: Immediate response even when team isn't online
- **Consistent Support**: Every crisis gets acknowledged and supported
- **Team Efficiency**: Alerts help us respond faster and more effectively
- **Community Care**: Shows our commitment to mental health support
- **Channel Focused**: Only active in appropriate channels for mental health discussions

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

### ✅ **Best Practices**
- **Acknowledge alerts quickly** - even if just "I see this, monitoring"
- **Coordinate in crisis channel** - "I'm reaching out to them now"
- **Follow up privately** - check on team members handling difficult cases
- **Use Ash as backup** - if you're not available, Ash provides continuity
- **Trust the system** - Ash's detection is quite accurate

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
- Keyword detection
- Technical issues
- Suggestions for improvements

Contact [your contact information] or discuss in the crisis team channel.

### 📝 **Feedback and Improvements**

Ash is continuously evolving. If you notice:
- **False positives**: Keywords that shouldn't trigger alerts
- **Missed crises**: Situations Ash should have caught
- **Inappropriate responses**: Times when Ash's tone was off
- **New keywords needed**: Phrases your community uses that aren't detected

Please report these for system improvements.

### 🔍 **Monitoring and Statistics**

Regular monitoring includes:
- Daily crisis detection counts
- Response accuracy rates
- API usage and costs
- Team response times
- Community feedback

### 🎯 **Success Metrics**

We measure success by:
- **Faster crisis response times** compared to human-only detection
- **Increased crisis intervention rates** (catching more situations)
- **Community feedback** on feeling supported
- **Team efficiency** in coordinating responses
- **Reduced burnout** from 24/7 monitoring burden

### 🚀 **Future Enhancements**

Planned improvements include:
- Enhanced keyword detection based on community usage
- Integration with additional mental health resources
- Improved conversation context understanding
- Analytics dashboard for team performance
- Additional customization options

### 🧠 **Understanding Ash's Limitations**

Ash is designed to **enhance** human crisis response, not replace it:

**What Ash does well:**
- Immediate keyword detection
- Consistent initial support
- Reliable team alerting
- 24/7 availability
- Emotion validation

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

**Always remember:**
- You're not alone - the team supports each other
- It's okay to ask for help with difficult cases
- Self-care is crucial for crisis responders
- Every intervention matters, even small ones

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

---

**Remember: We're building chosen family, one conversation at a time. Ash helps us do that more effectively, but the heart of our response is human connection and care.**

---

*Last updated: [Current Date]*
*Version: 1.0*
*Next review: [Set review schedule]*