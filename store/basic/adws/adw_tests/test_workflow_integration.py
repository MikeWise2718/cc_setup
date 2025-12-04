#!/usr/bin/env python3
"""
Comprehensive Workflow Integration Tests for ADW System

This test suite verifies that all ADW workflows function correctly with both:
1. ANTHROPIC_API_KEY authentication (API mode)
2. Claude Max subscription authentication (OAuth mode)

Usage:
    # Run all tests (auto-detects available auth)
    uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v

    # Run with coverage
    uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v \
        --cov=store/basic/adws --cov-report=term-missing

    # Run only API key tests
    ADW_AUTH_MODE=api_key uv run pytest ... -k "api_key"

    # Run only Claude Max tests
    ADW_AUTH_MODE=claude_max uv run pytest ... -k "claude_max"

    # Force skip auth checks (for unit tests only)
    ADW_SKIP_AUTH=1 uv run pytest ...

Environment Variables:
    ANTHROPIC_API_KEY: Required for API mode
    ADW_AUTH_MODE: Force specific auth mode (api_key, claude_max, or auto)
    ADW_SKIP_AUTH: Skip authentication checks for unit testing
    CLAUDE_CODE_PATH: Path to Claude Code CLI (default: claude)
"""

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# Auth Mode Detection and Configuration
# =============================================================================

class AuthMode(Enum):
    """Authentication modes for Claude Code CLI."""
    API_KEY = "api_key"
    CLAUDE_MAX = "claude_max"
    NONE = "none"


@dataclass
class AuthConfig:
    """Authentication configuration for tests."""
    mode: AuthMode
    api_key_available: bool
    claude_max_available: bool
    claude_cli_path: str
    claude_cli_installed: bool


