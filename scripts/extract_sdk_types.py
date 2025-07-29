#!/usr/bin/env python3
"""Extract Pydantic models from Ollama SDK for API compatibility.

This script clones the Ollama Python SDK from GitHub and extracts all Pydantic
model definitions to ensure our proxy maintains 100% compatibility with the
official Ollama API types.
"""

import argparse
import ast
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

import structlog
from git import Repo

logger = structlog.get_logger()

OLLAMA_SDK_REPO = "https://github.com/ollama/ollama-python.git"
OUTPUT_DIR = Path("references/ollama-types")
MODULES_TO_EXTRACT = ["_types", "_client"]  # The actual modules in ollama SDK


def main() -> None:
    """Main entry point for the SDK type extraction script."""
    parser = argparse.ArgumentParser(
        description="Extract Pydantic models from Ollama SDK"
    )
    parser.add_argument(
        "--repo-url",
        default=OLLAMA_SDK_REPO,
        help="Ollama SDK repository URL",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for extracted types",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to extract from (default: main)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-extraction even if output exists",
    )

    args = parser.parse_args()

    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger.info(
        "Starting Ollama SDK type extraction",
        repo_url=args.repo_url,
        output_dir=str(args.output_dir),
        branch=args.branch,
    )

    try:
        extract_types(
            repo_url=args.repo_url,
            output_dir=args.output_dir,
            branch=args.branch,
            force=args.force,
        )
        logger.info("Type extraction completed successfully")
    except Exception as e:
        logger.error("Type extraction failed", error=str(e))
        sys.exit(1)


def extract_types(
    repo_url: str,
    output_dir: Path,
    branch: str = "main",
    force: bool = False,
) -> None:
    """Extract Pydantic types from the Ollama SDK repository.

    Args:
        repo_url: URL of the Ollama SDK repository
        output_dir: Directory to save extracted types
        branch: Git branch to extract from
        force: Force re-extraction even if output exists
    """
    # Check if output already exists
    if output_dir.exists() and not force:
        logger.warning(
            "Output directory already exists, use --force to re-extract",
            output_dir=str(output_dir),
        )
        return

    # Create temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Clone repository
        logger.info("Cloning Ollama SDK repository", target_dir=temp_dir)
        clone_repository(repo_url, temp_path, branch)

        # Find and extract models
        sdk_path = temp_path / "ollama"
        if not sdk_path.exists():
            raise ValueError(f"Expected 'ollama' directory not found in {temp_path}")

        # Extract models from each module
        extracted_models = {}
        for module_name in MODULES_TO_EXTRACT:
            module_path = sdk_path / f"{module_name}.py"
            if module_path.exists():
                logger.info(f"Extracting models from {module_name}")
                models = extract_models_from_file(module_path)
                extracted_models[module_name] = models
            else:
                logger.warning(f"Module {module_name} not found at {module_path}")

        # Write extracted models to output directory
        write_extracted_models(extracted_models, output_dir)


def clone_repository(repo_url: str, target_dir: Path, branch: str) -> Repo:
    """Clone the Ollama SDK repository.

    Args:
        repo_url: URL of the repository
        target_dir: Directory to clone into
        branch: Branch to checkout

    Returns:
        The cloned repository object
    """
    try:
        repo = Repo.clone_from(
            repo_url,
            target_dir,
            branch=branch,
            depth=1,  # Shallow clone for efficiency
        )
        logger.info(
            "Repository cloned successfully",
            branch=branch,
            commit=repo.head.commit.hexsha[:8],
        )
        return repo
    except Exception as e:
        logger.error("Failed to clone repository", error=str(e))
        raise


def extract_models_from_file(file_path: Path) -> Dict[str, str]:
    """Extract Pydantic model definitions from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        Dictionary mapping model names to their source code
    """
    models = {}

    with open(file_path, "r") as f:
        source = f.read()

    # Parse the AST
    tree = ast.parse(source)

    # Extract imports we need
    imports = extract_imports(tree)

    # Find all class definitions that inherit from BaseModel
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if is_pydantic_model(node):
                model_name = node.name
                model_source = ast.get_source_segment(source, node)
                if model_source:
                    models[model_name] = model_source
                    logger.debug(f"Extracted model: {model_name}")

    # Add imports to the beginning of the extracted content
    if models:
        import_statements = "\n".join(imports)
        return {
            "__imports__": import_statements,
            **models,
        }

    return models


def extract_imports(tree: ast.Module) -> List[str]:
    """Extract import statements from an AST.

    Args:
        tree: The parsed AST module

    Returns:
        List of import statement strings
    """
    imports = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.ImportFrom):
            imports.append(ast.unparse(node))

    return imports


def is_pydantic_model(node: ast.ClassDef) -> bool:
    """Check if a class definition is a Pydantic model.

    Args:
        node: The class definition AST node

    Returns:
        True if the class inherits from BaseModel or SubscriptableBaseModel
    """
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in [
            "BaseModel",
            "SubscriptableBaseModel",
        ]:
            return True
        elif isinstance(base, ast.Attribute) and base.attr in [
            "BaseModel",
            "SubscriptableBaseModel",
        ]:
            return True
    return False


def write_extracted_models(
    models: Dict[str, Dict[str, str]],
    output_dir: Path,
) -> None:
    """Write extracted models to the output directory.

    Args:
        models: Dictionary mapping module names to model definitions
        output_dir: Directory to write the models to
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_path = output_dir / "__init__.py"
    init_content = '"""Extracted Pydantic models from Ollama SDK."""\n'
    init_path.write_text(init_content)

    # Write each module
    for module_name, module_models in models.items():
        if not module_models:
            continue

        module_path = output_dir / f"{module_name}.py"

        # Build module content
        content_parts = []

        # Add module docstring
        content_parts.append(
            f'"""Pydantic models extracted from ollama._{module_name}."""\n'
        )

        # Add imports if present
        if "__imports__" in module_models:
            content_parts.append(module_models["__imports__"])
            content_parts.append("")

        # Add each model
        for model_name, model_source in module_models.items():
            if model_name != "__imports__":
                content_parts.append(model_source)
                content_parts.append("\n")

        # Write the module
        module_content = "\n".join(content_parts)
        module_path.write_text(module_content)
        logger.info(f"Wrote {module_name}.py with {len(module_models) - 1} models")

    # Validate that models can be imported
    validate_extracted_models(output_dir)


def validate_extracted_models(output_dir: Path) -> None:
    """Validate that extracted models can be imported.

    Args:
        output_dir: Directory containing the extracted models

    Raises:
        ImportError: If models cannot be imported
    """
    # Add output directory to Python path temporarily
    sys.path.insert(0, str(output_dir.parent))

    try:
        for module_name in MODULES_TO_EXTRACT:
            module_path = output_dir / f"{module_name}.py"
            if module_path.exists():
                try:
                    # Try to import the module
                    __import__(
                        f"{output_dir.name}.{module_name}",
                        fromlist=[module_name],
                    )
                    logger.info(f"Successfully validated {module_name} module")
                except ImportError as e:
                    logger.error(f"Failed to import {module_name}: {e}")
                    raise
    finally:
        # Remove from path
        sys.path.pop(0)


if __name__ == "__main__":
    main()
