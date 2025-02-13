import git
import os
from typing import List, Tuple, Optional
from pathlib import Path

class GitService:
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path).resolve() if repo_path else None
        self.repo = None
        if repo_path:
            self.init_repo(repo_path)

    def init_repo(self, path: str) -> None:
        self.repo_path = Path(path).resolve()
        try:
            self.repo = git.Repo(path)
            self.repo.git.update_environment(GIT_PYTHON_REFRESH='quiet')
        except git.exc.InvalidGitRepositoryError:
            self.repo = None

    def get_current_branch(self) -> str:
        try:
            return self.repo.active_branch.name
        except (Exception, TypeError, AttributeError):
            try:
                return self.repo.head.reference.name
            except:
                return 'main'

    def is_git_repo(self) -> bool:
        return self.repo is not None and self.repo.git_dir is not None

    def init_new_repo(self) -> bool:
        try:
            self.repo = git.Repo.init(self.repo_path)
            initial_commit = True
            if not self.repo.head.is_valid():
                self.repo.index.commit("Initial commit")
            return True
        except Exception as e:
            print(f"Error initializing repository: {str(e)}")
            return False

    def get_remote_branches(self) -> List[str]:
        try:
            return [ref.name for ref in self.repo.remote().refs]
        except:
            return []

    def stage_file(self, file_path: str, change_type: str) -> bool:
        try:
            abs_path = Path(file_path).resolve()
            if not str(abs_path).startswith(str(self.repo_path)):
                raise Exception(f"File path {file_path} is outside repository")

            rel_path = str(abs_path.relative_to(self.repo_path))
            
            if change_type == 'D':
                self.repo.index.remove([rel_path], working_tree=True)
            else:
                self.repo.index.add([rel_path])
            return True
        except Exception as e:
            print(f"Error staging file: {str(e)}")
            return False

    def commit(self, message: str) -> bool:
        try:
            if not self.repo.is_dirty(untracked_files=True):
                return False
            self.repo.index.commit(message)
            return True
        except Exception as e:
            print(f"Error committing: {str(e)}")
            return False

    def get_unstaged_files(self) -> List[Tuple[str, str, str]]:
        if not self.repo:
            return []
        
        files = []
        try:
            for item in self.repo.index.diff(None):
                if item.deleted_file:
                    files.append((item.a_path, 'deleted', 'D'))
                else:
                    files.append((item.a_path, 'modified', 'M'))
            
            for item in self.repo.untracked_files:
                files.append((item, 'untracked', 'A'))
                
        except Exception as e:
            print(f"Error getting unstaged files: {str(e)}")
            
        return files

    def get_unpushed_commits(self) -> List[git.Commit]:
        if not self.repo:
            return []
        
        try:
            if not self.repo.remotes:
                return list(self.repo.iter_commits())

            remote = self.repo.remote()
            current_branch = self.get_current_branch()
            
            try:
                tracking_branch = f'{remote.name}/{current_branch}'
                if tracking_branch not in [ref.name for ref in self.repo.refs]:
                    return list(self.repo.iter_commits())
                return list(self.repo.iter_commits(f'{tracking_branch}..{current_branch}'))
            except git.exc.GitCommandError:
                return list(self.repo.iter_commits())
        except Exception as e:
            print(f"Error getting unpushed commits: {str(e)}")
            return []

    def push(self) -> bool:
        try:
            if not self.repo.remotes:
                return False
            remote = self.repo.remote()
            current_branch = self.get_current_branch()
            remote.push(refspec=f'{current_branch}:{current_branch}')
            return True
        except Exception as e:
            print(f"Error pushing changes: {str(e)}")
            return False

    def has_remote(self) -> bool:
        return bool(self.repo and self.repo.remotes)

    def get_repo_name(self) -> str:
        try:
            return os.path.basename(self.repo_path)
        except:
            return "Unknown Repository"
        
    def get_relative_path(self, absolute_path: str) -> str:
        try:
            abs_path = os.path.abspath(absolute_path)
            repo_path = os.path.abspath(self.repo_path)
            
            if os.path.isabs(absolute_path):
                return os.path.relpath(abs_path, repo_path)
            else:
                return absolute_path
        except ValueError:
            return absolute_path

    def get_absolute_path(self, file_path: str) -> str:
        if Path(file_path).is_absolute():
            return str(Path(file_path))
        return str(Path(self.repo_path) / file_path) 