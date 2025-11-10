# Conditional Documentation Guide

This prompt helps you determine what documentation you should read based on the specific changes you need to make in the codebase. Review the conditions below and read the relevant documentation before proceeding with your task.

## Instructions
- Review the task you've been asked to perform
- Check each documentation path in the Conditional Documentation section
- For each path, evaluate if any of the listed conditions apply to your task
  - IMPORTANT: Only read the documentation if any one of the conditions match your task
- IMPORTANT: You don't want to excessively read documentation. Only read the documentation if it's relevant to your task.

## Conditional Documentation

- README.md
  - Conditions:
    - When operating on source code directories (e.g., src/**, lib/**, backend/**, frontend/**, etc.)
    - When first understanding the project structure
    - When you want to learn the commands to start or stop the application

- Project-specific style/config files
  - Conditions:
    - When you need to make changes to styling, configuration, or other project-specific files
  - Examples: src/styles/**, config/**, etc. (paths vary by project)

- .claude/commands/classify_adw.md
  - Conditions:
    - When adding or removing new `.claude/adws/adw_*.py` files

- .claude/adws/README.md
  - Conditions:
    - When you're operating in the `.claude/adws/` directory