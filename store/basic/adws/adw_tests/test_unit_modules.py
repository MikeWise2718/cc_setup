#!/usr/bin/env python3
"""
Unit tests for ADW modules.

These tests verify the functionality of ADW core modules without requiring
external services (Claude API, GitHub, R2, etc.).

Run with: uv run pytest store/basic/adws/adw_tests/test_unit_modules.py -v
Run with coverage: uv run pytest store/basic/adws/adw_tests/test_unit_modules.py -v --cov=store/basic/adws/adw_modules --cov-report=term-missing
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adw_modules.data_types import (
    ADWStateData,
    AgentPromptRequest,
    AgentPromptResponse,
    ClaudeCodeResultMessage,
    E2ETestResult,
    GitHubComment,
    GitHubIssue,
    GitHubIssueListItem,
    GitHubLabel,
    GitHubMilestone,
    GitHubUser,
    ReviewIssue,
    ReviewResult,
    TestResult,
)
from adw_modules.utils import make_adw_id, parse_json, get_safe_subprocess_env, check_claude_auth_available
from adw_modules.state import ADWState


class TestDataTypes:
    """Tests for data_types.py Pydantic models."""

    def test_github_user_basic(self):
        """Test GitHubUser model creation."""
        user = GitHubUser(login="testuser")
        assert user.login == "testuser"
        assert user.is_bot is False
        assert user.name is None

    def test_github_user_with_all_fields(self):
        """Test GitHubUser with all fields populated."""
        user = GitHubUser(
            id="12345",
            login="botuser",
            name="Bot User",
            is_bot=True,
        )
        assert user.id == "12345"
        assert user.login == "botuser"
        assert user.name == "Bot User"
        assert user.is_bot is True

    def test_github_label(self):
        """Test GitHubLabel model."""
        label = GitHubLabel(
            id="1",
            name="bug",
            color="ff0000",
            description="Bug report",
        )
        assert label.name == "bug"
        assert label.color == "ff0000"

    def test_github_milestone(self):
        """Test GitHubMilestone model."""
        milestone = GitHubMilestone(
            id="1",
            number=1,
            title="v1.0",
            description="First release",
            state="open",
        )
        assert milestone.title == "v1.0"
        assert milestone.state == "open"

    def test_github_comment(self):
        """Test GitHubComment model with alias fields."""
        comment = GitHubComment(
            id="1",
            author=GitHubUser(login="commenter"),
            body="This is a comment",
            createdAt=datetime(2024, 1, 1, 12, 0, 0),
        )
        assert comment.body == "This is a comment"
        assert comment.created_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_github_issue_list_item(self):
        """Test GitHubIssueListItem model."""
        issue = GitHubIssueListItem(
            number=123,
            title="Test Issue",
            body="Issue body",
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 2),
        )
        assert issue.number == 123
        assert issue.title == "Test Issue"
        assert issue.labels == []

    def test_github_issue_full(self):
        """Test full GitHubIssue model."""
        issue = GitHubIssue(
            number=456,
            title="Full Issue",
            body="Full body",
            state="open",
            author=GitHubUser(login="author"),
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 2),
            url="https://github.com/test/repo/issues/456",
        )
        assert issue.number == 456
        assert issue.state == "open"
        assert issue.author.login == "author"
        assert issue.assignees == []
        assert issue.comments == []

    def test_agent_prompt_request(self):
        """Test AgentPromptRequest model."""
        request = AgentPromptRequest(
            prompt="Test prompt",
            adw_id="abc12345",
            agent_name="planner",
            model="sonnet",
            output_file="output.jsonl",
        )
        assert request.prompt == "Test prompt"
        assert request.model == "sonnet"
        assert request.dangerously_skip_permissions is False

    def test_agent_prompt_request_opus(self):
        """Test AgentPromptRequest with opus model."""
        request = AgentPromptRequest(
            prompt="Complex task",
            adw_id="def67890",
            model="opus",
            output_file="output.jsonl",
        )
        assert request.model == "opus"

    def test_agent_prompt_response(self):
        """Test AgentPromptResponse model."""
        response = AgentPromptResponse(
            output="Task completed",
            success=True,
            session_id="session-123",
        )
        assert response.success is True
        assert response.session_id == "session-123"

    def test_claude_code_result_message(self):
        """Test ClaudeCodeResultMessage model."""
        result = ClaudeCodeResultMessage(
            type="result",
            subtype="success",
            is_error=False,
            duration_ms=5000,
            duration_api_ms=4500,
            num_turns=3,
            result="Success",
            session_id="sess-abc",
            total_cost_usd=0.05,
        )
        assert result.is_error is False
        assert result.num_turns == 3
        assert result.total_cost_usd == 0.05

    def test_test_result(self):
        """Test TestResult model."""
        result = TestResult(
            test_name="test_login",
            passed=True,
            execution_command="pytest test_auth.py::test_login",
            test_purpose="Verify user login works",
        )
        assert result.passed is True
        assert result.error is None

    def test_test_result_failed(self):
        """Test TestResult model for failed test."""
        result = TestResult(
            test_name="test_broken",
            passed=False,
            execution_command="pytest test_broken.py",
            test_purpose="Test that fails",
            error="AssertionError: expected True",
        )
        assert result.passed is False
        assert "AssertionError" in result.error

    def test_e2e_test_result_passed(self):
        """Test E2ETestResult with passed status."""
        result = E2ETestResult(
            test_name="login_flow",
            status="passed",
            test_path="e2e/login.spec.ts",
            screenshots=["screenshot1.png"],
        )
        assert result.passed is True
        assert result.status == "passed"

    def test_e2e_test_result_failed(self):
        """Test E2ETestResult with failed status."""
        result = E2ETestResult(
            test_name="checkout_flow",
            status="failed",
            test_path="e2e/checkout.spec.ts",
            error="Element not found",
        )
        assert result.passed is False
        assert result.error == "Element not found"

    def test_adw_state_data(self):
        """Test ADWStateData model."""
        state = ADWStateData(
            adw_id="test1234",
            issue_number="123",
            branch_name="feat-123-test",
            plan_file="plan.md",
            issue_class="/feature",
        )
        assert state.adw_id == "test1234"
        assert state.issue_class == "/feature"

    def test_adw_state_data_minimal(self):
        """Test ADWStateData with minimal fields."""
        state = ADWStateData(adw_id="minimal1")
        assert state.adw_id == "minimal1"
        assert state.issue_number is None
        assert state.branch_name is None

    def test_review_issue(self):
        """Test ReviewIssue model."""
        issue = ReviewIssue(
            review_issue_number=1,
            screenshot_path="review_img/error.png",
            issue_description="Button misaligned",
            issue_resolution="Adjust CSS margin",
            issue_severity="tech_debt",
        )
        assert issue.issue_severity == "tech_debt"
        assert issue.screenshot_url is None

    def test_review_result(self):
        """Test ReviewResult model."""
        result = ReviewResult(
            success=True,
            review_summary="Implementation matches spec. All features working.",
            review_issues=[],
            screenshots=["ui.png"],
        )
        assert result.success is True
        assert len(result.review_issues) == 0


class TestUtils:
    """Tests for utils.py functions."""

    def test_make_adw_id_format(self):
        """Test that make_adw_id returns 8 character string."""
        adw_id = make_adw_id()
        assert len(adw_id) == 8
        assert isinstance(adw_id, str)

    def test_make_adw_id_unique(self):
        """Test that make_adw_id generates unique IDs."""
        ids = [make_adw_id() for _ in range(100)]
        assert len(set(ids)) == 100  # All unique

    def test_parse_json_raw(self):
        """Test parse_json with raw JSON."""
        result = parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_json_array(self):
        """Test parse_json with JSON array."""
        result = parse_json('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_parse_json_markdown_code_block(self):
        """Test parse_json with markdown code block."""
        text = """
