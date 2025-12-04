"""Unit tests for the Character class."""

import pytest
from src.character import Character
from src.maze import Position


class TestCharacter:
    """Tests for the Character class."""

    def test_character_creation_default(self) -> None:
        """Test creating a character with default position."""
        character = Character()

        assert character.position == Position(1, 1)
        assert character.keys_collected == 0
        assert character.moves_made == 0
        assert Position(1, 1) in character.visited_positions

    def test_character_creation_custom_position(self) -> None:
        """Test creating a character with custom position."""
        character = Character(position=Position(5, 5))

        assert character.position == Position(5, 5)
        assert Position(5, 5) in character.visited_positions

    def test_move_up(self) -> None:
        """Test calculating position after moving up."""
        character = Character(position=Position(5, 5))
        new_pos = character.move("up")

        assert new_pos == Position(5, 4)
        # Position should not change (just calculation)
        assert character.position == Position(5, 5)

    def test_move_down(self) -> None:
        """Test calculating position after moving down."""
        character = Character(position=Position(5, 5))
        new_pos = character.move("down")

        assert new_pos == Position(5, 6)

    def test_move_right(self) -> None:
        """Test calculating position after moving right."""
        character = Character(position=Position(5, 5))
        new_pos = character.move("right")

        assert new_pos == Position(6, 5)

    def test_move_left(self) -> None:
        """Test calculating position after moving left."""
        character = Character(position=Position(5, 5))
        new_pos = character.move("left")

        assert new_pos == Position(4, 5)

    def test_move_case_insensitive(self) -> None:
        """Test that move direction is case insensitive."""
        character = Character(position=Position(5, 5))

        assert character.move("UP") == Position(5, 4)
        assert character.move("Up") == Position(5, 4)
        assert character.move("uP") == Position(5, 4)

    def test_move_invalid_direction(self) -> None:
        """Test that invalid direction raises error."""
        character = Character()

        with pytest.raises(ValueError, match="Invalid direction"):
            character.move("north")

        with pytest.raises(ValueError, match="Invalid direction"):
            character.move("diagonal")

    def test_set_position(self) -> None:
        """Test setting character position."""
        character = Character(position=Position(1, 1))
        new_pos = Position(3, 3)

        character.set_position(new_pos)

        assert character.position == new_pos
        assert character.moves_made == 1
        assert new_pos in character.visited_positions

    def test_set_position_tracks_visits(self) -> None:
        """Test that set_position tracks all visited positions."""
        character = Character(position=Position(1, 1))

        character.set_position(Position(2, 1))
        character.set_position(Position(3, 1))
        character.set_position(Position(3, 2))

        assert len(character.visited_positions) == 4
        assert Position(1, 1) in character.visited_positions
        assert Position(2, 1) in character.visited_positions
        assert Position(3, 1) in character.visited_positions
        assert Position(3, 2) in character.visited_positions

    def test_collect_key(self) -> None:
        """Test collecting a key."""
        character = Character()

        assert character.keys_collected == 0
        character.collect_key()
        assert character.keys_collected == 1
        character.collect_key()
        assert character.keys_collected == 2

    def test_reset(self) -> None:
        """Test resetting character state."""
        character = Character(position=Position(1, 1))
        character.set_position(Position(5, 5))
        character.collect_key()
        character.collect_key()

        start_pos = Position(2, 2)
        character.reset(start_pos)

        assert character.position == start_pos
        assert character.keys_collected == 0
        assert character.moves_made == 0
        assert character.visited_positions == {start_pos}

    def test_get_stats(self) -> None:
        """Test getting character statistics."""
        character = Character(position=Position(1, 1))
        character.set_position(Position(2, 1))
        character.set_position(Position(3, 1))
        character.collect_key()

        stats = character.get_stats()

        assert stats["keys_collected"] == 1
        assert stats["moves_made"] == 2
        assert stats["positions_visited"] == 3

    def test_character_repr(self) -> None:
        """Test character string representation."""
        character = Character(position=Position(5, 5))
        character.collect_key()
        character.set_position(Position(5, 6))

        repr_str = repr(character)

        assert "Character" in repr_str
        assert "position" in repr_str
        assert "keys=1" in repr_str
        assert "moves=1" in repr_str