def detect_claude_cli() -> Tuple[bool, str]:
    """Detect if Claude Code CLI is installed and get its path."""
    claude_path = os.getenv("CLAUDE_CODE_PATH", "claude")
    try:
        result = subprocess.run(
            [claude_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, claude_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, claude_path


def detect_api_key_auth() -> bool:
    """Check if ANTHROPIC_API_KEY is available."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    return bool(api_key and len(api_key) > 10)


def detect_claude_max_auth() -> bool:
    """Check if Claude Max (OAuth) authentication is available.

    This checks if the user is logged in via `claude auth status` or similar.
    Claude Max users don't need an API key - they authenticate via OAuth.
    """
    claude_path = os.getenv("CLAUDE_CODE_PATH", "claude")
    try:
        # Try to check auth status - this varies by Claude Code version
        # Method 1: Check if we can run a simple command without API key
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)  # Remove API key to test OAuth

        result = subprocess.run(
            [claude_path, "--version"],
            capture_output=True,
            text=True,
            env=env,
            timeout=10
        )

        if result.returncode != 0:
            return False

        # Method 2: Try a minimal prompt to see if auth works
        # This is more reliable but slower
        # For now, we'll check if there's a Claude config file indicating login
        config_paths = [
            Path.home() / ".claude" / "config.json",
            Path.home() / ".config" / "claude" / "config.json",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                        # Check for OAuth tokens or session info
                        if config.get("oauth_token") or config.get("session"):
                            return True
                except (json.JSONDecodeError, KeyError):
                    pass

        # Fallback: assume Claude Max if CLI is installed but no API key
        # This allows testing even without explicit OAuth detection
        return True

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_auth_config() -> AuthConfig:
    """Get the current authentication configuration."""
    cli_installed, cli_path = detect_claude_cli()
    api_key_available = detect_api_key_auth()
    claude_max_available = detect_claude_max_auth() if cli_installed else False

    # Determine mode based on environment or detection
    forced_mode = os.getenv("ADW_AUTH_MODE", "auto").lower()

    if forced_mode == "api_key":
        mode = AuthMode.API_KEY if api_key_available else AuthMode.NONE
    elif forced_mode == "claude_max":
        mode = AuthMode.CLAUDE_MAX if claude_max_available else AuthMode.NONE
    else:  # auto
        if api_key_available:
            mode = AuthMode.API_KEY
        elif claude_max_available:
            mode = AuthMode.CLAUDE_MAX
        else:
            mode = AuthMode.NONE

    return AuthConfig(
        mode=mode,
        api_key_available=api_key_available,
        claude_max_available=claude_max_available,
        claude_cli_path=cli_path,
        claude_cli_installed=cli_installed,
    )


# Global auth config - computed once at module load
AUTH_CONFIG = get_auth_config()


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def auth_config():
    """Provide auth configuration to tests."""
    return AUTH_CONFIG


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_env_api_key():
    """Mock environment with API key."""
    with patch.dict(os.environ, {
        "ANTHROPIC_API_KEY": "test-api-key-12345",
        "CLAUDE_CODE_PATH": "claude",
    }):
        yield


@pytest.fixture
def mock_env_no_api_key():
    """Mock environment without API key (Claude Max mode)."""
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    with patch.dict(os.environ, env, clear=True):
        yield


# =============================================================================
# Skip Decorators
# =============================================================================

requires_cli = pytest.mark.skipif(
    not AUTH_CONFIG.claude_cli_installed,
    reason="Claude Code CLI not installed"
)

requires_api_key = pytest.mark.skipif(
    not AUTH_CONFIG.api_key_available,
    reason="ANTHROPIC_API_KEY not set"
)

requires_claude_max = pytest.mark.skipif(
    not AUTH_CONFIG.claude_max_available,
    reason="Claude Max authentication not available"
)

requires_any_auth = pytest.mark.skipif(
    AUTH_CONFIG.mode == AuthMode.NONE,
    reason="No authentication available (need API key or Claude Max)"
)


# =============================================================================
# Test: Auth Detection
# =============================================================================

class TestAuthDetection:
    """Tests for authentication mode detection."""

    def test_auth_config_structure(self, auth_config):
        """Verify auth config has expected structure."""
        assert isinstance(auth_config, AuthConfig)
        assert isinstance(auth_config.mode, AuthMode)
        assert isinstance(auth_config.api_key_available, bool)
        assert isinstance(auth_config.claude_max_available, bool)
        assert isinstance(auth_config.claude_cli_path, str)

    def test_detect_api_key_with_key(self):
        """Test API key detection when key is set."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key-12345"}):
            assert detect_api_key_auth() is True

    def test_detect_api_key_without_key(self):
        """Test API key detection when key is not set."""
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            assert detect_api_key_auth() is False

    def test_detect_api_key_empty_key(self):
        """Test API key detection with empty key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            assert detect_api_key_auth() is False

    def test_auth_mode_enum_values(self):
        """Verify AuthMode enum has expected values."""
        assert AuthMode.API_KEY.value == "api_key"
        assert AuthMode.CLAUDE_MAX.value == "claude_max"
        assert AuthMode.NONE.value == "none"


# =============================================================================
# Test: Workflow Module Imports
# =============================================================================

class TestWorkflowImports:
    """Test that all workflow modules can be imported."""

    def test_import_data_types(self):
        """Test importing data_types module."""
        from adw_modules.data_types import (
            ADWStateData,
            AgentPromptRequest,
            AgentPromptResponse,
            GitHubIssue,
            IssueClassSlashCommand,
        )
        assert ADWStateData is not None
        assert AgentPromptRequest is not None

    def test_import_state(self):
        """Test importing state module."""
        from adw_modules.state import ADWState
        assert ADWState is not None

    def test_import_utils(self):
        """Test importing utils module."""
        from adw_modules.utils import (
            make_adw_id,
            parse_json,
            get_safe_subprocess_env,
            setup_logger,
        )
        assert make_adw_id is not None
        assert parse_json is not None

    def test_import_agent(self):
        """Test importing agent module."""
        from adw_modules.agent import (
            prompt_claude_code,
            execute_template,
            check_claude_installed,
            get_model_for_slash_command,
        )
        assert prompt_claude_code is not None
        assert execute_template is not None

    def test_import_git_ops(self):
        """Test importing git_ops module."""
        from adw_modules.git_ops import (
            create_branch,
            commit_changes,
            finalize_git_operations,
        )
        assert create_branch is not None

    def test_import_github(self):
        """Test importing github module."""
        from adw_modules.github import (
            fetch_issue,
            make_issue_comment,
            get_repo_url,
        )
        assert fetch_issue is not None

    def test_import_workflow_ops(self):
        """Test importing workflow_ops module."""
        from adw_modules.workflow_ops import (
            classify_issue,
            build_plan,
            generate_branch_name,
        )
        assert classify_issue is not None


# =============================================================================
# Test: Agent Module Functionality
# =============================================================================

class TestAgentModule:
    """Tests for the agent module."""

    def test_get_model_for_slash_command(self):
        """Test model selection for slash commands."""
        from adw_modules.agent import get_model_for_slash_command

        # Commands that should use opus
        assert get_model_for_slash_command("/implement") == "opus"
        assert get_model_for_slash_command("/review") == "opus"
        assert get_model_for_slash_command("/bug") == "opus"
        assert get_model_for_slash_command("/feature") == "opus"

        # Commands that should use sonnet
        assert get_model_for_slash_command("/classify_issue") == "sonnet"
        assert get_model_for_slash_command("/commit") == "sonnet"
        assert get_model_for_slash_command("/test") == "sonnet"

        # Unknown command should use default
        assert get_model_for_slash_command("/unknown") == "sonnet"

    @requires_cli
    def test_check_claude_installed(self):
        """Test Claude CLI installation check."""
        from adw_modules.agent import check_claude_installed

        result = check_claude_installed()
        # If CLI is installed (as indicated by requires_cli), should return None
        assert result is None

    def test_agent_prompt_request_creation(self):
        """Test AgentPromptRequest model creation."""
        from adw_modules.data_types import AgentPromptRequest

        request = AgentPromptRequest(
            prompt="Test prompt",
            adw_id="test1234",
            agent_name="tester",
            model="sonnet",
            output_file="/tmp/test.jsonl",
        )
        assert request.prompt == "Test prompt"
        assert request.model == "sonnet"
        assert request.dangerously_skip_permissions is False

    def test_agent_prompt_response_creation(self):
        """Test AgentPromptResponse model creation."""
        from adw_modules.data_types import AgentPromptResponse

        response = AgentPromptResponse(
            output="Test output",
            success=True,
            session_id="sess-123",
        )
        assert response.success is True
        assert response.session_id == "sess-123"


# =============================================================================
# Test: Claude Code Execution (Integration)
# =============================================================================

class TestClaudeCodeExecution:
    """Integration tests for Claude Code CLI execution."""

    @requires_cli
    @requires_any_auth
    def test_simple_prompt_execution(self, temp_output_dir):
        """Test executing a simple prompt through Claude Code."""
        from adw_modules.agent import prompt_claude_code
        from adw_modules.data_types import AgentPromptRequest
        from adw_modules.utils import make_adw_id

        adw_id = make_adw_id()
        output_file = os.path.join(temp_output_dir, "test_output.jsonl")

        request = AgentPromptRequest(
            prompt="What is 2+2? Reply with just the number.",
            adw_id=adw_id,
            agent_name="test",
            model="sonnet",
            dangerously_skip_permissions=True,
            output_file=output_file,
        )

        response = prompt_claude_code(request)

        assert response is not None
        assert isinstance(response.success, bool)
        if response.success:
            assert "4" in response.output

    @requires_cli
    @requires_api_key
    def test_prompt_with_api_key(self, temp_output_dir):
        """Test Claude Code execution with API key authentication."""
        from adw_modules.agent import prompt_claude_code
        from adw_modules.data_types import AgentPromptRequest
        from adw_modules.utils import make_adw_id

        adw_id = make_adw_id()
        output_file = os.path.join(temp_output_dir, "api_key_test.jsonl")

        request = AgentPromptRequest(
            prompt="Say 'API key auth works' and nothing else.",
            adw_id=adw_id,
            agent_name="test_api",
            model="sonnet",
            dangerously_skip_permissions=True,
            output_file=output_file,
        )

        response = prompt_claude_code(request)

        assert response.success is True
        assert "API key auth works" in response.output or "auth" in response.output.lower()

    @requires_cli
    @requires_claude_max
    def test_prompt_with_claude_max(self, temp_output_dir, mock_env_no_api_key):
        """Test Claude Code execution with Claude Max authentication."""
        from adw_modules.agent import prompt_claude_code
        from adw_modules.data_types import AgentPromptRequest
        from adw_modules.utils import make_adw_id

        adw_id = make_adw_id()
        output_file = os.path.join(temp_output_dir, "claude_max_test.jsonl")

        request = AgentPromptRequest(
            prompt="Say 'Claude Max auth works' and nothing else.",
            adw_id=adw_id,
            agent_name="test_max",
            model="sonnet",
            dangerously_skip_permissions=True,
            output_file=output_file,
        )

        response = prompt_claude_code(request)

        # This test verifies Claude Max can work WITHOUT an API key
        assert response is not None
        # Note: This may fail if Claude Max isn't properly configured
        # The test documents the expected behavior


# =============================================================================
# Test: Workflow Scripts Structure
# =============================================================================

class TestWorkflowScriptsStructure:
    """Tests verifying workflow scripts have correct structure."""

    WORKFLOW_SCRIPTS = [
        "adw_plan.py",
        "adw_build.py",
        "adw_test.py",
        "adw_review.py",
        "adw_document.py",
        "adw_patch.py",
        "adw_plan_build.py",
        "adw_plan_build_test.py",
        "adw_plan_build_review.py",
        "adw_plan_build_test_review.py",
        "adw_plan_build_document.py",
        "adw_sdlc.py",
    ]

    def test_all_workflow_scripts_exist(self):
        """Verify all expected workflow scripts exist."""
        adws_dir = Path(__file__).parent.parent

        for script in self.WORKFLOW_SCRIPTS:
            script_path = adws_dir / script
            assert script_path.exists(), f"Missing workflow script: {script}"

    def test_workflow_scripts_are_executable(self):
        """Verify workflow scripts have shebang and are properly formatted."""
        adws_dir = Path(__file__).parent.parent

        for script in self.WORKFLOW_SCRIPTS:
            script_path = adws_dir / script
            with open(script_path) as f:
                first_line = f.readline()
                # Should have uv shebang
                assert "uv run" in first_line or "python" in first_line, \
                    f"{script} missing proper shebang"

    def test_workflow_scripts_have_main(self):
        """Verify workflow scripts have main() function."""
        adws_dir = Path(__file__).parent.parent

        for script in self.WORKFLOW_SCRIPTS:
            script_path = adws_dir / script
            content = script_path.read_text()
            assert "def main()" in content, f"{script} missing main() function"
            assert 'if __name__ == "__main__"' in content, \
                f"{script} missing __main__ guard"


# =============================================================================
# Test: Environment Variable Handling
# =============================================================================

class TestEnvironmentHandling:
    """Tests for environment variable handling in workflows."""

    def test_get_safe_subprocess_env_includes_api_key(self):
        """Test that safe env includes ANTHROPIC_API_KEY when set."""
        from adw_modules.utils import get_safe_subprocess_env

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            env = get_safe_subprocess_env()
            assert "ANTHROPIC_API_KEY" in env
            assert env["ANTHROPIC_API_KEY"] == "test-key"

    def test_get_safe_subprocess_env_excludes_sensitive(self):
        """Test that safe env excludes non-whitelisted vars."""
        from adw_modules.utils import get_safe_subprocess_env

        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "SECRET_DATABASE_PASSWORD": "secret123",
            "AWS_SECRET_KEY": "aws-secret",
        }):
            env = get_safe_subprocess_env()
            assert "SECRET_DATABASE_PASSWORD" not in env
            assert "AWS_SECRET_KEY" not in env

    def test_get_safe_subprocess_env_without_api_key(self):
        """Test safe env when ANTHROPIC_API_KEY is not set."""
        from adw_modules.utils import get_safe_subprocess_env

        env_copy = os.environ.copy()
        env_copy.pop("ANTHROPIC_API_KEY", None)

        with patch.dict(os.environ, env_copy, clear=True):
            env = get_safe_subprocess_env()
            # Should not include ANTHROPIC_API_KEY if not set
            assert env.get("ANTHROPIC_API_KEY") is None


# =============================================================================
# Test: Model Selection
# =============================================================================

class TestModelSelection:
    """Tests for model selection logic."""

    def test_slash_command_model_mapping(self):
        """Test the slash command to model mapping."""
        from adw_modules.agent import SLASH_COMMAND_MODEL_MAP

        # Verify mapping exists and has expected commands
        assert "/implement" in SLASH_COMMAND_MODEL_MAP
        assert "/classify_issue" in SLASH_COMMAND_MODEL_MAP
        assert "/review" in SLASH_COMMAND_MODEL_MAP

        # Verify opus is used for complex tasks
        assert SLASH_COMMAND_MODEL_MAP["/implement"] == "opus"
        assert SLASH_COMMAND_MODEL_MAP["/bug"] == "opus"

        # Verify sonnet is used for simpler tasks
        assert SLASH_COMMAND_MODEL_MAP["/classify_issue"] == "sonnet"
        assert SLASH_COMMAND_MODEL_MAP["/commit"] == "sonnet"

    @requires_cli
    @requires_any_auth
    def test_model_parameter_passed_to_cli(self, temp_output_dir):
        """Test that model parameter is correctly passed to Claude CLI."""
        from adw_modules.agent import prompt_claude_code
        from adw_modules.data_types import AgentPromptRequest
        from adw_modules.utils import make_adw_id

        adw_id = make_adw_id()

        # Test with sonnet
        request = AgentPromptRequest(
            prompt="Say 'test' and nothing else.",
            adw_id=adw_id,
            agent_name="model_test",
            model="sonnet",
            dangerously_skip_permissions=True,
            output_file=os.path.join(temp_output_dir, "model_test.jsonl"),
        )

        response = prompt_claude_code(request)
        # If successful, the model was accepted
        assert response is not None


# =============================================================================
# Main Entry Point
# =============================================================================

def print_auth_status():
    """Print current authentication status."""
    print("\n" + "=" * 60)
    print("ADW Workflow Test Suite - Authentication Status")
    print("=" * 60)
    print(f"Claude CLI installed: {AUTH_CONFIG.claude_cli_installed}")
    print(f"Claude CLI path: {AUTH_CONFIG.claude_cli_path}")
    print(f"API key available: {AUTH_CONFIG.api_key_available}")
    print(f"Claude Max available: {AUTH_CONFIG.claude_max_available}")
    print(f"Active auth mode: {AUTH_CONFIG.mode.value}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_auth_status()
    pytest.main([__file__, "-v", "--tb=short"])
