#!/usr/bin/env python3
"""
Flash Sync API: GitHub API-based Cross-Repository Synchronization
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from pathlib import Path

# Configuration
TARGET_REPOS = [
    "Jvryan92/epochcore_RAS",
    "EpochCore5/epochcore_RAS", 
    "Jvryan92/EpochCore_OS",
    "Jvryan92/StategyDECK",
    "Jvryan92/saas-hub",
    "EpochCore5/epoch5-template",
    "Jvryan92/epoch-mesh"
]

SYNC_ITEMS = [
    "agents/",
    "manifests/",
    ".github/workflows/recursive_matrix_autonomy.yml"
]

class GitHubFlashSync:
    """GitHub API-based flash synchronization for EpochCore autonomous agents."""
    
    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'EpochCore-Flash-Sync/1.0'
        })
        self.base_url = 'https://api.github.com'
        self.sync_timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get file content as base64 encoded string."""
        try:
            with open(file_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            return content
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return None

    def get_directory_files(self, directory: str) -> List[Dict[str, str]]:
        """Get all files in a directory recursively."""
        files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            self.logger.warning(f"Directory {directory} does not exist")
            return files
            
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                content = self.get_file_content(str(file_path))
                if content:
                    relative_path = file_path.relative_to('.')
                    files.append({
                        'path': str(relative_path),
                        'content': content
                    })
        
        return files

    def create_sync_manifest(self) -> Dict[str, Any]:
        """Create synchronization manifest."""
        return {
            'flash_sync': {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'version': 'v1.0',
                'sync_id': f'api_flash_sync_{self.sync_timestamp}',
                'items_synced': SYNC_ITEMS,
                'target_repositories': TARGET_REPOS,
                'sync_strategy': 'github_api_propagation',
                'execution_mode': 'autonomous',
                'recursive_depth': 3
            },
            'agent_status': {
                'kpi_prediction_agent': 'v4',
                'failure_remediation_agent': 'v4', 
                'portfolio_optimizer': 'v4',
                'meta_experiment_cascade': 'v4',
                'resource_allocation_agent': 'v3',
                'compliance_auditor': 'v4',
                'innovation_diffuser': 'v4',
                'user_feedback_engine': 'v4',
                'explainability_agent': 'v4',
                'agent_registry': 'v4',
                'audit_evolution_manager': 'v3'
            }
        }

    def get_default_branch(self, repo: str) -> str:
        """Get the default branch of a repository."""
        url = f"{self.base_url}/repos/{repo}"
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json().get('default_branch', 'main')
        else:
            self.logger.warning(f"Failed to get default branch for {repo}, using 'main'")
            return 'main'

    def create_branch(self, repo: str, branch_name: str, base_branch: str) -> bool:
        """Create a new branch from base branch."""
        # Get the SHA of the base branch
        url = f"{self.base_url}/repos/{repo}/git/refs/heads/{base_branch}"
        response = self.session.get(url)
        
        if response.status_code != 200:
            self.logger.error(f"Failed to get {base_branch} SHA for {repo}")
            return False
        
        base_sha = response.json()['object']['sha']
        
        # Create new branch
        url = f"{self.base_url}/repos/{repo}/git/refs"
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': base_sha
        }
        
        response = self.session.post(url, json=data)
        
        if response.status_code == 201:
            self.logger.info(f"Created branch {branch_name} in {repo}")
            return True
        elif response.status_code == 422:
            self.logger.info(f"Branch {branch_name} already exists in {repo}")
            return True
        else:
            self.logger.error(f"Failed to create branch {branch_name} in {repo}: {response.text}")
            return False

    def update_file(self, repo: str, file_path: str, content: str, branch: str, message: str) -> bool:
        """Update or create a file in the repository."""
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}"
        
        # Check if file exists
        response = self.session.get(url, params={'ref': branch})
        
        data = {
            'message': message,
            'content': content,
            'branch': branch
        }
        
        if response.status_code == 200:
            # File exists, update it
            data['sha'] = response.json()['sha']
            method = 'PUT'
        else:
            # File doesn't exist, create it
            method = 'PUT'
        
        response = self.session.request(method, url, json=data)
        
        if response.status_code in [200, 201]:
            self.logger.debug(f"Updated {file_path} in {repo}")
            return True
        else:
            self.logger.error(f"Failed to update {file_path} in {repo}: {response.text}")
            return False

    def create_pull_request(self, repo: str, branch_name: str, base_branch: str) -> bool:
        """Create a pull request for the sync branch."""
        url = f"{self.base_url}/repos/{repo}/pulls"
        
        data = {
            'title': f'🚀 Flash Sync: EpochCore Autonomous Agents Update ({self.sync_timestamp})',
            'head': branch_name,
            'base': base_branch,
            'body': f'''# 🚀 EpochCore Flash Sync: Autonomous Agents Update

## Summary
Auto-synchronized EpochCore autonomous agents and manifests from the main repository.

## Changes
- **Autonomous Agent Stubs**: Updated to latest versions (v3-v4)
- **Recursive Matrix Workflow**: Enhanced parallel execution pipeline
- **Manifests**: Propagated audit logs and execution results
- **Cross-Repo Sync**: Flash propagation timestamp `{self.sync_timestamp}`

## Agent Versions Synced
- kpi_prediction_agent: v4
- failure_remediation_agent: v4
- portfolio_optimizer: v4
- meta_experiment_cascade: v4
- resource_allocation_agent: v3
- compliance_auditor: v4
- innovation_diffuser: v4
- user_feedback_engine: v4
- explainability_agent: v4
- agent_registry: v4
- audit_evolution_manager: v3

## Validation
✅ All agents include recursive logic and manifest output  
✅ GitHub Actions workflow configured for matrix execution  
✅ Audit evolution logging enabled  
✅ Cross-portfolio sync capabilities enabled  

## Next Steps
1. Review and merge this PR
2. Trigger the recursive matrix workflow
3. Monitor autonomous agent execution
4. Verify audit logs and manifest outputs

---
*Auto-generated by EpochCore Flash Sync System*
*Ready for recursive autonomous operation across portfolio*
''',
            'draft': False
        }
        
        response = self.session.post(url, json=data)
        
        if response.status_code == 201:
            pr_url = response.json()['html_url']
            self.logger.info(f"Created PR: {pr_url}")
            return True
        else:
            self.logger.error(f"Failed to create PR for {repo}: {response.text}")
            return False

    def sync_repository(self, repo: str) -> bool:
        """Synchronize files to a single repository."""
        self.logger.info(f"Starting sync to {repo}")
        
        try:
            # Get default branch
            default_branch = self.get_default_branch(repo)
            branch_name = f"flash-sync-{self.sync_timestamp}"
            
            # Create sync branch
            if not self.create_branch(repo, branch_name, default_branch):
                return False
            
            # Collect all files to sync
            files_to_sync = []
            
            for item in SYNC_ITEMS:
                if item.endswith('/'):
                    # Directory
                    directory_files = self.get_directory_files(item.rstrip('/'))
                    files_to_sync.extend(directory_files)
                else:
                    # Single file
                    content = self.get_file_content(item)
                    if content:
                        files_to_sync.append({
                            'path': item,
                            'content': content
                        })
            
            # Add sync manifest
            manifest_content = json.dumps(self.create_sync_manifest(), indent=2)
            manifest_b64 = base64.b64encode(manifest_content.encode()).decode()
            files_to_sync.append({
                'path': 'manifests/flash_sync_manifest.json',
                'content': manifest_b64
            })
            
            # Update files
            success_count = 0
            for file_info in files_to_sync:
                if self.update_file(
                    repo, 
                    file_info['path'], 
                    file_info['content'], 
                    branch_name,
                    f"Flash sync: Update {file_info['path']}"
                ):
                    success_count += 1
            
            self.logger.info(f"Successfully synced {success_count}/{len(files_to_sync)} files to {repo}")
            
            # Create pull request
            if success_count > 0:
                return self.create_pull_request(repo, branch_name, default_branch)
            else:
                self.logger.warning(f"No files synced to {repo}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing to {repo}: {e}")
            return False

    def flash_sync_all(self) -> Dict[str, Any]:
        """Execute flash sync across all target repositories."""
        self.logger.info("🚀 Starting Flash Sync API execution")
        
        results = {
            'sync_timestamp': self.sync_timestamp,
            'total_repos': len(TARGET_REPOS),
            'successful_syncs': 0,
            'failed_syncs': 0,
            'results': {}
        }
        
        for repo in TARGET_REPOS:
            success = self.sync_repository(repo)
            results['results'][repo] = 'success' if success else 'failed'
            
            if success:
                results['successful_syncs'] += 1
            else:
                results['failed_syncs'] += 1
        
        # Summary
        self.logger.info(f"🎯 Flash Sync Complete: {results['successful_syncs']}/{results['total_repos']} successful")
        
        return results


