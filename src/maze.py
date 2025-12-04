from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class CellType(Enum):
    """Enumeration of possible cell types in the maze."""

    EMPTY = "."
    WALL = "#"
    START = "S"
    EXIT = "E"
    KEY = "K"


@dataclass
class Position:
    """Represents a 2D position in the maze."""

    x: int
    y: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def to_tuple(self) -> tuple[int, int]:
        """Convert position to tuple."""
        return (self.x, self.y)


# Direction offsets for movement
DIRECTIONS: dict[str, Position] = {
    "up": Position(0, -1),
    "down": Position(0, 1),
    "right": Position(1, 0),
    "left": Position(-1, 0),
}


@dataclass
class Maze:
    """
    Represents a grid-based maze.

    The maze is a 2D grid where each cell can be empty, a wall, the start position,
    the exit, or contain an item (like a key).

    Attributes:
        width: The width of the maze (5-10).
        height: The height of the maze (5-10).
        grid: 2D list representing the maze cells.
        start_position: The starting position in the maze.
        exit_position: The exit position in the maze.
        key_positions: Set of positions containing keys.
    """

    width: int
    height: int
    grid: list[list[CellType]] = field(default_factory=list)
    start_position: Position = field(default_factory=lambda: Position(0, 0))
    exit_position: Position = field(default_factory=lambda: Position(0, 0))
    key_positions: set[Position] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Validate maze dimensions."""
        if not (5 <= self.width <= 10):
            raise ValueError(f"Width must be between 5 and 10, got {self.width}")
        if not (5 <= self.height <= 10):
            raise ValueError(f"Height must be between 5 and 10, got {self.height}")

    @classmethod
    def create_default(cls, width: int = 7, height: int = 7) -> Maze:
        """
        Create a default maze with predefined layout.

        Args:
            width: Width of the maze (5-10).
            height: Height of the maze (5-10).

        Returns:
            A new Maze instance with a default layout.
        """
        maze = cls(width=width, height=height)
        maze._initialize_empty_grid()
        maze._add_default_walls()
        maze._set_start_and_exit()
        maze._add_keys()
        return maze

    @classmethod
    def from_layout(cls, layout: list[str]) -> Maze:
        """
        Create a maze from a string layout.

        Args:
            layout: List of strings representing the maze.
                    Characters: '#' = wall, '.' = empty, 'S' = start,
                               'E' = exit, 'K' = key

        Returns:
            A new Maze instance based on the layout.
        """
        height = len(layout)
        width = len(layout[0]) if layout else 0

        maze = cls(width=width, height=height)
        maze.grid = []
        maze.key_positions = set()

        for y, row in enumerate(layout):
            grid_row: list[CellType] = []
            for x, char in enumerate(row):
                cell_type = cls._char_to_cell_type(char)
                grid_row.append(cell_type)

                if cell_type == CellType.START:
                    maze.start_position = Position(x, y)
                elif cell_type == CellType.EXIT:
                    maze.exit_position = Position(x, y)
                elif cell_type == CellType.KEY:
                    maze.key_positions.add(Position(x, y))

            maze.grid.append(grid_row)

        return maze

    @staticmethod
    def _char_to_cell_type(char: str) -> CellType:
        """Convert a character to a CellType."""
        mapping = {
            "#": CellType.WALL,
            ".": CellType.EMPTY,
            "S": CellType.START,
            "E": CellType.EXIT,
            "K": CellType.KEY,
        }
        return mapping.get(char, CellType.EMPTY)

    def _initialize_empty_grid(self) -> None:
        """Initialize the grid with empty cells and border walls."""
        self.grid = []
        for y in range(self.height):
            row: list[CellType] = []
            for x in range(self.width):
                # Create border walls
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    row.append(CellType.WALL)
                else:
                    row.append(CellType.EMPTY)
            self.grid.append(row)

    def _add_default_walls(self) -> None:
        """Add some internal walls to make the maze interesting."""
        # Add some internal walls based on maze size
        internal_walls = [
            (2, 1),
            (2, 2),
            (2, 3),
            (4, 3),
            (4, 4),
            (4, 5),
            (1, 5),
            (2, 5),
            (5, 1),
        ]
        for x, y in internal_walls:
            if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                self.grid[y][x] = CellType.WALL

    def _set_start_and_exit(self) -> None:
        """Set the start and exit positions."""
        self.start_position = Position(1, 1)
        self.exit_position = Position(self.width - 2, self.height - 2)
        self.grid[self.start_position.y][self.start_position.x] = CellType.START
        self.grid[self.exit_position.y][self.exit_position.x] = CellType.EXIT

    def _add_keys(self) -> None:
        """Add keys to the maze."""
        self.key_positions = set()
        # Add a key in a strategic location
        key_pos = Position(3, 2)
        if self.is_valid_position(key_pos) and self.get_cell(key_pos) == CellType.EMPTY:
            self.grid[key_pos.y][key_pos.x] = CellType.KEY
            self.key_positions.add(key_pos)

        key_pos2 = Position(self.width - 3, self.height - 3)
        if (
            self.is_valid_position(key_pos2)
            and self.get_cell(key_pos2) == CellType.EMPTY
        ):
            self.grid[key_pos2.y][key_pos2.x] = CellType.KEY
            self.key_positions.add(key_pos2)

    def is_valid_position(self, position: Position) -> bool:
        """
        Check if a position is within the maze bounds.

        Args:
            position: The position to check.

        Returns:
            True if the position is within bounds, False otherwise.
        """
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def is_walkable(self, position: Position) -> bool:
        """
        Check if a position can be walked on (not a wall).

        Args:
            position: The position to check.

        Returns:
            True if the position is walkable, False otherwise.
        """
        if not self.is_valid_position(position):
            return False
        return self.grid[position.y][position.x] != CellType.WALL

    def get_cell(self, position: Position) -> CellType:
        """
        Get the cell type at a given position.

        Args:
            position: The position to query.

        Returns:
            The CellType at the position.

        Raises:
            IndexError: If the position is out of bounds.
        """
        if not self.is_valid_position(position):
            raise IndexError(f"Position {position} is out of bounds")
        return self.grid[position.y][position.x]

    def set_cell(self, position: Position, cell_type: CellType) -> None:
        """
        Set the cell type at a given position.

        Args:
            position: The position to modify.
            cell_type: The new cell type.

        Raises:
            IndexError: If the position is out of bounds.
        """
        if not self.is_valid_position(position):
            raise IndexError(f"Position {position} is out of bounds")
        self.grid[position.y][position.x] = cell_type

    def remove_key(self, position: Position) -> bool:
        """
        Remove a key from the given position.

        Args:
            position: The position to remove the key from.

        Returns:
            True if a key was removed, False otherwise.
        """
        if position in self.key_positions:
            self.key_positions.remove(position)
            self.grid[position.y][position.x] = CellType.EMPTY
            return True
        return False

    def has_key_at(self, position: Position) -> bool:
        """
        Check if there's a key at the given position.

        Args:
            position: The position to check.

        Returns:
            True if there's a key at the position, False otherwise.
        """
        return position in self.key_positions

    def is_exit(self, position: Position) -> bool:
        """
        Check if the given position is the exit.

        Args:
            position: The position to check.

        Returns:
            True if the position is the exit, False otherwise.
        """
        return position == self.exit_position

    def get_visible_cells(
        self, position: Position, visibility_range: int = 2
    ) -> dict[Position, CellType]:
        """
        Get visible cells around a position (fog of war).

        Args:
            position: The center position.
            visibility_range: How far the player can see.

        Returns:
            Dictionary mapping positions to their cell types.
        """
        visible: dict[Position, CellType] = {}
        for dy in range(-visibility_range, visibility_range + 1):
            for dx in range(-visibility_range, visibility_range + 1):
                check_pos = Position(position.x + dx, position.y + dy)
                if self.is_valid_position(check_pos):
                    visible[check_pos] = self.get_cell(check_pos)
        return visible

    def to_string(self, player_position: Position | None = None) -> str:
        """
        Convert the maze to a string representation.

        Args:
            player_position: Optional player position to display.

        Returns:
            String representation of the maze.
        """
        lines: list[str] = []
        for y in range(self.height):
            row_chars: list[str] = []
            for x in range(self.width):
                pos = Position(x, y)
                if player_position and pos == player_position:
                    row_chars.append("@")
                else:
                    row_chars.append(self.grid[y][x].value)
            lines.append("".join(row_chars))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Maze(width={self.width}, height={self.height})"
