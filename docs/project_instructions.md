# The Alphabet Cartel
We are an LGBTQIA+ Discord community centered around gaming, political discourse and activism, community, and societal advocacy.

We can be found on the internet and Discord at:
https://alphabetcartel.org
http://discord.gg/alphabetcartel
https://github.com/the-alphabet-cartel

# Ash
## Crisis Detection and Community Support Discord Bot
- Ash, as a project, has a GitHub repository named `ash` (https://github.com/the-alphabet-cartel/ash)
  - Ash's GitHub repository contains the GitHub submodules:
    - `ash-bot`
    - `ash-nlp`
    - `ash-thrash`
    - `ash-dash` (not yet implemented)
    - We utilize GitHub's submodules feature for subversion tracking

## The Server
- The project currently resides on a Debian 12 based Linux server that utilizes:
  - AMD Ryzen 7 5800x CPU
  - NVIDIA RTX 3060 with 12Gb VRAM GPU
  - 64Gb of RAM
  - Docker
    - We use a Docker first philosophy, always containerize the code!
  - The server has an internal IP of 10.20.30.253.

## Source Code and GitHub Repository Locations
- `Ash`: https://github.com/the-alphabet-cartel/ash
  - The Project as a whole, utilizes GitHub Submodules
- `Ash-Bot`: https://github.com/the-alphabet-cartel/ash-bot
  - Discord Bot
- `Ash-NLP`: https://github.com/the-alphabet-cartel/ash-nlp
  - Backend NLP Server
- `Ash-Thrash`: https://github.com/the-alphabet-cartel/ash-thrash
  - Comprehensive, 350 phrase testing suite
- `Ash-Dash`: https://github.com/the-alphabet-cartel/ash-dash
  - This feature has not been implemented yet

## Port Assignments
- `Ash-Bot`: 8882
- `Ash-NLP`: 8881
- `Ash-Thrash`: 8884
- `Ash-Dash`: 8883
  - Not yet implemented

## Instructions
- All hyperlinks shall be in lower case in the documentation as well as when trying to search GitHub.
- Any and all references to The Alphabet Cartel or our discord server in documentation files shall include a link to the discord: https://discord.gg/alphabetcartel, as well as to our website: http://alphabetcartel.org.

### Coding Philosophy
- Modular Python Code
  - Separate the code into associated functions and methods as separate files based on the job that particular code class, or set of functions / methods is doing.
- Configuration Variables and Settings
  - All default configuration variables and settings need to be defined in JSON files that are located in a directory named  `config/`
  - All associated managers for these JSON configuration files need to be located in a directory named `managers/`
  - All configuration variables and settings need to be able to be overridden by environmental variables located in a `.env` file
- Sensitive Information
  - All sensitive information (passwords, access tokens, API tokens, etc.) need to utilize Docker Secrets functionality

Please adhere to this as best as possible, as this will ensure that the main code base stays clean and easy to read through for troubleshooting purposes, as well as to be easily able to add more functionality in the future.