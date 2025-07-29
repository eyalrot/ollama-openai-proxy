"""
Example unit tests demonstrating test infrastructure.

This module shows proper unit testing patterns including:
- Use of test markers
- Fixture usage
- AAA pattern (Arrange, Act, Assert)
- Type hints
"""

import pytest
from pathlib import Path
from typing import Dict


@pytest.mark.unit
def test_basic_arithmetic():
    """Test basic arithmetic operations."""
    # Arrange
    a = 5
    b = 3

    # Act
    result = a + b

    # Assert
    assert result == 8


@pytest.mark.unit
def test_string_operations():
    """Test string manipulation."""
    # Arrange
    text = "hello world"

    # Act
    capitalized = text.capitalize()
    upper = text.upper()

    # Assert
    assert capitalized == "Hello world"
    assert upper == "HELLO WORLD"


@pytest.mark.unit
def test_project_root_fixture(project_root: Path):
    """Test that project root fixture works correctly."""
    # Assert
    assert project_root.exists()
    assert project_root.is_dir()
    assert (project_root / "pytest.ini").exists()


@pytest.mark.unit
def test_temp_test_data_fixture(temp_test_data: Dict[str, Path]):
    """Test that temporary test data fixture creates files."""
    # Assert
    assert temp_test_data["data_dir"].exists()
    assert temp_test_data["json_file"].exists()
    assert temp_test_data["text_file"].exists()

    # Verify content
    json_content = temp_test_data["json_file"].read_text()
    assert "test" in json_content

    text_content = temp_test_data["text_file"].read_text()
    assert text_content == "Test content"


@pytest.mark.unit
def test_override_settings_fixture(override_settings):
    """Test that settings override fixture works."""
    import os

    # Arrange
    test_key = "TEST_ENV_VAR"
    test_value = "test_value_123"

    # Act
    override_settings(TEST_ENV_VAR=test_value)

    # Assert
    assert os.environ.get(test_key) == test_value


@pytest.mark.unit
class TestExampleClass:
    """Example test class demonstrating class-based testing."""

    def test_list_operations(self):
        """Test list operations."""
        # Arrange
        items = [1, 2, 3]

        # Act
        items.append(4)
        items.extend([5, 6])

        # Assert
        assert len(items) == 6
        assert items[-1] == 6

    def test_dict_operations(self):
        """Test dictionary operations."""
        # Arrange
        data = {"name": "test", "value": 42}

        # Act
        data["status"] = "active"
        value = data.get("value", 0)

        # Assert
        assert len(data) == 3
        assert value == 42
        assert data["status"] == "active"


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_value,expected",
    [
        (0, "zero"),
        (1, "positive"),
        (-1, "negative"),
    ],
)
def test_parametrized_example(input_value: int, expected: str):
    """Example of parametrized testing."""
    # Act
    if input_value == 0:
        result = "zero"
    elif input_value > 0:
        result = "positive"
    else:
        result = "negative"

    # Assert
    assert result == expected
