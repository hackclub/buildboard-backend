import os
import time
import jwt
import requests
from typing import Optional, Dict, Any

class GitHubService:
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
        
        if self.private_key:
            # Handle escaped newlines if present
            self.private_key = self.private_key.replace("\\n", "\n")

    def generate_jwt(self) -> str:
        """Generate a JWT for the GitHub App."""
        if not self.app_id or not self.private_key:
            raise ValueError("GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY must be set")

        payload = {
            "iat": int(time.time()) - 60,
            "exp": int(time.time()) + (10 * 60),
            "iss": self.app_id
        }

        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_installation_token(self, installation_id: str) -> str:
        """Get an access token for a specific installation."""
        jwt_token = self.generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        response = requests.post(url, headers=headers)
        
        if response.status_code == 201:
            return response.json()["token"]
        else:
            raise Exception(f"Failed to get installation token: {response.status_code} - {response.text}")

    def get_readme(self, installation_id: str, repo_path: str) -> Dict[str, Any]:
        """Fetch the README content and SHA from GitHub."""
        token = self.get_installation_token(installation_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        url = f"https://api.github.com/repos/{repo_path}/readme"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return {"content": content, "sha": data["sha"]}
        elif response.status_code == 404:
            return {"content": "", "sha": None}
        else:
            raise Exception(f"Failed to fetch README: {response.status_code} - {response.text}")

    def update_readme(self, installation_id: str, repo_path: str, content: str, sha: Optional[str], message: str = "Update README via Buildboard") -> Dict[str, Any]:
        """Update the README on GitHub."""
        token = self.get_installation_token(installation_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        import base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        data = {
            "message": message,
            "content": encoded_content
        }
        if sha:
            data["sha"] = sha
            
        url = f"https://api.github.com/repos/{repo_path}/contents/README.md"
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            raise Exception(f"Failed to update README: {response.status_code} - {response.text}")
