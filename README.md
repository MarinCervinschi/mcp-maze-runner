# 🎮 MCP Maze Runner

An interactive maze game controlled through natural language chat, built to demonstrate the Model Context Protocol (MCP) integration with AI agents.

## Overview

**MCP Maze Runner** is an educational project that showcases how to build an AI-powered game using the Model Context Protocol. Players navigate a maze by chatting with an AI agent, which uses MCP tools to control the game. The agent interprets natural language commands like "move forward" or "look around" and translates them into game actions.

### Architecture

```mermaid
graph TD
    A[User Chat Input] --> B[Google ADK Agent]
    B --> C[MCP Server]
    C --> D[Game Logic]
    D -.-> C
    C -.-> B
    B -.-> A
    
    subgraph "Game State Loop"
        D --> C
        C --> B
        B --> A
    end
```

## Features

### Core Features
- **Natural Language Control**: Command your character using plain English
- **Interactive Maze**: Navigate through a grid-based maze with obstacles
- **AI-Powered Agent**: Intelligent interpretation of player intentions
- **MCP Integration**: Full implementation of Model Context Protocol

### Game Mechanics
- 🚶 **Movement**: Navigate in four directions (North, South, East, West)
- 🧱 **Obstacles**: Walls block your path, requiring strategic thinking
- 🔑 **Keys**: Collect keys to unlock special doors
- 🚪 **Exit**: Find and reach the maze exit to win

### MCP Tools Exposed
- `move(direction)` - Move the player in a cardinal direction (north, south, east, west)
- `look_around(visibility_range)` - See nearby cells, walls, keys, and available moves
- `get_game_state()` - Get complete game state (position, keys, moves, status)
- `get_maze_display(fog_of_war)` - Get ASCII visualization of the maze
- `reset_game()` - Reset the game to start fresh with a new maze

## Installation & Usage

### 1. Install uv if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# pip
pip install uv
```

### 2. Clone and Setup:

```bash
# clone the repo
git clone https://github.com/MarinCervinschi/mcp-maze-runner.git
cd mcp-maze-runner

# install dependencies
uv sync
```

### 3. Configure API Key
- Create a `.env` file in the `root_agent` directory with your Google API key:

```text
GOOGLE_API_KEY=your_google_api_key_here
```

you can obtain an API key from the [Google AI Studio](https://aistudio.google.com/api-keys).

### 4. Run the Application:

```bash
uv run adk web
```
- Open your browser and navigate to [http://localhost:8000](http://localhost:8000) to start playing!
- This is the adk web chat interface where you can interact with the maze runner agent.

### 5. Alternatively, you can run the game and play in the terminal:

```bash
uv run python main.py
```
- This will start the game in your terminal, allowing you to interact with the maze directly.
- In this mode you don't use the AI agent or the MCP tools, but it's a fun way to experience the maze!

### Running Tests

```bash
uv run pytest tests/ -v
```

## Technology Stack

### Backend
- **Python 3.10+**: Core programming language
- **MCP Library** (`mcp`): Model Context Protocol implementation
- **Google ADK**: AI agent framework with Gemini integration

## License

MIT License - feel free to use this project for learning and teaching.