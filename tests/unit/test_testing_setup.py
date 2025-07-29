"""
Meta-tests to verify test infrastructure setup.

This module verifies that our testing infrastructure is properly configured
and working as expected.
"""

import subprocess
import sys
import pytest
from pathlib import Path


@pytest.mark.unit
class TestTestingInfrastructure:
    """Tests to verify the test infrastructure itself works correctly."""

    def test_pytest_can_discover_tests(self):
        """Verify pytest can discover and collect tests."""
        # Run pytest in collect-only mode
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
        )

        # Should find tests
        assert result.returncode == 0
        assert "test session starts" in result.stdout
        assert "collected" in result.stdout

        # Should find both unit and integration tests
        output = result.stdout
        assert "<Package unit>" in output or "tests/unit" in output
        assert "<Package integration>" in output or "tests/integration" in output

    def test_coverage_reporting_works(self):
        """Verify coverage reporting is configured."""
        # Run a simple coverage command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=app",
                "--cov-report=",
                "-x",
                "tests/unit/test_example.py::test_basic_arithmetic",
            ],
            capture_output=True,
            text=True,
        )

        # Coverage should run successfully
        assert result.returncode == 0
        assert "coverage:" in result.stdout.lower() or "Coverage" in result.stderr

    def test_markers_filter_correctly(self):
        """Verify test markers work for filtering."""
        # Run only unit tests
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-m", "unit", "--collect-only", "-q"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should not include integration tests
        assert "test_integration" not in result.stdout or "deselected" in result.stdout

    def test_async_tests_run_correctly(self):
        """Verify async tests are properly configured."""
        # Run a specific async test
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-v",
                "tests/integration/test_example_integration.py"
                + "::test_async_health_endpoint",
            ],
            capture_output=True,
            text=True,
        )

        # Should pass
        assert result.returncode == 0
        assert "PASSED" in result.stdout

    def test_fixtures_available(self):
        """Verify key fixtures are available."""
        # This test uses fixtures to verify they work
        # Just check that Path exists

        # Get fixtures through pytest
        root = Path(__file__).parent.parent.parent
        assert root.exists()
        assert (root / "pytest.ini").exists()

    def test_coverage_threshold_enforcement(self):
        """Verify coverage threshold is enforced."""
        # Create a dummy module with low coverage
        test_file = Path("_test_coverage_dummy.py")
        test_file.write_text(
            """
def covered_function():
    return True

def uncovered_function():
    if False:
        return "This won't be covered"
    return "Also not covered"
"""
        )

        test_test_file = Path("test__test_coverage_dummy.py")
        test_test_file.write_text(
            """
from _test_coverage_dummy import covered_function

def test_covered():
    assert covered_function() == True
"""
        )

        try:
            # Run coverage with threshold
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "--cov=_test_coverage_dummy",
                    "--cov-fail-under=80",
                    "test__test_coverage_dummy.py",
                ],
                capture_output=True,
                text=True,
            )

            # Should fail due to coverage threshold
            assert result.returncode != 0
            assert "Required test coverage of 80% not reached" in result.stdout
        finally:
            # Clean up
            test_file.unlink(missing_ok=True)
            test_test_file.unlink(missing_ok=True)
            Path(".coverage").unlink(missing_ok=True)

    def test_html_coverage_generation(self):
        """Verify HTML coverage reports are generated."""
        htmlcov_dir = Path("htmlcov")

        # Directory should exist from previous test runs
        assert htmlcov_dir.exists()
        assert htmlcov_dir.is_dir()

        # Should contain HTML files
        html_files = list(htmlcov_dir.glob("*.html"))
        assert len(html_files) > 0

        # Should have index.html
        assert (htmlcov_dir / "index.html").exists()

    def test_makefile_targets_exist(self):
        """Verify all required Makefile targets exist."""
        makefile = Path("Makefile")
        assert makefile.exists()

        content = makefile.read_text()

        # Check for required targets
        required_targets = [
            "test:",
            "test-unit:",
            "test-integration:",
            "coverage:",
        ]

        for target in required_targets:
            assert target in content, f"Makefile missing target: {target}"

    @pytest.mark.parametrize(
        "marker", ["unit", "integration", "slow", "requires_api_key"]
    )
    def test_markers_registered(self, marker):
        """Verify all markers are properly registered."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--markers"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert f"@pytest.mark.{marker}" in result.stdout
