"""Unit tests for the Maze class."""

import pytest
from src.maze import Maze, Position, CellType, DIRECTIONS


class TestPosition:
    """Tests for the Position dataclass."""

    def test_position_creation(self) -> None:
        """Test creating a position."""
        pos = Position(3, 5)
        assert pos.x == 3
        assert pos.y == 5

    def test_position_equality(self) -> None:
        """Test position equality comparison."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 1)

        assert pos1 == pos2
        assert pos1 != pos3

    def test_position_hash(self) -> None:
        """Test that positions can be used in sets and dicts."""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)

        positions = {pos1, pos2}
        assert len(positions) == 1

    def test_position_addition(self) -> None:
        """Test adding two positions."""
        pos1 = Position(1, 2)
        pos2 = Position(3, 4)
        result = pos1 + pos2

        assert result.x == 4
        assert result.y == 6

    def test_position_to_tuple(self) -> None:
        """Test converting position to tuple."""
        pos = Position(5, 10)
        assert pos.to_tuple() == (5, 10)


class TestDirections:
    """Tests for direction constants."""

    def test_all_directions_exist(self) -> None:
        """Test that all four cardinal directions are defined."""
        assert "north" in DIRECTIONS
        assert "south" in DIRECTIONS
        assert "east" in DIRECTIONS
        assert "west" in DIRECTIONS

    def test_direction_offsets(self) -> None:
        """Test that direction offsets are correct."""
        assert DIRECTIONS["north"] == Position(0, -1)
        assert DIRECTIONS["south"] == Position(0, 1)
        assert DIRECTIONS["east"] == Position(1, 0)
        assert DIRECTIONS["west"] == Position(-1, 0)


class TestMaze:
    """Tests for the Maze class."""

    def test_maze_creation_valid_dimensions(self) -> None:
        """Test creating a maze with valid dimensions."""
        maze = Maze(width=5, height=5)
        assert maze.width == 5
        assert maze.height == 5

    def test_maze_creation_invalid_width_too_small(self) -> None:
        """Test that creating a maze with width < 5 raises error."""
        with pytest.raises(ValueError, match="Width must be between 5 and 10"):
            Maze(width=4, height=5)

    def test_maze_creation_invalid_width_too_large(self) -> None:
        """Test that creating a maze with width > 10 raises error."""
        with pytest.raises(ValueError, match="Width must be between 5 and 10"):
            Maze(width=11, height=5)

    def test_maze_creation_invalid_height_too_small(self) -> None:
        """Test that creating a maze with height < 5 raises error."""
        with pytest.raises(ValueError, match="Height must be between 5 and 10"):
            Maze(width=5, height=4)

    def test_maze_creation_invalid_height_too_large(self) -> None:
        """Test that creating a maze with height > 10 raises error."""
        with pytest.raises(ValueError, match="Height must be between 5 and 10"):
            Maze(width=5, height=11)

    def test_create_default_maze(self) -> None:
        """Test creating a default maze."""
        maze = Maze.create_default(7, 7)

        assert maze.width == 7
        assert maze.height == 7
        assert maze.start_position == Position(1, 1)
        assert maze.exit_position == Position(5, 5)
        assert len(maze.grid) == 7
        assert all(len(row) == 7 for row in maze.grid)

    def test_create_maze_from_layout(self) -> None:
        """Test creating a maze from a string layout."""
        layout = [
            "#####",
            "#S..#",
            "#.#.#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)

        assert maze.width == 5
        assert maze.height == 5
        assert maze.start_position == Position(1, 1)
        assert maze.exit_position == Position(3, 3)

    def test_from_layout_with_keys(self) -> None:
        """Test creating a maze with keys from layout."""
        layout = [
            "#####",
            "#S.K#",
            "#.#.#",
            "#K.E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)

        assert len(maze.key_positions) == 2
        assert Position(3, 1) in maze.key_positions
        assert Position(1, 3) in maze.key_positions

    def test_is_valid_position(self) -> None:
        """Test position validation."""
        maze = Maze.create_default(5, 5)

        assert maze.is_valid_position(Position(0, 0)) is True
        assert maze.is_valid_position(Position(4, 4)) is True
        assert maze.is_valid_position(Position(2, 2)) is True
        assert maze.is_valid_position(Position(-1, 0)) is False
        assert maze.is_valid_position(Position(0, -1)) is False
        assert maze.is_valid_position(Position(5, 0)) is False
        assert maze.is_valid_position(Position(0, 5)) is False

    def test_is_walkable(self) -> None:
        """Test walkable cell checking."""
        layout = [
            "#####",
            "#S..#",
            "#.#.#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)

        # Walls should not be walkable
        assert maze.is_walkable(Position(0, 0)) is False
        assert maze.is_walkable(Position(2, 2)) is False

        # Empty cells should be walkable
        assert maze.is_walkable(Position(1, 1)) is True
        assert maze.is_walkable(Position(2, 1)) is True

        # Out of bounds should not be walkable
        assert maze.is_walkable(Position(-1, 0)) is False
        assert maze.is_walkable(Position(10, 10)) is False

    def test_get_cell(self) -> None:
        """Test getting cell type at position."""
        layout = [
            "#####",
            "#S.K#",
            "#.#.#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)

        assert maze.get_cell(Position(0, 0)) == CellType.WALL
        assert maze.get_cell(Position(1, 1)) == CellType.START
        assert maze.get_cell(Position(2, 1)) == CellType.EMPTY
        assert maze.get_cell(Position(3, 1)) == CellType.KEY
        assert maze.get_cell(Position(3, 3)) == CellType.EXIT

    def test_get_cell_out_of_bounds(self) -> None:
        """Test that getting cell out of bounds raises error."""
        maze = Maze.create_default(5, 5)

        with pytest.raises(IndexError):
            maze.get_cell(Position(10, 10))

    def test_set_cell(self) -> None:
        """Test setting cell type at position."""
        maze = Maze.create_default(5, 5)
        maze.set_cell(Position(2, 2), CellType.KEY)

        assert maze.get_cell(Position(2, 2)) == CellType.KEY

    def test_remove_key(self) -> None:
        """Test removing a key from the maze."""
        layout = [
            "#####",
            "#S.K#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)
        key_pos = Position(3, 1)

        assert key_pos in maze.key_positions
        assert maze.remove_key(key_pos) is True
        assert key_pos not in maze.key_positions
        assert maze.get_cell(key_pos) == CellType.EMPTY

    def test_remove_key_no_key(self) -> None:
        """Test removing a key where there is none."""
        maze = Maze.create_default(5, 5)
        assert maze.remove_key(Position(2, 2)) is False

    def test_has_key_at(self) -> None:
        """Test checking for key at position."""
        layout = [
            "#####",
            "#S.K#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)

        assert maze.has_key_at(Position(3, 1)) is True
        assert maze.has_key_at(Position(2, 2)) is False

    def test_is_exit(self) -> None:
        """Test checking if position is exit."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)

        assert maze.is_exit(Position(3, 3)) is True
        assert maze.is_exit(Position(1, 1)) is False

    def test_get_visible_cells(self) -> None:
        """Test getting visible cells around position."""
        maze = Maze.create_default(7, 7)
        visible = maze.get_visible_cells(Position(3, 3), visibility_range=1)

        # Should include 3x3 area around position
        assert len(visible) == 9
        assert Position(3, 3) in visible
        assert Position(2, 2) in visible
        assert Position(4, 4) in visible

    def test_to_string_without_player(self) -> None:
        """Test converting maze to string without player."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)
        result = maze.to_string()

        assert "#####" in result
        assert "S" in result
        assert "E" in result

    def test_to_string_with_player(self) -> None:
        """Test converting maze to string with player position."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        maze = Maze.from_layout(layout)
        result = maze.to_string(player_position=Position(2, 2))

        assert "@" in result

    def test_maze_repr(self) -> None:
        """Test maze string representation."""
        maze = Maze.create_default(5, 5)
        assert "Maze(width=5, height=5)" in repr(maze)
