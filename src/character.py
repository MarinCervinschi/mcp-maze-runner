from __future__ import annotations

from dataclasses import dataclass, field

from src.maze import Position, DIRECTIONS


@dataclass
class Character:
    """
    Represents a player character in the maze.

    Attributes:
        position: Current position of the character.
        keys_collected: Number of keys the character has collected.
        moves_made: Total number of moves made.
        visited_positions: Set of all positions the character has visited.
    """

    position: Position = field(default_factory=lambda: Position(1, 1))
    keys_collected: int = 0
    moves_made: int = 0
    visited_positions: set[Position] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Initialize the visited positions with the starting position."""
        self.visited_positions.add(self.position)

    def move(self, direction: str) -> Position:
        """
        Calculate the new position after moving in a direction.

        This method does NOT update the character's position - it only
        calculates where the character would be if they moved.

        Args:
            direction: The direction to move ('north', 'south', 'east', 'west').

        Returns:
            The new position after the move.

        Raises:
            ValueError: If the direction is invalid.
        """
        direction_lower = direction.lower()
        if direction_lower not in DIRECTIONS:
            raise ValueError(
                f"Invalid direction: {direction}. "
                f"Valid directions are: {', '.join(DIRECTIONS.keys())}"
            )

        offset = DIRECTIONS[direction_lower]
        return self.position + offset

    def set_position(self, new_position: Position) -> None:
        """
        Set the character's position and update tracking.

        Args:
            new_position: The new position to set.
        """
        self.position = new_position
        self.moves_made += 1
        self.visited_positions.add(new_position)

    def collect_key(self) -> None:
        """Increment the key count when collecting a key."""
        self.keys_collected += 1

    def reset(self, start_position: Position) -> None:
        """
        Reset the character to initial state.

        Args:
            start_position: The starting position to reset to.
        """
        self.position = start_position
        self.keys_collected = 0
        self.moves_made = 0
        self.visited_positions = {start_position}

    def get_stats(self) -> dict[str, int]:
        """
        Get character statistics.

        Returns:
            Dictionary with character stats.
        """
        return {
            "keys_collected": self.keys_collected,
            "moves_made": self.moves_made,
            "positions_visited": len(self.visited_positions),
        }

    def __repr__(self) -> str:
        return (
            f"Character(position={self.position}, "
            f"keys={self.keys_collected}, moves={self.moves_made})"
        )
