"""Unit tests for the SDK type extraction script."""

import ast
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scripts.extract_sdk_types import (
    extract_imports,
    extract_models_from_file,
    is_pydantic_model,
    validate_extracted_models,
    write_extracted_models,
)


class TestASTHelpers:
    """Test AST parsing helper functions."""

    def test_is_pydantic_model_basemodel(self):
        """Test detecting BaseModel inheritance."""
        code = """
class MyModel(BaseModel):
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert is_pydantic_model(class_node) is True

    def test_is_pydantic_model_subscriptable(self):
        """Test detecting SubscriptableBaseModel inheritance."""
        code = """
class MyModel(SubscriptableBaseModel):
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert is_pydantic_model(class_node) is True

    def test_is_pydantic_model_not_pydantic(self):
        """Test non-Pydantic class detection."""
        code = """
class MyClass:
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        assert is_pydantic_model(class_node) is False

    def test_extract_imports(self):
        """Test import extraction from AST."""
        code = """
import os
from typing import Optional
from pydantic import BaseModel

class MyModel(BaseModel):
    pass
"""
        tree = ast.parse(code)
        imports = extract_imports(tree)

        assert len(imports) == 3
        assert "import os" in imports
        assert "from typing import Optional" in imports
        assert "from pydantic import BaseModel" in imports


class TestModelExtraction:
    """Test model extraction functionality."""

    def test_extract_models_from_file(self, tmp_path):
        """Test extracting models from a Python file."""
        code = """
from pydantic import BaseModel
from typing import Optional

class Options(BaseModel):
    numa: Optional[bool] = None

class Message(BaseModel):
    role: str
    content: Optional[str] = None

class NotAModel:
    pass
"""
        file_path = tmp_path / "test_models.py"
        file_path.write_text(code)

        models = extract_models_from_file(file_path)

        assert "__imports__" in models
        assert "Options" in models
        assert "Message" in models
        assert "NotAModel" not in models

        # Check imports are extracted
        imports = models["__imports__"]
        assert "from pydantic import BaseModel" in imports
        assert "from typing import Optional" in imports

    def test_extract_models_empty_file(self, tmp_path):
        """Test extracting from empty file."""
        file_path = tmp_path / "empty.py"
        file_path.write_text("")

        models = extract_models_from_file(file_path)
        assert models == {}

    def test_extract_models_no_pydantic(self, tmp_path):
        """Test extracting from file without Pydantic models."""
        code = """
class RegularClass:
    def __init__(self):
        pass
"""
        file_path = tmp_path / "no_models.py"
        file_path.write_text(code)

        models = extract_models_from_file(file_path)
        assert models == {}


class TestFileWriting:
    """Test file writing functionality."""

    def test_write_extracted_models(self, tmp_path):
        """Test writing models to output directory."""
        models = {
            "types": {
                "__imports__": (
                    "from pydantic import BaseModel\n" "from typing import Optional"
                ),
                "Options": (
                    "class Options(BaseModel):\n" "    numa: Optional[bool] = None"
                ),
                "Message": "class Message(BaseModel):\n    role: str",
            },
            "client": {},  # Empty module
        }

        output_dir = tmp_path / "output"
        write_extracted_models(models, output_dir)

        # Check __init__.py created
        assert (output_dir / "__init__.py").exists()

        # Check types.py created with content
        types_file = output_dir / "types.py"
        assert types_file.exists()
        content = types_file.read_text()
        assert "from pydantic import BaseModel" in content
        assert "class Options(BaseModel):" in content
        assert "class Message(BaseModel):" in content

        # Check empty module not created
        assert not (output_dir / "client.py").exists()

    def test_write_extracted_models_creates_dir(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        models = {"test": {"Model": "class Model(BaseModel): pass"}}
        output_dir = tmp_path / "new" / "nested" / "dir"

        write_extracted_models(models, output_dir)

        assert output_dir.exists()
        assert (output_dir / "__init__.py").exists()


class TestValidation:
    """Test model validation functionality."""

    @patch("scripts.extract_sdk_types.MODULES_TO_EXTRACT", ["test_module"])
    def test_validate_extracted_models_success(self, tmp_path):
        """Test successful validation of extracted models."""
        # Create a valid module
        output_dir = tmp_path / "ollama_types"
        output_dir.mkdir()

        module_file = output_dir / "test_module.py"
        module_file.write_text(
            """
from pydantic import BaseModel

class TestModel(BaseModel):
    field: str
"""
        )

        # Should not raise any exception
        validate_extracted_models(output_dir)

    @patch("scripts.extract_sdk_types.MODULES_TO_EXTRACT", ["bad_module"])
    def test_validate_extracted_models_import_error(self, tmp_path):
        """Test validation fails on import error."""
        output_dir = tmp_path / "ollama_types"
        output_dir.mkdir()

        module_file = output_dir / "bad_module.py"
        module_file.write_text("import nonexistent_module")

        with pytest.raises(ImportError):
            validate_extracted_models(output_dir)


class TestGitIntegration:
    """Test Git repository cloning."""

    @patch("scripts.extract_sdk_types.Repo")
    def test_clone_repository(self, mock_repo):
        """Test repository cloning."""
        from scripts.extract_sdk_types import clone_repository

        mock_repo_instance = Mock()
        mock_repo_instance.head.commit.hexsha = "abcd1234"
        mock_repo.clone_from.return_value = mock_repo_instance

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            repo = clone_repository("https://example.com/repo.git", temp_path, "main")

            mock_repo.clone_from.assert_called_once_with(
                "https://example.com/repo.git",
                temp_path,
                branch="main",
                depth=1,
            )
            assert repo == mock_repo_instance
