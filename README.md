# 🔎 Convolyzer

Convolyzer is a Discord bot that aims to help community manager and members
to better understand each other and improve interactions between the members. It uses NLP methods and
tries to provide more accurate result. Feel free to add it in your
server and play with it!

## 🧰 Features

The main features of this project are:

- Mood and MBTI analysis
- Summary and topics extraction
- Social graph representation

## 📦 Installation

### 👾 Create your Discord application

- Create a new bot app by following [this guide](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot).
- Invite your bot in your server by following [this guide](https://discordjs.guide/preparations/adding-your-bot-to-servers.html).

### 📥 Get the source code

Clone the code of the repos locally and go into the directory.

### 💻 Setup System dependencies

In order to run the bot on your computer, you must have the following packages installed:

- Python 3.11+
- Graphviz 9.0+
- Build tools (GCC 12.3+)

If you are on a Debian-based Linux distribution, you can use:

```
apt update && apt upgrade
apt install build-essential graphviz libgraphviz-dev python3-dev
```

If you are on NixOS, simply run `nix develop` (recommended) or `nix-shell` in
the project directory and go to the [configuration section](#configuration).

### 🔨 Setup Python Environment

We will install all Python dependencies inside a virtual env, but you can choose your way.

1. Make sure Python virtual env tool is installed.
2. Create a virtual env with `python3 -m venv venv`
3. Activate your virtual env with `source venv/bin/activate`
4. Install dependencies with `pip install -r requirements.txt`

You are ready!

### 📝 Configuration

In this part, we will write the configuration file in order to run the bot.

1. Create the config file based on the example: `cp config.example.json config.json`
2. Fill the configuration file with your preferences and login token.

### 📔 Note about configuration fields

- **token**: This is the bot's token.
- **staff_team**: The list of users' ID who can call staff command.
- **debug**: If the bot will deploy global commands or just guild commands in
  the `test_guild`.
- **test_guild**: The guild where deploy app command in debug mode.
- **color**: The color used in the bot's message.
- **prefix**: The bot's prefix.

## 🏁 Run the bot

After all that, you just have to run `python main.py` to start the bot!

## 📚 Generate the documentation

To generate the documentation, you just have to run:

`sphinx-build -M html docs/source/ docs/build/`

Then you can open the `index.html` in the `docs/build/html` folder.
