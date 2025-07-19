# Ash
 Mental Health Discord Bot

## Ash - Crisis Response System Guide
### Who is Ash?
Ash is our new AI-powered mental health support bot for The Alphabet Cartel. Designed as a "Gothic counselor" and "Family Sage," Ash automatically detects when community members are struggling and provides immediate support while alerting our crisis response team when needed.

## How Ash Works
### 🔍 Automatic Detection
Ash monitors all messages in our server for keywords indicating mental health struggles:
* Depression symptoms: "feel worthless," "hate myself," "so tired," "nobody cares"
* Anxiety signs: "panic attack," "can't breathe," "losing control"
* Identity struggles: "don't know who I am," "feel fake," "don't belong"
* Crisis indicators: "want to die," "kill myself," "end it all," "cut myself"

### 🎭 Ash's Personality
* Voice: Sardonic but caring, philosophical, uses dark humor appropriately
* Approach: Validates pain without toxic positivity, offers gentle insights
* Style: Makes supportive statements rather than asking lots of follow-up questions
* Language: Uses "we" instead of "you" to build connection

### 📊 Three-Tier Crisis Response
🟢 LOW CRISIS (Depression, Anxiety, Identity Issues)
Ash Response: Supportive reply only
Team Alert: None
Examples: "I feel empty," "hate myself," "so anxious"

#### 🟡 MEDIUM CRISIS (Severe Distress, Panic Attacks)
Ash Response: Supportive reply
Team Alert: Orange alert in crisis response channel
No Staff DM: Team awareness only
Examples: "can't take it anymore," "panic attack," "everything hurts"

#### 🔴 HIGH CRISIS (Suicidal Ideation, Self-Harm, Immediate Danger)
Ash Response: Supportive reply + crisis resources
Team Alert: Red alert in crisis response channel + role ping
Staff DM: PapaBearDoes receives detailed private message
Examples: "want to die," "kill myself," "have a plan," "cut myself"

### 💬 Conversation Tracking
After Ash responds to someone, they're tracked for 5 minutes to allow follow-up conversation:
* User can continue talking to Ash for 5 minutes after initial response
* Each response resets the 5-minute timer
* Conversations are contained to the original channel
* Crisis escalation: If someone escalates during conversation (low → medium → high), Ash responds accordingly and triggers appropriate alerts

### 🚨 Alert System Details
#### Medium Crisis Alerts
Where:
* Crisis response channel only
Who:
* Crisis response team role pinged
Info:
* User, location, message link, "monitor situation" guidance

#### High Crisis Alerts
Where:
* Crisis response channel (team coordination)
* Private DM to PapaBearDoes (leadership notification)
Who:
* Crisis response team + staff lead
Info:
* Full details including original message content, user info, jump links

### 🛠 Technical Features
* Always Available: Runs 24/7 in Docker containers
* Rate Limited: Prevents spam/abuse
* Auto-Updates: Code changes automatically deploy via GitHub
* Logging: All interactions logged for monitoring and improvement

### What This Means for Crisis Response Team
✅ What Ash Handles Automatically
* Immediate support responses to people in crisis
* Keyword detection and crisis level assessment
* Initial validation and comfort for community members
* Automatic team notifications for medium/high crisis

### 👥 What the Team Still Does
* Medium Crisis: Monitor situation, provide additional support if needed
* High Crisis: Immediate response required - check on the person, coordinate care
* Follow-up: Ash provides initial support, team provides ongoing human care
* Complex situations: Ash handles detection, team handles complex interventions

### 🎯 Response Guidelines
When you get a Medium Crisis alert:
* Review the situation in the linked message
* Monitor for escalation
* Jump in if the person needs more support than Ash can provide

When you get a High Crisis alert:
* Immediate response required
* Check the crisis response channel for team coordination
* One team member should reach out directly to the person
* Coordinate with other responders to avoid overwhelming the person
* Escalate to professional resources if needed (#queer-resources channel)

### 📈 Benefits for Our Community
24/7 Coverage: Immediate response even when team isn't online
Consistent Support: Every crisis gets acknowledged and supported
Team Efficiency: Alerts help us respond faster and more effectively
Community Care: Shows our commitment to mental health support

Ash is designed to enhance our human crisis response, not replace it.

Remember: Ash provides initial support and alerts, but human connection and care remain the heart of our crisis response.