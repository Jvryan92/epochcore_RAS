"""Base agent class with async support."""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path


class AsyncBaseAgent:
    """Base class for asynchronous AI agents."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent.

        Args:
            name: Agent name
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    async def run_async(self) -> Dict[str, Any]:
        """Run the agent asynchronously.

        Returns:
            Execution results
        """
        raise NotImplementedError("Async agents must implement run_async")

    async def validate_config_async(self) -> bool:
        """Validate agent configuration asynchronously.

        Returns:
            True if configuration is valid
        """
        return True

    async def get_project_root_async(self) -> Path:
        """Get the project root directory asynchronously.

        Returns:
            Path to project root
        """
        # Start from current directory and look for .git
        current = Path.cwd()
        while not (current / ".git").exists():
            if current.parent == current:
                raise RuntimeError("Not in a git repository")
            current = current.parent
        return current

    @classmethod
    def is_async(cls) -> bool:
        """Check if agent supports async operation.

        Returns:
            True if agent supports async
        """
        return True
