import os
from huggingface_hub import HfApi

def deploy():
    token = os.environ.get('HF_TOKEN')
    api = HfApi(token=token)
    
    user = api.whoami()['name']
    repo_id = f"{user}/vce-mcp"
    
    print(f"Checking if space {repo_id} exists...")
    try:
        api.repo_info(repo_id, repo_type="space")
        print("Space exists.")
    except Exception as e:
        print("Space not found. Creating it now...")
        api.create_repo(repo_id=repo_id, repo_type="space", space_sdk="docker")
        print("Space created successfully!")

    print("Uploading project files to Hugging Face...")
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=[
            ".venv/*",
            ".venv",
            ".git/*",
            ".git",
            "__pycache__/*",
            ".pytest_cache/*",
            "*.pyc",
            "uvicorn.log",
            "scripts/*"
        ]
    )
    # The Hugging Face subdomain is formatted as: username-spacename.hf.space
    # Convert repo name and user name to lowercase for the URL, and replace spaces with hyphens if any
    space_domain = f"{user.lower()}-vce-mcp.hf.space"
    
    print(f"Deployment successful! Your Space URL is: https://{space_domain}")
    print(f"Your MCP Server Endpoint will be: https://{space_domain}/mcp")

if __name__ == "__main__":
    deploy()
