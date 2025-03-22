import os
import github3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")

def authenticate_github():
    """Authenticate with GitHub API using a Personal Access Token (PAT)."""
    gh = github3.login(token=GITHUB_API_KEY)
    if gh is None:
        print("Authentication failed. Check your GitHub API key.")
        return None
    return gh

def get_pr_files(repo_owner, repo_name, pr_number):
    """Fetch modified files and their content from a PR."""
    gh = authenticate_github()
    if gh is None:
        return []

    repo = gh.repository(repo_owner, repo_name)
    pr = repo.pull_request(pr_number)

    modified_files = []
    for file in pr.files():
        modified_files.append({
            "filename": file.filename,
            "changes": file.patch  # The code diff
        })

    return modified_files

if __name__ == "__main__":
    repo_owner = "PGoyal-06"
    repo_name = "A_repo_name"
    pr_number = 1  # Change this to an actual PR number
    files = get_pr_files(repo_owner, repo_name, pr_number)

    for file in files:
        print(f"File: {file['filename']}")
        print(file['changes'])
