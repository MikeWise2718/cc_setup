# Claude Code Project Instructions

Project-specific guidelines for working on cc_setup.

## Commit Guidelines

### Version Bumps
When adding new features or making significant changes to the codebase:
- **Always bump the version in `pyproject.toml`** as part of the same commit
- Don't create separate commits for version bumps
- Follow semantic versioning: MAJOR.MINOR.PATCH
  - PATCH: Bug fixes, minor improvements
  - MINOR: New features (like execution logging)
  - MAJOR: Breaking changes

### What to Track
All files in these directories **must** be tracked in git:
- `store/` - Artifacts that cc_setup deploys
- `specs/` - Implementation specs and historical context

### Commit Process
1. Review `git status` to see ALL modified files before committing
2. Include related changes (like version bumps) in the same commit
3. Use `git add` with specific paths, but verify nothing is missed

## Directory Structure

- `store/basic/` - Basic mode artifacts (single worktree)
- `store/iso/` - Isolated worktree mode artifacts
- `store/iso_v1/` - Extended isolated mode with enhanced ADW modules
- `store/git/` - Language-specific .gitignore templates
- `specs/` - Implementation plans and handoff documents
- `temp/` - Gitignored directory for testing
