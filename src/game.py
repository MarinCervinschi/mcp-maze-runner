from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.maze import Maze, Position, CellType, DIRECTIONS
from src.character import Character


class GameStatus(Enum):
    """Enumeration of possible game states."""

    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


@dataclass
class MoveResult:
    """Result of a movement attempt."""

    success: bool
    message: str
    new_position: Position | None = None
    key_collected: bool = False
    reached_exit: bool = False


@dataclass
class Game:
    """
    Main game class that orchestrates the maze game.

    Manages the maze, character, and game state. Provides methods for
    player movement, item collection, and game status tracking.

    Attributes:
        maze: The maze instance.
        character: The player character.
        status: Current game status.
        total_keys: Total number of keys in the maze.
    """

    maze: Maze = field(default_factory=lambda: Maze.create_default())
    character: Character = field(default_factory=Character)
    status: GameStatus = GameStatus.PLAYING
    total_keys: int = 0

    def __post_init__(self) -> None:
        """Initialize game state after dataclass initialization."""
        self.character.position = self.maze.start_position
        self.character.visited_positions = {self.maze.start_position}
        self.total_keys = len(self.maze.key_positions)

    @classmethod
    def create_new(cls, width: int = 7, height: int = 7) -> Game:
        """
        Create a new game with a default maze.

        Args:
            width: Width of the maze.
            height: Height of the maze.

        Returns:
            A new Game instance.
        """
        maze = Maze.create_default(width, height)
        character = Character(position=maze.start_position)
        game = cls(maze=maze, character=character)
        game.total_keys = len(maze.key_positions)
        return game

    @classmethod
    def from_layout(cls, layout: list[str]) -> Game:
        """
        Create a game from a maze layout.

        Args:
            layout: List of strings representing the maze.

        Returns:
            A new Game instance.
        """
        maze = Maze.from_layout(layout)
        character = Character(position=maze.start_position)
        game = cls(maze=maze, character=character)
        game.total_keys = len(maze.key_positions)
        return game

    def move(self, direction: str) -> MoveResult:
        """
        Attempt to move the player in a direction.

        Args:
            direction: The direction to move ('north', 'south', 'east', 'west').

        Returns:
            MoveResult with success status and details.
        """
        if self.status != GameStatus.PLAYING:
            return MoveResult(
                success=False,
                message=f"Game is over. Status: {self.status.value}",
            )

        # Validate direction
        direction_lower = direction.lower()
        if direction_lower not in DIRECTIONS:
            return MoveResult(
                success=False,
                message=(
                    f"Invalid direction: '{direction}'. "
                    f"Valid directions: {', '.join(DIRECTIONS.keys())}"
                ),
            )

        # Calculate new position
        new_position = self.character.move(direction)

        # Check if movement is valid
        if not self.maze.is_walkable(new_position):
            return MoveResult(
                success=False,
                message=f"Cannot move {direction_lower}: there's a wall!",
                new_position=self.character.position,
            )

        # Move the character
        self.character.set_position(new_position)

        # Check for key collection
        key_collected = False
        if self.maze.has_key_at(new_position):
            self.maze.remove_key(new_position)
            self.character.collect_key()
            key_collected = True

        # Check for exit
        reached_exit = self.maze.is_exit(new_position)
        if reached_exit:
            self.status = GameStatus.WON

        # Build result message
        message = f"Moved {direction_lower} to position ({new_position.x}, {new_position.y})."
        if key_collected:
            message += " You collected a key! 🔑"
        if reached_exit:
            message += " Congratulations! You reached the exit! 🎉"

        return MoveResult(
            success=True,
            message=message,
            new_position=new_position,
            key_collected=key_collected,
            reached_exit=reached_exit,
        )

    def look_around(self, visibility_range: int = 2) -> dict[str, Any]:
        """
        Get information about the player's surroundings.

        Args:
            visibility_range: How far the player can see.

        Returns:
            Dictionary with visibility information.
        """
        visible_cells = self.maze.get_visible_cells(
            self.character.position, visibility_range
        )

        # Convert to serializable format
        visible_info: dict[str, list[dict[str, Any]]] = {
            "walls": [],
            "empty": [],
            "keys": [],
            "exit": [],
            "start": [],
        }

        for pos, cell_type in visible_cells.items():
            pos_dict = {"x": pos.x, "y": pos.y}
            if cell_type == CellType.WALL:
                visible_info["walls"].append(pos_dict)
            elif cell_type == CellType.KEY:
                visible_info["keys"].append(pos_dict)
            elif cell_type == CellType.EXIT:
                visible_info["exit"].append(pos_dict)
            elif cell_type == CellType.START:
                visible_info["start"].append(pos_dict)
            else:
                visible_info["empty"].append(pos_dict)

        # Get available directions
        available_moves = self.get_available_moves()

        return {
            "current_position": {
                "x": self.character.position.x,
                "y": self.character.position.y,
            },
            "visible_cells": visible_info,
            "available_moves": available_moves,
        }

    def get_available_moves(self) -> list[str]:
        """
        Get list of valid movement directions from current position.

        Returns:
            List of valid direction strings.
        """
        available: list[str] = []
        for direction in DIRECTIONS:
            new_pos = self.character.move(direction)
            if self.maze.is_walkable(new_pos):
                available.append(direction)
        return available

    def get_state(self) -> dict[str, Any]:
        """
        Get the complete game state.

        Returns:
            Dictionary with all game state information.
        """
        return {
            "status": self.status.value,
            "player": {
                "position": {
                    "x": self.character.position.x,
                    "y": self.character.position.y,
                },
                "keys_collected": self.character.keys_collected,
                "moves_made": self.character.moves_made,
            },
            "maze": {
                "width": self.maze.width,
                "height": self.maze.height,
                "total_keys": self.total_keys,
                "keys_remaining": len(self.maze.key_positions),
            },
            "exit_position": {
                "x": self.maze.exit_position.x,
                "y": self.maze.exit_position.y,
            },
        }

    def get_maze_display(self, fog_of_war: bool = False) -> str:
        """
        Get a string representation of the maze.

        Args:
            fog_of_war: If True, only show visited/visible cells.

        Returns:
            String representation of the maze.
        """
        if not fog_of_war:
            return self.maze.to_string(self.character.position)

        # Fog of war mode - only show visible cells
        visible = self.maze.get_visible_cells(self.character.position, visibility_range=2)
        lines: list[str] = []

        for y in range(self.maze.height):
            row_chars: list[str] = []
            for x in range(self.maze.width):
                pos = Position(x, y)
                if pos == self.character.position:
                    row_chars.append("@")
                elif pos in visible:
                    row_chars.append(self.maze.grid[y][x].value)
                elif pos in self.character.visited_positions:
                    # Show visited but not currently visible as dimmed
                    row_chars.append("·")
                else:
                    row_chars.append("?")
            lines.append("".join(row_chars))

        return "\n".join(lines)

    def reset(self) -> None:
        """Reset the game to initial state with the same maze layout."""
        # Restore keys to their original positions
        # We need to recreate the maze to restore keys
        self.maze = Maze.create_default(self.maze.width, self.maze.height)
        self.character.reset(self.maze.start_position)
        self.total_keys = len(self.maze.key_positions)
        self.status = GameStatus.PLAYING

    def __repr__(self) -> str:
        return (
            f"Game(status={self.status.value}, "
            f"player_pos={self.character.position}, "
            f"keys={self.character.keys_collected}/{self.total_keys})"
        )