Here is the result:
```json
{"status": "success", "count": 42}
```
That's all.
"""
        result = parse_json(text)
        assert result == {"status": "success", "count": 42}

    def test_parse_json_plain_code_block(self):
        """Test parse_json with plain code block (no json label)."""
        text = """
```
{"data": [1, 2, 3]}
```
"""
        result = parse_json(text)
        assert result == {"data": [1, 2, 3]}

    def test_parse_json_embedded_in_text(self):
        """Test parse_json extracts JSON from surrounding text."""
        text = 'Some text before {"result": true} some text after'
        result = parse_json(text)
        assert result == {"result": True}

    def test_parse_json_invalid(self):
        """Test parse_json raises ValueError for invalid JSON."""
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            parse_json("not valid json at all")

    def test_parse_json_with_pydantic_model(self):
        """Test parse_json with Pydantic model target type."""
        json_text = '{"test_name": "test1", "passed": true, "execution_command": "pytest", "test_purpose": "testing"}'
        result = parse_json(json_text, TestResult)
        assert isinstance(result, TestResult)
        assert result.test_name == "test1"
        assert result.passed is True

    def test_get_safe_subprocess_env(self):
        """Test get_safe_subprocess_env returns filtered env."""
        with patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key",
            "PATH": "/usr/bin",
            "HOME": "/home/test",
            "SECRET_KEY": "should-not-appear",
        }, clear=True):
            env = get_safe_subprocess_env()
            assert "ANTHROPIC_API_KEY" in env
            assert "PATH" in env
            assert "HOME" in env
            assert "SECRET_KEY" not in env
            assert env["PYTHONUNBUFFERED"] == "1"

    def test_check_claude_auth_with_api_key(self):
        """Test check_claude_auth_available detects API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test-key-12345"}):
            available, mode = check_claude_auth_available()
            assert available is True
            assert mode == "api_key"

    def test_check_claude_auth_without_api_key(self):
        """Test check_claude_auth_available without API key."""
        env = os.environ.copy()
        env.pop("ANTHROPIC_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            available, mode = check_claude_auth_available()
            # Result depends on whether Claude CLI is installed
            assert mode in ["api_key", "oauth", "none"]

    def test_check_claude_auth_empty_api_key(self):
        """Test check_claude_auth_available with empty API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            available, mode = check_claude_auth_available()
            # With empty key, should try OAuth or return none
            assert mode in ["oauth", "none"]


class TestADWState:
    """Tests for state.py ADWState class."""

    def test_init_requires_adw_id(self):
        """Test ADWState requires adw_id."""
        with pytest.raises(ValueError, match="adw_id is required"):
            ADWState("")

    def test_init_with_adw_id(self):
        """Test ADWState initialization."""
        state = ADWState("test1234")
        assert state.adw_id == "test1234"
        assert state.data["adw_id"] == "test1234"

    def test_update(self):
        """Test ADWState.update method."""
        state = ADWState("test1234")
        state.update(issue_number="123", branch_name="feat-123")
        assert state.data["issue_number"] == "123"
        assert state.data["branch_name"] == "feat-123"

    def test_update_ignores_unknown_fields(self):
        """Test ADWState.update ignores non-core fields."""
        state = ADWState("test1234")
        state.update(issue_number="123", unknown_field="ignored")
        assert state.data["issue_number"] == "123"
        assert "unknown_field" not in state.data

    def test_get(self):
        """Test ADWState.get method."""
        state = ADWState("test1234")
        state.update(issue_number="456")
        assert state.get("issue_number") == "456"
        assert state.get("missing_key") is None
        assert state.get("missing_key", "default") == "default"

    def test_save_and_load(self):
        """Test saving and loading state from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch the project root detection
            with patch.object(ADWState, 'get_state_path') as mock_path:
                state_file = Path(tmpdir) / "agents" / "test1234" / "adw_state.json"
                mock_path.return_value = str(state_file)

                # Create and save state
                state = ADWState("test1234")
                state.update(issue_number="789", branch_name="fix-789")
                state.save()

                # Verify file exists
                assert state_file.exists()

                # Verify content
                with open(state_file) as f:
                    data = json.load(f)
                assert data["adw_id"] == "test1234"
                assert data["issue_number"] == "789"

    def test_to_stdout(self, capsys):
        """Test ADWState.to_stdout outputs JSON."""
        state = ADWState("test1234")
        state.update(issue_number="123", issue_class="/bug")
        state.to_stdout()

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["adw_id"] == "test1234"
        assert output["issue_number"] == "123"
        assert output["issue_class"] == "/bug"

    def test_from_stdin_no_input(self):
        """Test ADWState.from_stdin returns None when stdin is tty."""
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.return_value = True
            result = ADWState.from_stdin()
            assert result is None

    def test_from_stdin_with_input(self):
        """Test ADWState.from_stdin parses piped JSON."""
        input_data = json.dumps({
            "adw_id": "piped123",
            "issue_number": "999",
        })
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.return_value = False
            mock_stdin.read.return_value = input_data

            result = ADWState.from_stdin()
            assert result is not None
            assert result.adw_id == "piped123"
            assert result.get("issue_number") == "999"

    def test_from_stdin_empty_input(self):
        """Test ADWState.from_stdin handles empty input."""
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.return_value = False
            mock_stdin.read.return_value = ""

            result = ADWState.from_stdin()
            assert result is None

    def test_from_stdin_invalid_json(self):
        """Test ADWState.from_stdin handles invalid JSON."""
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.return_value = False
            mock_stdin.read.return_value = "not json"

            result = ADWState.from_stdin()
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
