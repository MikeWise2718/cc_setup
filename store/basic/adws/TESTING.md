# ADW Testing Guide

This document describes how to run tests with code coverage for the ADW (AI Developer Workflow) system.

## Test Suite Overview

The ADW test suite consists of:

1. **Unit Tests** (`adw_tests/test_unit_modules.py`) - Test core modules without external dependencies
2. **Workflow Integration Tests** (`adw_tests/test_workflow_integration.py`) - Test workflow structure and Claude Code execution
3. **Agent Tests** (`adw_tests/test_agents.py`) - Test Claude Code CLI integration with different models
4. **R2 Upload Tests** (`adw_tests/test_r2_uploader.py`) - Test Cloudflare R2 uploads (requires R2 credentials)
5. **E2E Tests** (`adw_tests/test_adw_test_e2e.py`) - End-to-end workflow tests

## Authentication Modes

The ADW system supports two authentication modes for Claude Code CLI:

### 1. API Key Mode (ANTHROPIC_API_KEY)
Traditional authentication using an Anthropic API key set via environment variable.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Claude Max Mode (OAuth)
Authentication via Claude Max subscription - no API key required. Users authenticate via `claude login` and the CLI uses stored OAuth tokens.

The test suite automatically detects which auth mode is available and runs appropriate tests.

## Prerequisites

From the cc_setup project root, ensure dev dependencies are installed:

```bash
uv sync
```

This installs:
- pytest>=8.0.0
- pytest-cov>=4.1.0
- coverage[toml]>=7.4.0
- pydantic>=2.0.0
- python-dotenv>=1.0.0

## Running Tests

### Quick Test Run (No Coverage)

```bash
# Run all unit tests
uv run pytest store/basic/adws/adw_tests/test_unit_modules.py -v

# Run a specific test class
uv run pytest store/basic/adws/adw_tests/test_unit_modules.py::TestDataTypes -v

# Run a specific test
uv run pytest store/basic/adws/adw_tests/test_unit_modules.py::TestUtils::test_make_adw_id_format -v
```

### Running Tests with Coverage

```bash
# Run all tests with coverage
uv run pytest store/basic/adws/adw_tests/test_unit_modules.py \
    store/basic/adws/adw_tests/test_workflow_integration.py -v \
    --cov=store/basic/adws/adw_modules \
    --cov-report=term-missing \
    --cov-report=html

# Run only unit tests (no external services)
uv run pytest store/basic/adws/adw_tests/test_unit_modules.py -v \
    --cov=store/basic/adws/adw_modules \
    --cov-report=term-missing

# View HTML report (generated in coverage_html/)
# Open coverage_html/index.html in a browser
```

### Running Tests with Specific Auth Mode

```bash
# Force API key mode (requires ANTHROPIC_API_KEY)
ADW_AUTH_MODE=api_key uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v

# Force Claude Max mode (no API key, uses OAuth)
ADW_AUTH_MODE=claude_max uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v

# Auto-detect (default) - uses whichever auth is available
uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v

# Run only API key-specific tests
uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v -k "api_key"

# Run only Claude Max-specific tests
uv run pytest store/basic/adws/adw_tests/test_workflow_integration.py -v -k "claude_max"
```

### Running All ADW Tests (Basic + ISO modes)

```bash
# Run all configured test paths
uv run pytest -v --cov=store/basic/adws/adw_modules --cov=store/iso/adws/adw_modules --cov-report=term-missing
```

### Running Integration Tests

**Note:** Integration tests require external services and credentials.

```bash
# Test Claude Code agents (requires ANTHROPIC_API_KEY)
cd store/basic/adws
uv run adw_tests/test_agents.py

# Test R2 uploads (requires Cloudflare R2 credentials)
uv run adw_tests/test_r2_uploader.py
```

## Coverage Configuration

Coverage settings are defined in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["store/basic/adws/adw_modules", "store/iso/adws/adw_modules"]
branch = true
omit = [
    "*/__pycache__/*",
    "*/adw_tests/*",
    "*/adw_triggers/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
show_missing = true
precision = 2

[tool.coverage.html]
directory = "coverage_html"
```

## Current Coverage Report

As of the latest test run (70 tests: 69 passed, 1 skipped):

| Module | Statements | Missing | Branch | Coverage |
|--------|------------|---------|--------|----------|
| `__init__.py` | 0 | 0 | 0 | 100.00% |
| `data_types.py` | 119 | 0 | 0 | **100.00%** |
| `state.py` | 73 | 22 | 20 | **67.74%** |
| `utils.py` | 87 | 35 | 32 | **57.14%** |
| `agent.py` | 115 | 65 | 22 | **40.88%** |
| `git_ops.py` | 84 | 73 | 34 | 9.32%* |
| `github.py` | 109 | 93 | 16 | 12.80%* |
| `r2_uploader.py` | 64 | 64 | 14 | 0.00%* |
| `workflow_ops.py` | 269 | 236 | 100 | 8.94%* |
| **TOTAL** | 920 | 588 | 238 | **31.61%** |

*\*These modules require external services (GitHub API, R2) or full workflow execution.*

## Test Categories

### Unit Tests (test_unit_modules.py)

Tests that run without external dependencies (43 tests):

- **TestDataTypes** - Pydantic model validation and serialization
- **TestUtils** - Utility functions (`make_adw_id`, `parse_json`, `get_safe_subprocess_env`, `check_claude_auth_available`)
- **TestADWState** - State management class functionality

### Workflow Integration Tests (test_workflow_integration.py)

Tests for workflow structure and Claude Code execution (27 tests):

- **TestAuthDetection** - Authentication mode detection (API key vs Claude Max)
- **TestWorkflowImports** - Module import verification
- **TestAgentModule** - Agent module functionality
- **TestClaudeCodeExecution** - Claude Code CLI execution tests
- **TestWorkflowScriptsStructure** - Workflow script structure validation
- **TestEnvironmentHandling** - Environment variable handling
- **TestModelSelection** - Model selection logic

### Integration Tests

Tests requiring external services:

- **test_agents.py** - Claude Code CLI with opus/sonnet models
- **test_r2_uploader.py** - Cloudflare R2 file uploads
- **test_adw_test_e2e.py** - Full ADW workflow execution

## Adding New Tests

1. Create test functions in the appropriate test file
2. Follow naming convention: `test_<description>`
3. Use pytest fixtures for setup/teardown
4. Mock external dependencies when possible

Example:

```python
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = my_function(input_data)

    # Assert
    assert result == expected_output
```

## Troubleshooting

### ModuleNotFoundError

Ensure you're running from the cc_setup root directory and dependencies are installed:

```bash
cd /path/to/cc_setup
uv sync
```

### Import Errors

The test file adds the parent directory to `sys.path`. If imports fail, verify the directory structure:

```
store/basic/adws/
├── adw_modules/
│   ├── __init__.py
│   ├── data_types.py
│   ├── state.py
│   └── utils.py
└── adw_tests/
    ├── __init__.py
    └── test_unit_modules.py
```

### Coverage Not Tracking

Ensure the `--cov` path matches your source directory structure exactly.
