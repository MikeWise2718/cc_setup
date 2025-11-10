# Install & Prime

## Read
.env.sample (if it exists, never read .env)

## Read and Execute
.claude/commands/prime.md

## Run
- Think through each of these steps to make sure you don't miss anything.
- Remove the existing git remote: `git remote remove origin`
- Initialize a new git repository: `git init`
- Install project dependencies (e.g., backend and frontend dependencies if applicable)
- (Optional) Run `./scripts/copy_dot_env.sh` if you need to copy environment files. Customize the script first.
- (Optional) Run `./scripts/reset_db.sh` if your project uses a database. Customize the script first.
- On a background process, run `./scripts/start.sh` with 'nohup' or a 'subshell' to start the application so you don't get stuck

## Report
- Output the work you've just done in a concise bullet point list.
- If `.env.sample` exists, instruct the user to create `.env` from it with their configuration values
- Check for any other environment file templates (`.env.sample`, `config.sample.json`, etc.) and inform the user
- Mention the application URL based on `scripts/start.sh` configuration
- Mention: 'To enable AI Developer Workflows with GitHub integration, update the remote repo URL and push to a new repository:
  ```
  git remote add origin <your-new-repo-url>
  git push -u origin main
  ```'
- (Optional) If image uploading features are used, mention setting up image hosting (Cloudflare, S3, etc.) per .env.sample