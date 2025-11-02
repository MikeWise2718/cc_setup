# Application Validation Test Suite (TEMPLATE)

Execute comprehensive validation tests for your application, returning results in a standardized JSON format for automated processing.

**CUSTOMIZATION REQUIRED**: This file contains example tests for a Python/TypeScript stack. Replace with tests appropriate for your project's technology stack. See examples at the bottom of this file.

## Purpose

Proactively identify and fix issues in the application before they impact users or developers. By running this comprehensive test suite, you can:
- Detect syntax errors, type mismatches, and import failures
- Identify broken tests or security vulnerabilities
- Verify build processes and dependencies
- Ensure the application is in a healthy state

## Variables

TEST_COMMAND_TIMEOUT: 5 minutes

## Instructions

- Execute each test in the sequence provided below
- Capture the result (passed/failed) and any error messages
- IMPORTANT: Return ONLY the JSON array with test results
  - IMPORTANT: Do not include any additional text, explanations, or markdown formatting
  - We'll immediately run JSON.parse() on the output, so make sure it's valid JSON
- If a test passes, omit the error field
- If a test fails, include the error message in the error field
- Execute all tests even if some fail
- Error Handling:
  - If a command returns non-zero exit code, mark as failed and immediately stop processing tests
  - Capture stderr output for error field
  - Timeout commands after `TEST_COMMAND_TIMEOUT`
  - IMPORTANT: If a test fails, stop processing tests and return the results thus far
- Some tests may have dependencies (e.g., server must be stopped for port availability)
- Test execution order is important - dependencies should be validated first
- All file paths are relative to the project root
- Always run `pwd` and `cd` before each test to ensure you're operating in the correct directory for the given test

## Test Execution Sequence

**TODO**: Customize these tests for your project. The examples below are for a Python backend + TypeScript frontend stack. Replace with your own tests.

### Example Tests (Python Backend + TypeScript Frontend)

1. **Python Syntax Check**
   - Preparation Command: None
   - Command: `cd backend && python -m py_compile *.py`
   - test_name: "backend_syntax_check"
   - test_purpose: "Validates Python syntax by compiling source files to bytecode"

2. **Backend Code Quality Check**
   - Preparation Command: None
   - Command: `cd backend && ruff check . || pylint src/ || flake8 src/`
   - test_name: "backend_linting"
   - test_purpose: "Validates code quality, identifies unused imports, style violations, and potential bugs"

3. **All Backend Tests**
   - Preparation Command: None
   - Command: `cd backend && pytest tests/ -v --tb=short`
   - test_name: "backend_tests"
   - test_purpose: "Validates all backend functionality"

4. **TypeScript Type Check** (if applicable)
   - Preparation Command: None
   - Command: `cd frontend && tsc --noEmit`
   - test_name: "frontend_type_check"
   - test_purpose: "Validates TypeScript type correctness without generating output files"

5. **Frontend Build** (if applicable)
   - Preparation Command: None
   - Command: `cd frontend && npm run build`
   - test_name: "frontend_build"
   - test_purpose: "Validates the complete frontend build process"

## Report

- IMPORTANT: Return results exclusively as a JSON array based on the `Output Structure` section below.
- Sort the JSON array with failed tests (passed: false) at the top
- Include all tests in the output, both passed and failed
- The execution_command field should contain the exact command that can be run to reproduce the test
- This allows subsequent agents to quickly identify and resolve errors

### Output Structure

```json
[
  {
    "test_name": "string",
    "passed": boolean,
    "execution_command": "string",
    "test_purpose": "string",
    "error": "optional string"
  },
  ...
]
```

### Example Output

```json
[
  {
    "test_name": "frontend_build",
    "passed": false,
    "execution_command": "cd frontend && npm run build",
    "test_purpose": "Validates TypeScript compilation, module resolution, and production build process",
    "error": "TS2345: Argument of type 'string' is not assignable to parameter of type 'number'"
  },
  {
    "test_name": "backend_tests",
    "passed": true,
    "execution_command": "cd backend && pytest tests/ -v --tb=short",
    "test_purpose": "Validates all backend functionality"
  }
]
```

---

## Technology Stack Examples

### Node.js/JavaScript Project

```markdown
1. **JavaScript Syntax Check**
   - Command: `npx eslint src/`
   - test_name: "javascript_linting"
   - test_purpose: "Validates JavaScript syntax and style"

2. **Unit Tests**
   - Command: `npm test`
   - test_name: "unit_tests"
   - test_purpose: "Validates application functionality"

3. **Build**
   - Command: `npm run build`
   - test_name: "build"
   - test_purpose: "Validates build process"
```

### Go Project

```markdown
1. **Go Syntax Check**
   - Command: `go build ./...`
   - test_name: "go_build"
   - test_purpose: "Validates Go syntax and compilation"

2. **Go Tests**
   - Command: `go test ./... -v`
   - test_name: "go_tests"
   - test_purpose: "Validates application functionality"

3. **Go Linting**
   - Command: `golangci-lint run`
   - test_name: "go_linting"
   - test_purpose: "Validates code quality"
```

### Rust Project

```markdown
1. **Rust Check**
   - Command: `cargo check`
   - test_name: "rust_check"
   - test_purpose: "Validates Rust syntax without producing binaries"

2. **Rust Tests**
   - Command: `cargo test`
   - test_name: "rust_tests"
   - test_purpose: "Validates application functionality"

3. **Rust Clippy**
   - Command: `cargo clippy -- -D warnings`
   - test_name: "rust_linting"
   - test_purpose: "Validates code quality with Rust's linter"

4. **Rust Build**
   - Command: `cargo build --release`
   - test_name: "rust_build"
   - test_purpose: "Validates production build"
```

### C# / .NET Project

```markdown
1. **.NET Build**
   - Command: `dotnet build`
   - test_name: "dotnet_build"
   - test_purpose: "Validates C# compilation and builds"

2. **.NET Tests**
   - Command: `dotnet test`
   - test_name: "dotnet_tests"
   - test_purpose: "Validates application functionality"

3. **.NET Format Check**
   - Command: `dotnet format --verify-no-changes`
   - test_name: "dotnet_format"
   - test_purpose: "Validates code formatting"
```

### Java/Maven Project

```markdown
1. **Maven Compile**
   - Command: `mvn compile`
   - test_name: "maven_compile"
   - test_purpose: "Validates Java compilation"

2. **Maven Tests**
   - Command: `mvn test`
   - test_name: "maven_tests"
   - test_purpose: "Validates application functionality"

3. **Maven Package**
   - Command: `mvn package`
   - test_name: "maven_package"
   - test_purpose: "Validates packaging process"
```

### Multi-Language/Monorepo Example

```markdown
1. **Backend Tests (Python)**
   - Command: `cd services/api && pytest tests/`
   - test_name: "api_tests"
   - test_purpose: "Validates API service"

2. **Worker Tests (Go)**
   - Command: `cd services/worker && go test ./...`
   - test_name: "worker_tests"
   - test_purpose: "Validates worker service"

3. **Frontend Build (TypeScript)**
   - Command: `cd apps/web && npm run build`
   - test_name: "web_build"
   - test_purpose: "Validates web application build"
```
