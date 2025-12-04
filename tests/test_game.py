"""Unit tests for the Game class."""

import pytest
from src.game import Game, GameStatus, MoveResult
from src.maze import Maze, Position, CellType
from src.character import Character


class TestGameCreation:
    """Tests for Game creation and initialization."""

    def test_create_new_default(self) -> None:
        """Test creating a new game with defaults."""
        game = Game.create_new()

        assert game.status == GameStatus.PLAYING
        assert game.character.position == game.maze.start_position
        assert game.total_keys == len(game.maze.key_positions)

    def test_create_new_custom_size(self) -> None:
        """Test creating a new game with custom size."""
        game = Game.create_new(width=8, height=8)

        assert game.maze.width == 8
        assert game.maze.height == 8

    def test_create_from_layout(self) -> None:
        """Test creating a game from a layout."""
        layout = [
            "#####",
            "#S.K#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)

        assert game.maze.width == 5
        assert game.maze.height == 5
        assert game.character.position == Position(1, 1)
        assert game.total_keys == 1


class TestGameMovement:
    """Tests for player movement in the game."""

    def test_move_valid_direction(self) -> None:
        """Test moving in a valid direction."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        result = game.move("right")

        assert result.success is True
        assert game.character.position == Position(2, 1)
        assert "Moved right" in result.message

    def test_move_into_wall(self) -> None:
        """Test that moving into a wall fails."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        result = game.move("up")

        assert result.success is False
        assert "wall" in result.message.lower()
        assert game.character.position == Position(1, 1)

    def test_move_invalid_direction(self) -> None:
        """Test that invalid direction fails."""
        game = Game.create_new()
        result = game.move("north")

        assert result.success is False
        assert "Invalid direction" in result.message

    def test_move_after_game_won(self) -> None:
        """Test that moving after winning fails."""
        layout = [
            "#####",
            "#S.E#",
            "#...#",
            "#...#",
            "#####",
        ]
        game = Game.from_layout(layout)
        game.move("right")
        game.move("right")  # Should win

        result = game.move("down")

        assert result.success is False
        assert "over" in result.message.lower()

    def test_move_collects_key(self) -> None:
        """Test that moving onto a key collects it."""
        layout = [
            "#####",
            "#SK.#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        result = game.move("right")

        assert result.success is True
        assert result.key_collected is True
        assert game.character.keys_collected == 1
        assert "key" in result.message.lower()

    def test_move_reaches_exit(self) -> None:
        """Test that reaching exit wins the game."""
        layout = [
            "#####",
            "#S.E#",
            "#...#",
            "#...#",
            "#####",
        ]
        game = Game.from_layout(layout)
        game.move("right")
        result = game.move("right")

        assert result.success is True
        assert result.reached_exit is True
        assert game.status == GameStatus.WON
        assert "exit" in result.message.lower()


class TestGameLookAround:
    """Tests for the look around functionality."""

    def test_look_around_basic(self) -> None:
        """Test basic look around functionality."""
        game = Game.create_new()
        info = game.look_around()

        assert "current_position" in info
        assert "visible_cells" in info
        assert "available_moves" in info

    def test_look_around_shows_walls(self) -> None:
        """Test that look around shows nearby walls."""
        layout = [
            "#####",
            "#S..#",
            "#.#.#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        info = game.look_around(visibility_range=3)

        assert len(info["visible_cells"]["walls"]) > 0

    def test_look_around_shows_keys(self) -> None:
        """Test that look around shows nearby keys."""
        layout = [
            "#####",
            "#SK.#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        info = game.look_around()

        assert len(info["visible_cells"]["keys"]) > 0


class TestGameAvailableMoves:
    """Tests for available moves functionality."""

    def test_get_available_moves_corner(self) -> None:
        """Test available moves from a corner."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        moves = game.get_available_moves()

        assert "right" in moves
        assert "down" in moves
        assert "up" not in moves
        assert "left" not in moves

    def test_get_available_moves_center(self) -> None:
        """Test available moves from the center."""
        layout = [
            "#####",
            "#...#",
            "#.S.#",
            "#...#",
            "#####",
        ]
        game = Game.from_layout(layout)
        moves = game.get_available_moves()

        assert "up" in moves
        assert "down" in moves
        assert "right" in moves
        assert "left" in moves


class TestGameState:
    """Tests for game state functionality."""

    def test_get_state(self) -> None:
        """Test getting game state."""
        game = Game.create_new()
        state = game.get_state()

        assert state["status"] == "playing"
        assert "player" in state
        assert "maze" in state
        assert "exit_position" in state

    def test_get_state_after_moves(self) -> None:
        """Test game state after making moves."""
        layout = [
            "#####",
            "#SK.#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        game.move("right")  # Collect key

        state = game.get_state()

        assert state["player"]["keys_collected"] == 1
        assert state["player"]["moves_made"] == 1
        assert state["maze"]["keys_remaining"] == 0


class TestGameDisplay:
    """Tests for maze display functionality."""

    def test_get_maze_display_no_fog(self) -> None:
        """Test getting maze display without fog of war."""
        layout = [
            "#####",
            "#S..#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        display = game.get_maze_display(fog_of_war=False)

        assert "@" in display  # Player marker
        assert "E" in display  # Exit visible

    def test_get_maze_display_with_fog(self) -> None:
        """Test getting maze display with fog of war."""
        layout = [
            "##########",
            "#S.......#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#.......E#",
            "##########",
        ]
        game = Game.from_layout(layout)
        display = game.get_maze_display(fog_of_war=True)

        assert "@" in display  # Player marker
        assert "?" in display  # Hidden cells


class TestGameReset:
    """Tests for game reset functionality."""

    def test_reset_game(self) -> None:
        """Test resetting the game."""
        layout = [
            "#####",
            "#SK.#",
            "#...#",
            "#..E#",
            "#####",
        ]
        game = Game.from_layout(layout)
        game.move("right")  # Collect key
        game.move("right")
        game.move("down")

        game.reset()

        assert game.status == GameStatus.PLAYING
        assert game.character.position == game.maze.start_position
        assert game.character.keys_collected == 0
        assert game.character.moves_made == 0


class TestMoveResult:
    """Tests for the MoveResult dataclass."""

    def test_move_result_creation(self) -> None:
        """Test creating a MoveResult."""
        result = MoveResult(
            success=True,
            message="Test message",
            new_position=Position(2, 2),
            key_collected=True,
            reached_exit=False,
        )

        assert result.success is True
        assert result.message == "Test message"
        assert result.new_position == Position(2, 2)
        assert result.key_collected is True
        assert result.reached_exit is False

    def test_move_result_defaults(self) -> None:
        """Test MoveResult default values."""
        result = MoveResult(success=False, message="Failed")

        assert result.new_position is None
        assert result.key_collected is False
        assert result.reached_exit is False


class TestGameRepr:
    """Tests for game string representation."""

    def test_game_repr(self) -> None:
        """Test game string representation."""
        game = Game.create_new()
        repr_str = repr(game)

        assert "Game" in repr_str
        assert "status=playing" in repr_str
