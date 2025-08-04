# The Alphabet Cartel
We are an LGBTQIA+ Discord community centered around gaming, political discourse and activism, community, and societal advocacy.

We can be found on the internet and Discord at:
https://alphabetcartel.org
http://discord.gg/alphabetcartel
https://github.com/the-alphabet-cartel

# Ash-Thrash
## Crisis Detection and Community Support Discord Bot
- `Ash-Thrash`
  - https://github.com/the-alphabet-cartel/ash-thrash
  - GitHub submodule for the project `Ash`
    - https://github.com/the-alphabet-cartel/ash

## The Server
- `Ash-Thrash`
  - Currently resides on a Debian 12 based Linux server that utilizes:
    - AMD Ryzen 7 5800x CPU
    - NVIDIA RTX 3060 with 12Gb VRAM GPU
    - 64Gb of RAM
    - Docker
      - We use a Docker first philosophy, always containerize the code!
    - The server has an internal IP of 10.20.30.253.

## Source Code and GitHub Repository Locations
- `Ash-Thrash`: https://github.com/the-alphabet-cartel/ash-thrash
  - Discord Bot

## Port Assignments
- `Ash-Thrash`: 8884

## Instructions
- All hyperlinks shall be in lower case in the documentation as well as when trying to search GitHub.
- All references to The Alphabet Cartel or our discord server in documentation files shall include a link to the discord: https://discord.gg/alphabetcartel, as well as to our website: http://alphabetcartel.org.

### Coding Philosophy
- Modular Python Code
  - Separate the code into associated functions and methods as separate files based on the job that particular code class, or set of functions / methods is doing.
- Configuration Variables and Settings
  - All default configuration variables and settings need to be defined in JSON files that are located in a directory named  `ash-thrash/config/`
  - All associated managers for these JSON configuration files need to be located in a directory named `ash-thrash/managers/`
  - All configuration variables and settings need to be able to be overridden by environmental variables located in a `.env` file located at `ash-thrash/.env`
- Sensitive Information
  - All sensitive information (passwords, access tokens, API tokens, etc.) need to utilize Docker Secrets functionality

Please adhere to this as best as possible, as this will ensure that the main code base stays clean and easy to read through for troubleshooting purposes, as well as to be easily able to add more functionality in the future.