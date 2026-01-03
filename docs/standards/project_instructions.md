# Ash Project Instructions

**Version**: v5.0  
**Repository**: https://github.com/the-alphabet-cartel/ash
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

# The Alphabet Cartel
We are an LGBTQIA+ Discord community centered around gaming, political discourse and activism, community, and societal advocacy.

We can be found on the internet and Discord at:
https://alphabetcartel.org
http://discord.gg/alphabetcartel
https://github.com/the-alphabet-cartel

# Ash

## 🎯 CORE SYSTEM VISION (Never to be violated):

### **Ash is a CRISIS DETECTION Ecosystem for Discord that**:
1. **FIRST**:
2. **SECOND**:
3. **FALLBACK**:
4. **PURPOSE**:

---

## Crisis Detection and Community Support Natural Language Processor
- `Ash`
  - https://github.com/the-alphabet-cartel/ash

## The Server
- `Ash`
  - Currently resides on a Debian 12 based Linux server that utilizes:
    - AMD Ryzen 7 5800x CPU
    - NVIDIA RTX 3060 with 12Gb VRAM GPU
    - 64Gb of RAM
    - Docker
      - We use a Docker first philosophy
        - Always containerize the code!
    - The server has an internal IP of 10.20.30.253

## Source Code and GitHub Repository Locations
- `Ash`: https://github.com/the-alphabet-cartel/ash

## General Instructions
- Read and follow the Clean Architecture Charter (`\10.20.30.253\nas\git\ash\docs\standards\clean_architecture_charter.md`) to the letter.
  - This is our bible for all code within the Ash ecosystem.
- Always ask for the current version of a specific file before making any modifications, changes, or edits to that file.
  - This is to ensure that we're both on the "same page" before making adjustments to the code.
- All hyperlinks shall be in lower case in the documentation as well as when trying to search GitHub.
- All references to The Alphabet Cartel or our discord server in documentation files shall include a link to the discord: https://discord.gg/alphabetcartel, as well as to our website: http://alphabetcartel.org.
- This is a collaborative project, as such do not use accusatory phrasing such as "your code", or "you forgot".  Instead use the inclusive "we" and "our".

### Coding Philosophy
- Modular Python Code
  - Separate the code into associated functions and methods as separate files based on the job that particular code class, or set of functions / methods is doing.
  - Python is only accessible from within the Docker container
    - `docker exec ash python *script_to_run.py*`
- **No Bash Scripting!**
- Configuration Variables and Settings
  - All default configuration variables and settings need to be defined in JSON files that are located in a directory named  `./config/`.
    - Standard format for use is defined in the Clean Architecture Charter
  - All associated managers for these JSON configuration files need to be located in a directory named `./managers/`
    - Standard format for use is defined in the Clean Architecture Charter
  - All configuration variables and settings need to be able to be overridden by environmental variables located in a `.env` file located at `./.env`
- Sensitive Information
  - All sensitive information (passwords, access tokens, API tokens, etc.) need to utilize Docker Secrets functionality

Adhering to these rules will ensure that the main code base stays clean and easy to read through for troubleshooting purposes, as well as to be easily able to add more functionality in the future.

---

**Built with care for chosen family** 🏳️‍🌈
