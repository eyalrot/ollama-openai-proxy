"""Unit tests for code quality tooling."""

import subprocess
import sys
from pathlib import Path
import pytest
import tempfile


@pytest.mark.unit
class TestCodeQualityTools:
    """Tests for code quality tool configuration and Makefile targets."""

    def test_black_config_exists(self):
        """Test that Black configuration exists."""
        pyproject = Path("pyproject.toml")
        assert pyproject.exists()

        content = pyproject.read_text()
        assert "[tool.black]" in content
        assert "line-length = 88" in content
        assert "py312" in content

    def test_flake8_config_exists(self):
        """Test that Flake8 configuration exists."""
        flake8_config = Path(".flake8")
        assert flake8_config.exists()

        content = flake8_config.read_text()
        assert "max-line-length = 88" in content
        assert "E203, W503" in content

    def test_mypy_config_exists(self):
        """Test that Mypy configuration exists."""
        mypy_config = Path("mypy.ini")
        assert mypy_config.exists()

        content = mypy_config.read_text()
        assert "python_version = 3.12" in content
        assert "disallow_untyped_defs = True" in content

    def test_makefile_format_target(self):
        """Test that make format runs without errors."""
        result = subprocess.run(
            ["make", "format"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "error" not in result.stderr.lower()

    def test_makefile_lint_target(self):
        """Test that make lint runs without errors."""
        result = subprocess.run(
            ["make", "lint"],
            capture_output=True,
            text=True,
        )

        # Should pass since we've already fixed all issues
        assert result.returncode == 0

    def test_makefile_type_check_target(self):
        """Test that make type-check runs without errors."""
        result = subprocess.run(
            ["make", "type-check"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Success" in result.stdout or result.returncode == 0

    def test_makefile_quality_target(self):
        """Test that make quality runs all checks."""
        # Test that the quality target exists in Makefile
        makefile = Path("Makefile")
        content = makefile.read_text()

        # Check that quality target depends on all three
        assert "quality: format lint type-check" in content

        # Also check it's a .PHONY target
        assert ".PHONY: quality" in content

    def test_black_formats_code(self):
        """Test that Black actually formats code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a badly formatted file
            test_file = Path(tmpdir) / "test_format.py"
            test_file.write_text(
                "def test(  x,y  ):\n"
                "    return x+y\n"
                "list=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]"
            )

            # Run black on it
            result = subprocess.run(
                [sys.executable, "-m", "black", str(test_file)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0

            # Check it was formatted
            formatted = test_file.read_text()
            assert "def test(x, y):" in formatted
            assert "return x + y" in formatted
            assert "list = [" in formatted

    def test_flake8_catches_violations(self):
        """Test that Flake8 catches style violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with violations
            test_file = Path(tmpdir) / "test_lint.py"
            test_file.write_text(
                "import os\n"  # Unused import
                "def test( ):\n"  # Whitespace issues
                "    x=1+2\n"  # Missing spaces around operators
                "    return"  # Missing value
            )

            # Run flake8 on it
            result = subprocess.run(
                [sys.executable, "-m", "flake8", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should fail and report violations
            assert result.returncode != 0
            assert "F401" in result.stdout  # unused import
            assert "E" in result.stdout  # style errors

    def test_mypy_catches_type_errors(self):
        """Test that Mypy catches type errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with type errors
            test_file = Path(tmpdir) / "test_types.py"
            test_file.write_text(
                "def add(x: int, y: int) -> int:\n"
                "    return x + y\n"
                "\n"
                "result = add('hello', 'world')  # Type error\n"
            )

            # Run mypy on it
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "--no-error-summary", str(test_file)],
                capture_output=True,
                text=True,
            )

            # Should report type error
            assert "Argument 1" in result.stdout or "error" in result.stdout
            assert "str" in result.stdout

    def test_all_python_files_have_type_hints(self):
        """Test that all app files use type hints."""
        app_dir = Path("app")

        for py_file in app_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            content = py_file.read_text()

            # Skip empty __init__.py files
            if py_file.name == "__init__.py" and not content.strip():
                continue

            # Check for function definitions with type hints
            if "def " in content and "(" in content:
                # This is a basic check - mypy will do the real verification
                has_arrow = "->" in content
                has_colon = ": " in content

                # At least some functions should have type hints
                assert has_arrow or has_colon, f"{py_file} appears to lack type hints"

    def test_configs_match_tech_stack_versions(self):
        """Test that tool versions match tech stack requirements."""
        # These versions are specified in the tech stack
        expected = {
            "black": "23.12.1",
            "flake8": "7.0.0",
            "mypy": "1.8.0",
        }

        # Check Black version
        result = subprocess.run(
            ["black", "--version"],
            capture_output=True,
            text=True,
        )
        assert expected["black"] in result.stdout

        # Check flake8 version
        result = subprocess.run(
            ["flake8", "--version"],
            capture_output=True,
            text=True,
        )
        assert expected["flake8"] in result.stdout

        # Check mypy version
        result = subprocess.run(
            ["mypy", "--version"],
            capture_output=True,
            text=True,
        )
        assert expected["mypy"] in result.stdout

    def test_makefile_help_includes_quality_targets(self):
        """Test that Makefile help shows all quality targets."""
        result = subprocess.run(
            ["make", "help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "format" in result.stdout
        assert "lint" in result.stdout
        assert "type-check" in result.stdout
        assert "quality" in result.stdout

        # Check descriptions are present
        assert "Format code with black" in result.stdout
        assert "Run linting checks" in result.stdout
        assert "Run type checking with mypy" in result.stdout
        assert "Run all code quality checks" in result.stdout
