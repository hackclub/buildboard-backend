import os
import time
import jwt
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse


class AppNotInstalledError(Exception):
    """Raised when the GitHub App is not installed on a repository."""
    pass


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

    def _app_headers(self) -> dict:
        """Get headers for GitHub App authentication (JWT)."""
        jwt_token = self.generate_jwt()
        return {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def normalize_repo_path(self, repo_input: str) -> str:
        """
        Normalize various GitHub repo formats to 'owner/repo'.
        
        Accepts:
          - owner/repo
          - https://github.com/owner/repo
          - https://github.com/owner/repo.git
          - git@github.com:owner/repo.git
        
        Returns: 'owner/repo'
        """
        repo_input = repo_input.strip()
        
        if not repo_input:
            raise ValueError("Repository cannot be empty")

        # URL format (http/https)
        if repo_input.startswith("http://") or repo_input.startswith("https://"):
            parsed = urlparse(repo_input)
            path = parsed.path.strip("/")
            parts = path.split("/")
            if len(parts) < 2:
                raise ValueError("Invalid GitHub repository URL")
            owner, repo = parts[0], parts[1]
            if repo.endswith(".git"):
                repo = repo[:-4]
            return f"{owner}/{repo}"

        # SSH format
        if repo_input.startswith("git@github.com:"):
            path = repo_input.split(":", 1)[1]
            if path.endswith(".git"):
                path = path[:-4]
            if "/" not in path:
                raise ValueError("Invalid GitHub SSH URL")
            return path

        # Assume owner/repo format
        if "/" not in repo_input:
            raise ValueError("Repository must be in 'owner/repo' format or a GitHub URL")
        
        parts = repo_input.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("Invalid repository format. Use 'owner/repo'")
        
        return repo_input

    def get_installation_for_repo(self, repo_path: str) -> Tuple[int, str]:
        """
        Get the GitHub App installation ID for a repository.
        
        Args:
            repo_path: Repository in 'owner/repo' format (will be normalized)
            
        Returns:
            Tuple of (installation_id, canonical_full_name)
            
        Raises:
            AppNotInstalledError: If the GitHub App is not installed on the repo
        """
        repo_path = self.normalize_repo_path(repo_path)
        headers = self._app_headers()
        
        url = f"https://api.github.com/repos/{repo_path}/installation"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            installation_id = data["id"]
            
            # Get canonical repo name using installation token
            try:
                token = self.get_installation_token(str(installation_id))
                repo_response = requests.get(
                    f"https://api.github.com/repos/{repo_path}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28",
                    },
                )
                if repo_response.status_code == 200:
                    canonical_name = repo_response.json()["full_name"]
                else:
                    canonical_name = repo_path
            except Exception:
                canonical_name = repo_path
            
            return installation_id, canonical_name
        
        if response.status_code == 404:
            raise AppNotInstalledError(
                f"The Buildboard GitHub App is not installed on '{repo_path}'. "
                "Please install the app on this repository and try again."
            )
        
        if response.status_code == 403:
            raise AppNotInstalledError(
                f"Access denied for repository '{repo_path}'. "
                "Make sure the Buildboard GitHub App is installed and has access to this repository."
            )
        
        raise Exception(
            f"Failed to find installation for repository: {response.status_code} - {response.text}"
        )

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
