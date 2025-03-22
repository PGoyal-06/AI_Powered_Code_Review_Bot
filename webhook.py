import os
import base64
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REVIEWS_LOG = []

client = OpenAI(api_key=OPENAI_API_KEY)  # Updated OpenAI client

@app.route("/webhook", methods=["POST"])
def github_webhook():
    event = request.headers.get("X-GitHub-Event", "")
    payload = request.get_json()

    print(f"[Webhook] Event received: {event}")
    print(f"[Webhook] Payload:\n{payload}")

    if event == "pull_request":
        handle_pull_request_event(payload)
    elif event == "push":
        handle_push_event(payload)
    elif event == "issue_comment":
        handle_issue_comment_event(payload)

    return "", 200

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", reviews=REVIEWS_LOG)

def handle_pull_request_event(payload):
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    pr_number = pr.get("number")
    repo = payload.get("repository", {})
    repo_full_name = repo.get("full_name")
    branch = pr.get("head", {}).get("ref")

    if action in ["opened", "reopened", "synchronize"]:
        print(f"[Webhook] PR #{pr_number} opened in repo: {repo_full_name}")

        files = get_modified_files(repo_full_name, pr_number)
        all_reviews = []
        label = "needs improvement"

        for file_path in files:
            if file_path.endswith(".py"):
                code = fetch_file_content(repo_full_name, file_path, branch)
                if code:
                    review = analyze_code_with_ai(code, file_path)
                    all_reviews.append((file_path, review))
                    if "no major issues" in review.lower():
                        label = "approved"

        full_comment = ""
        for file, review in all_reviews:
            full_comment += f"### Review for `{file}`:\n{review}\n\n"
            REVIEWS_LOG.append({"file": file, "review": review})

        post_comment(repo_full_name, pr_number, full_comment)
        add_label(repo_full_name, pr_number, label)

        if label == "approved":
            auto_merge_pr(repo_full_name, pr_number)

def handle_push_event(payload):
    repo = payload.get("repository", {}).get("full_name")
    pusher = payload.get("pusher", {}).get("name")
    commits = payload.get("commits", [])
    print(f"[Push Event] {pusher} pushed {len(commits)} commit(s) to {repo}.")

def handle_issue_comment_event(payload):
    action = payload.get("action")
    comment = payload.get("comment", {}).get("body")
    issue = payload.get("issue", {})
    repo = payload.get("repository", {}).get("full_name")

    if action == "created" and "review please" in comment.lower():
        issue_number = issue.get("number")
        commenter = payload.get("comment", {}).get("user", {}).get("login")
        print(f"[Issue Comment Event] @{commenter} requested a review on issue #{issue_number} in {repo}.")

def get_modified_files(repo_full_name, pr_number):
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {GITHUB_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [file["filename"] for file in response.json()]
    print(f"[Error] Could not fetch modified files: {response.text}")
    return []

def fetch_file_content(repo_full_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json().get("content", "")
        encoding = response.json().get("encoding", "base64")
        if encoding == "base64":
            return base64.b64decode(content).decode("utf-8")
    print(f"[Error] Could not fetch content for {file_path}")
    return None

def analyze_code_with_ai(code, filename):
    prompt = f"""
You are an AI code reviewer. Provide clear, file-specific feedback for the given Python file.
Focus on security, performance, code quality, and documentation.

File: {filename}

Code:
{code}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional code reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Error] AI review failed: {e}")
        return "[AI Review Failed]"

def post_comment(repo_full_name, pr_number, comment):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("[Webhook] Comment posted successfully.")
    else:
        print(f"[Error] Failed to post comment: {response.text}")

def add_label(repo_full_name, pr_number, label):
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/labels"
    headers = {
        "Authorization": f"token {GITHUB_API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"labels": [label]}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"[Webhook] Label '{label}' added to PR #{pr_number}.")
    else:
        print(f"[Error] Failed to add label: {response.text}")

def auto_merge_pr(repo_full_name, pr_number):
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/merge"
    headers = {
        "Authorization": f"token {GITHUB_API_KEY}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "commit_title": "Auto-merged by AI Review Bot",
        "merge_method": "squash"
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"[Webhook] PR #{pr_number} auto-merged successfully.")
    else:
        print(f"[Error] Auto-merge failed: {response.text}")

if __name__ == "__main__":
    app.run(debug=True)
