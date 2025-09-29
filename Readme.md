# 🤖 AI-Powered Code Review Bot

An intelligent GitHub-integrated bot that automatically reviews pull requests using OpenAI's GPT model. It provides detailed feedback on Python code focusing on security, performance, documentation, and code quality. Perfect for developers looking to automate their code review workflow with AI.

---

## 🚀 Features

- ✅ Automatically reviews pull requests when opened, reopened, or updated
- 💬 Posts file-specific AI-generated comments to the pull request
- 🏷️ Adds labels like `approved` or `needs improvement` based on review results
- 🔀 Automatically merges PRs if they pass the review
- 🌐 Dashboard view of previous reviews
- 🔐 Uses GitHub and OpenAI APIs with secure token handling

---

## 🛠️ Tech Stack

- **Python**
- **Flask** – for the webhook server
- **OpenAI GPT-3.5** – for natural language code analysis
- **GitHub REST API** – for repo integration
- **HTML/CSS (Jinja2)** – for the dashboard

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

```
git clone https://github.com/yourusername/AI_Powered_Code_Review_Bot.git
cd AI_Powered_Code_Review_Bot

### 2. Create a virtual environment

python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

### 3. Install Dependencies


pip install -r requirements.txt

### 4. Create .env file
Create a .env file in the root directory with the following content:

GITHUB_API_KEY=your_github_personal_access_token
OPENAI_API_KEY=your_openai_api_key
```
Your GitHub token must have **repo** and **workflow** scopes.

## 🔗 Github Webhook Setup

1. Go to your GitHub repository → **Settings** → **Webhooks** → **Add webhook**

2. Set the following:

* **Payload URL**: http://your-domain.com/webhook or http://localhost:5000/webhook

* **Content type**: application/json

* **Events to trigger**:

    * ✅ Pull requests

    * ✅ Push

    * ✅ Issue comments

3. Save the webhook.

---

## 🌐 Endpoints

| Route  | Description |
| ------------- | ------------- |
| /webhook  | Receives GitHub webhook events  |
| /dashboard  | Displays all past code reviews  |

---

## 🧠 How It Works

1. GitHub triggers a webhook on PR open/sync/reopen.
2. The bot:
    * Fetches modified .py files
    * Sends the code to OpenAI for review
    * Posts review comments to the PR
    * Adds an approval or improvement label
    * Merges the PR if approved
3. Reviews are logged in-memory and visible via /dashboard.

---

## 💡 Example Workflow

* Developer opens a PR.
* Bot gets triggered via webhook.
* AI analyzes the Python files and posts detailed feedback.
* PR is labeled and potentially auto-merged.
* Review logs are stored and shown on the dashboard.

---

## 🛣️ Roadmap

- [x]PR code review with OpenAI
- [x]Auto-labeling and merge
- [x]Dashboard for historical reviews
- [ ]Multi-file analysis context-aware
- [ ]Custom review rules (security, style, etc.)
- [ ]Web-based dashboard with filters/search
- [ ]Slack/Discord notification integration

---

##  🤝 Contributing
Pull requests and suggestions are welcome!
Fork the repo, create a branch, and submit a PR.

---

## 🧑‍💻 Author
Made with ❤️ by Parth Goyal

---
Testing webhook
