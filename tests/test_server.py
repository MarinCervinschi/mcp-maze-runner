"""Unit tests for the MCP server tools."""

from src.server import (
    get_game,
    reset_game_instance,
    move,
    look_around,
    get_game_state,
    get_maze_display,
    reset_game,
)
from src.game import GameStatus


class TestServerGameManagement:
    """Tests for game instance management."""

    def setup_method(self) -> None:
        """Reset game state before each test."""
        reset_game_instance()

    def test_get_game_creates_instance(self) -> None:
        """Test that get_game creates a game if none exists."""
        import src.server

        src.server._game = None
        game = get_game()
        assert game is not None
        assert game.status == GameStatus.PLAYING

    def test_get_game_returns_same_instance(self) -> None:
        """Test that get_game returns the same instance."""
        game1 = get_game()
        game2 = get_game()
        assert game1 is game2

    def test_reset_game_instance_creates_new(self) -> None:
        """Test that reset_game_instance creates a new game."""
        game1 = get_game()
        game1.move("right")  # Make some changes
        game2 = reset_game_instance()
        assert game2.character.moves_made == 0


class TestMoveTool:
    """Tests for the move tool."""

    def setup_method(self) -> None:
        """Reset game state before each test."""
        reset_game_instance()

    def test_move_valid_direction(self) -> None:
        """Test moving in a valid direction."""
        result = move("down")
        assert result["success"] is True
        assert "Moved down" in result["message"]
        assert result["game_status"] == "playing"

    def test_move_into_wall(self) -> None:
        """Test moving into a wall."""
        result = move("up")
        assert result["success"] is False
        assert "wall" in result["message"].lower()

    def test_move_invalid_direction(self) -> None:
        """Test moving in an invalid direction."""
        result = move("north")
        assert result["success"] is False
        assert "Invalid direction" in result["message"]

    def test_move_returns_position(self) -> None:
        """Test that successful move returns new position."""
        result = move("down")
        assert result["success"] is True
        assert "new_position" in result
        assert "x" in result["new_position"]
        assert "y" in result["new_position"]


class TestLookAroundTool:
    """Tests for the look_around tool."""

    def setup_method(self) -> None:
        """Reset game state before each test."""
        reset_game_instance()

    def test_look_around_returns_info(self) -> None:
        """Test that look_around returns visibility info."""
        result = look_around()
        assert "current_position" in result
        assert "visible_cells" in result
        assert "available_moves" in result

    def test_look_around_custom_range(self) -> None:
        """Test look_around with custom visibility range."""
        result = look_around(visibility_range=3)
        assert "visible_cells" in result

    def test_look_around_clamps_range(self) -> None:
        """Test that visibility range is clamped to valid values."""
        result1 = look_around(visibility_range=0)
        result2 = look_around(visibility_range=10)
        # Both should return valid results
        assert "visible_cells" in result1
        assert "visible_cells" in result2


class TestGetGameStateTool:
    """Tests for the get_game_state tool."""

    def setup_method(self) -> None:
        """Reset game state before each test."""
        reset_game_instance()

    def test_get_game_state_returns_state(self) -> None:
        """Test that get_game_state returns complete state."""
        result = get_game_state()
        assert "status" in result
        assert "player" in result
        assert "maze" in result
        assert "exit_position" in result

    def test_get_game_state_reflects_moves(self) -> None:
        """Test that state reflects moves made."""
        move("down")
        result = get_game_state()
        assert result["player"]["moves_made"] == 1


class TestGetMazeDisplayTool:
    """Tests for the get_maze_display tool."""

    def setup_method(self) -> None:
        """Reset game state before each test."""
        reset_game_instance()

    def test_get_maze_display_returns_string(self) -> None:
        """Test that maze display returns a string."""
        result = get_maze_display()
        assert isinstance(result, str)
        assert "@" in result  # Player marker
        assert "#" in result  # Wall markers

    def test_get_maze_display_fog_of_war(self) -> None:
        """Test maze display with fog of war enabled."""
        result = get_maze_display(fog_of_war=True)
        assert isinstance(result, str)
        assert "?" in result  # Hidden cells


class TestResetGameTool:
    """Tests for the reset_game tool."""

    def setup_method(self) -> None:
        """Reset game state before each test."""
        reset_game_instance()

    def test_reset_game_returns_message(self) -> None:
        """Test that reset_game returns confirmation."""
        result = reset_game()
        assert "reset" in result.lower()

    def test_reset_game_clears_progress(self) -> None:
        """Test that reset_game clears game progress."""
        move("down")
        move("down")
        reset_game()
        state = get_game_state()
        assert state["player"]["moves_made"] == 0
        assert state["player"]["keys_collected"] == 0
