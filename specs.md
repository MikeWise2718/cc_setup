# cc_setup - a claude code setup program specification
This is a spec for program copies useful artificats into a claude code target project.

# Background
There are a set of repos in the subfolder d:\tac. These have many claude code artifcats in these repos, we are particular interested in:
  - Claude slash commands in .claude/commands
  - Claude hooks in .claude/hooks
  - Claude configuration in in .claude/setup.json
  - Scripts in /scripts
  - Agent Developer Workflow python scripts in /adws
Each repo has various versions of these.

There is a recommendation for a basic setup in `basic_template_recommendation.md` (basic mode), and an isolated worktree capable frecommdation in `worktree_template_recommendation.md` (iso or isolated mode).

# Program requirements.
We need a python script that will take a path to a target project as an input, and augment it with the scripts and other artifcats from those recommendations.
- It should have command line parameters using argparse
- It should have a paraemter specifying the target directory
- It should ahve a parameters specifying either `basic` or `iso` mode.
- It should by default run in non-execute mode where by it just looks to see if the destination folder has an appropirate structure and if existing assets would be overwritten, and warnings generated.
- It should have an execute mode where by it actually copies the artificats into the destiation, but not overwriting things
- There should be messages about what artificats would be added (non-execute mode) or are added (execute mode)
- It should have an overwrite assets flag whereby artificats are overwritten.
- It should have color-coded output using the "rich" library
- General messages green, OK messages green, Warnings yellow, Errors red.
- The python script should hve the name "cc_setup.py"
- This project should be run and managed using uv and have a standard python directory structures
- A log with all the calling parameters, decisions made, and actions taken (or would have been taken) being listed.
- There should be a readme with basic information and usage instructions
- there should be a help function that outputs what artificats are created in basic mode, and in iso mode.