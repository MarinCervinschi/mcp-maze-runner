from mcp.server.fastmcp import FastMCP

from src.game import Game

# Create the FastMCP server
mcp = FastMCP("mcp-maze-runner")

# Global game instance to maintain state between tool calls
_game: Game | None = None


def get_game() -> Game:
    """Get the current game instance, creating one if needed."""
    global _game
    if _game is None:
        _game = Game.create_new()
    return _game


def reset_game_instance() -> Game:
    """Reset the game to a new instance."""
    global _game
    _game = Game.create_new()
    return _game


@mcp.tool()
def move(direction: str) -> dict:
    """
    Move the player in a cardinal direction.

    Args:
        direction: The direction to move - 'up', 'down', 'left', or 'right'

    Returns:
        Result with success status, message, and any events (key collected, reached exit)
    """
    game = get_game()
    result = game.move(direction)

    response = {
        "success": result.success,
        "message": result.message,
        "key_collected": result.key_collected,
        "reached_exit": result.reached_exit,
        "game_status": game.status.value,
    }
    if result.new_position:
        response["new_position"] = {
            "x": result.new_position.x,
            "y": result.new_position.y,
        }

    return response


@mcp.tool()
def look_around(visibility_range: int = 2) -> dict:
    """
    Look around the current position to see nearby cells.

    Args:
        visibility_range: How far to look (1-5, default: 2)

    Returns:
        Information about visible walls, keys, exit, and available movement directions
    """
    game = get_game()
    visibility_range = max(1, min(5, visibility_range))
    return game.look_around(visibility_range)


@mcp.tool()
def get_game_state() -> dict:
    """
    Get the complete current game state.

    Returns:
        Game state including player position, keys collected, moves made, and status
    """
    game = get_game()
    return game.get_state()


@mcp.tool()
def get_maze_display(fog_of_war: bool = False) -> str:
    """
    Get a visual ASCII representation of the maze.

    The player is shown as '@', walls as '#', keys as 'K', start as 'S', exit as 'E'.

    Args:
        fog_of_war: If true, only show visited/visible cells (default: false)

    Returns:
        ASCII art representation of the maze
    """
    game = get_game()
    return game.get_maze_display(fog_of_war)


@mcp.tool()
def reset_game() -> str:
    """
    Reset the game to start fresh with a new maze.

    Use this when the player wants to start over or after winning/losing.

    Returns:
        Confirmation message
    """
    reset_game_instance()
    return "Game has been reset. A new maze is ready! Use 'get_maze_display' to see it."


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
