#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Plan Build Test Iso - Compositional workflow for isolated planning, building, and testing

Usage: uv run adw_plan_build_test_iso.py <issue-number> [adw-id] [--skip-e2e]

This script runs:
1. adw_plan_iso.py - Planning phase (isolated)
2. adw_build_iso.py - Implementation phase (isolated)
3. adw_test_iso.py - Testing phase (isolated)

The scripts are chained together via persistent state (adw_state.json).
"""

import subprocess
import sys
import os

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adw_modules.workflow_ops import ensure_adw_id
from adw_modules.github import make_issue_comment
from adw_modules.utils import get_local_timestamp


def main():
    """Main entry point."""
    # Check for --skip-e2e flag
    skip_e2e = "--skip-e2e" in sys.argv
    if skip_e2e:
        sys.argv.remove("--skip-e2e")

    if len(sys.argv) < 2:
        print("Usage: uv run adw_plan_build_test_iso.py <issue-number> [adw-id] [--skip-e2e]")
        print("\nThis runs the isolated plan, build, and test workflow:")
        print("  1. Plan (isolated)")
        print("  2. Build (isolated)")
        print("  3. Test (isolated)")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Ensure ADW ID exists with initialized state
    adw_id = ensure_adw_id(issue_number, adw_id)
    print(f"Using ADW ID: {adw_id}")

    # Post workflow start notification
    try:
        timestamp = get_local_timestamp()
        make_issue_comment(
            issue_number,
            f"🤖 **ADW Plan+Build+Test Workflow Started**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n"
            f"**Workflow:** Plan → Build → Test\n"
            f"**E2E Tests:** {'Skipped' if skip_e2e else 'Included'}\n\n"
            f"📋 Phase 1/3: Planning..."
        )
    except Exception as e:
        print(f"WARNING: Failed to post start comment to issue: {e}")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ===== PLAN PHASE =====
    plan_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_plan_iso.py"),
        issue_number,
        adw_id,
    ]
    print(f"\n=== ISOLATED PLAN PHASE ===")
    print(f"Running: {' '.join(plan_cmd)}")
    plan = subprocess.run(plan_cmd)

    if plan.returncode != 0:
        timestamp = get_local_timestamp()
        error_msg = (
            f"❌ **ADW Plan Phase Failed**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n"
            f"**Phase:** 1/3 - Planning\n"
            f"**Return Code:** {plan.returncode}\n\n"
            f"**Error:** The planning phase failed to complete successfully.\n\n"
            f"**Logs:** Check `agents/{adw_id}/planner/raw_output.jsonl` for details.\n\n"
            f"**Next Steps:**\n"
            f"- Review the error logs\n"
            f"- Check if the issue description is clear\n"
            f"- Verify API keys and credentials\n"
            f"- Manually retry: `cd trees/{adw_id} && uv run --extra adws python adws/adw_plan_iso.py {issue_number} {adw_id}`"
        )
        print(error_msg)
        try:
            make_issue_comment(issue_number, error_msg)
        except Exception as e:
            print(f"ERROR: Failed to post error comment to issue: {e}")
        sys.exit(1)

    # Post plan success
    try:
        timestamp = get_local_timestamp()
        make_issue_comment(
            issue_number,
            f"✅ **Plan Phase Completed**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n\n"
            f"🔨 Phase 2/3: Building implementation..."
        )
    except Exception as e:
        print(f"WARNING: Failed to post plan success comment to issue: {e}")

    # ===== BUILD PHASE =====
    build_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_build_iso.py"),
        issue_number,
        adw_id,
    ]
    print(f"\n=== ISOLATED BUILD PHASE ===")
    print(f"Running: {' '.join(build_cmd)}")
    build = subprocess.run(build_cmd)

    if build.returncode != 0:
        timestamp = get_local_timestamp()
        error_msg = (
            f"❌ **ADW Build Phase Failed**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n"
            f"**Phase:** 2/3 - Implementation\n"
            f"**Return Code:** {build.returncode}\n\n"
            f"**Error:** The implementation phase failed to complete successfully.\n\n"
            f"**Status:** Plan was created successfully, but implementation failed.\n\n"
            f"**Logs:** Check `agents/{adw_id}/implementor/raw_output.jsonl` for details.\n\n"
            f"**Next Steps:**\n"
            f"- Review the implementation logs\n"
            f"- Check the plan file for issues: `specs/issue-{issue_number}-adw-{adw_id}-*.md`\n"
            f"- Manually retry: `cd trees/{adw_id} && uv run --extra adws python adws/adw_build_iso.py {issue_number} {adw_id}`"
        )
        print(error_msg)
        try:
            make_issue_comment(issue_number, error_msg)
        except Exception as e:
            print(f"ERROR: Failed to post error comment to issue: {e}")
        sys.exit(1)

    # Post build success
    try:
        timestamp = get_local_timestamp()
        make_issue_comment(
            issue_number,
            f"✅ **Build Phase Completed**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n\n"
            f"🧪 Phase 3/3: Running tests..."
        )
    except Exception as e:
        print(f"WARNING: Failed to post build success comment to issue: {e}")

    # ===== TEST PHASE =====
    test_cmd = [
        "uv",
        "run",
        os.path.join(script_dir, "adw_test_iso.py"),
        issue_number,
        adw_id,
    ]
    if skip_e2e:
        test_cmd.append("--skip-e2e")

    print(f"\n=== ISOLATED TEST PHASE ===")
    print(f"Running: {' '.join(test_cmd)}")
    test = subprocess.run(test_cmd)

    if test.returncode != 0:
        timestamp = get_local_timestamp()
        error_msg = (
            f"❌ **ADW Test Phase Failed**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n"
            f"**Phase:** 3/3 - Testing\n"
            f"**Return Code:** {test.returncode}\n\n"
            f"**Error:** The testing phase failed - tests did not pass.\n\n"
            f"**Status:**\n"
            f"- ✅ Plan created successfully\n"
            f"- ✅ Implementation completed\n"
            f"- ❌ Tests failed\n\n"
            f"**Logs:** Check `agents/{adw_id}/tester/raw_output.jsonl` for details.\n\n"
            f"**Next Steps:**\n"
            f"- Review the test failure logs\n"
            f"- Check which tests failed and why\n"
            f"- The implementation may need fixes\n"
            f"- Manually retry: `cd trees/{adw_id} && uv run --extra adws python adws/adw_test_iso.py {issue_number} {adw_id}`"
        )
        print(error_msg)
        try:
            make_issue_comment(issue_number, error_msg)
        except Exception as e:
            print(f"ERROR: Failed to post error comment to issue: {e}")
        sys.exit(1)

    # Post final success notification
    try:
        timestamp = get_local_timestamp()
        make_issue_comment(
            issue_number,
            f"✅ **ADW Plan+Build+Test Workflow Completed**\n\n"
            f"**Timestamp:** {timestamp}\n"
            f"**ADW ID:** `{adw_id}`\n"
            f"**Status:** All phases completed successfully! 🎉\n\n"
            f"**Phases Completed:**\n"
            f"- ✅ Planning\n"
            f"- ✅ Implementation\n"
            f"- ✅ Testing (All tests passed!)\n\n"
            f"**Next Steps:**\n"
            f"- Review the changes in the worktree: `trees/{adw_id}/`\n"
            f"- Check the pull request for the implementation\n"
            f"- The fix has been validated with tests and is ready for review!"
        )
    except Exception as e:
        print(f"WARNING: Failed to post success comment to issue: {e}")

    print(f"\n=== ISOLATED WORKFLOW COMPLETED ===")
    print(f"ADW ID: {adw_id}")
    print(f"All phases completed successfully!")


if __name__ == "__main__":
    main()