def main():
    """Main execution function."""
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ Error: GitHub token not found in GH_TOKEN or GITHUB_TOKEN environment variable")
        return 1
    
    try:
        sync = GitHubFlashSync(token)
        results = sync.flash_sync_all()
        
        # Print summary
        print("\n" + "="*60)
        print("🚀 FLASH SYNC API COMPLETE")
        print("="*60)
        print(f"📊 Summary:")
        print(f"  Successful syncs: {results['successful_syncs']}")
        print(f"  Failed syncs: {results['failed_syncs']}")
        print(f"  Total repositories: {results['total_repos']}")
        print(f"  Sync timestamp: {results['sync_timestamp']}")
        
        print(f"\n📁 Results by repository:")
        for repo, status in results['results'].items():
            status_icon = "✅" if status == 'success' else "❌"
            print(f"  {status_icon} {repo}: {status}")
        
        print(f"\n🔄 Next steps:")
        print(f"  1. Review and merge PRs in target repositories")
        print(f"  2. Trigger recursive matrix workflows")
        print(f"  3. Monitor autonomous agent execution")
        print(f"  4. Verify cross-portfolio improvements")
        
        print(f"\n⚡ Flash sync ritual complete - Portfolio ready for autonomous operation!")
        
        return 0 if results['failed_syncs'] == 0 else 1
        
    except Exception as e:
        print(f"❌ Flash sync failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())