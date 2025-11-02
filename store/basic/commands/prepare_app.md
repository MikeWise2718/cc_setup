# Prepare Application

Setup the application for the review or test.

## Variables

PORT: 8000  # TODO: Customize this to match your application's main port (check scripts/start.sh)

## Setup

- (Optional) Reset the database by running `scripts/reset_db.sh` if your project uses a database
- IMPORTANT: Make sure the application is running on a background process using `nohup sh ./scripts/start.sh > /dev/null 2>&1 &` before executing the test steps. Use `./scripts/stop_apps.sh` to stop the application.
- Read `scripts/` and `README.md` for more information on how to start, stop and reset the application.

