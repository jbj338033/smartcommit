import git
import os
from typing import List, Tuple

class GitService:
   def __init__(self, repo_path: str = None):
       self.repo_path = os.path.abspath(repo_path) if repo_path else None
       self.repo = None
       if repo_path:
           self.init_repo(repo_path)

   def init_repo(self, path: str):
       self.repo_path = os.path.abspath(path)
       try:
           self.repo = git.Repo(path)
       except git.exc.InvalidGitRepositoryError:
           self.repo = None

   def get_current_branch(self) -> str:
       try:
           return self.repo.active_branch.name
       except Exception:
           return 'main'

   def is_git_repo(self) -> bool:
       return self.repo is not None

   def init_new_repo(self) -> bool:
       try:
           self.repo = git.Repo.init(self.repo_path)
           return True
       except Exception as e:
           print(f"Error initializing repository: {str(e)}")
           return False

   def get_absolute_path(self, relative_path: str) -> str:
       if os.path.isabs(relative_path):
           return relative_path
       return os.path.join(self.repo_path, relative_path)

   def get_relative_path(self, absolute_path: str) -> str:
       try:
           return os.path.relpath(absolute_path, self.repo_path)
       except ValueError:
           return absolute_path

   def stage_file(self, file_path: str, change_type: str) -> bool:
       try:
           abs_path = os.path.abspath(os.path.join(self.repo_path, file_path))
           rel_path = os.path.relpath(abs_path, self.repo_path)
           
           if not abs_path.startswith(self.repo_path):
               raise Exception(f"File path {file_path} is outside repository")

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
               abs_path = os.path.join(self.repo_path, item.a_path)
               rel_path = os.path.relpath(abs_path, self.repo_path)
               
               if item.deleted_file:
                   files.append((rel_path, 'deleted', 'D'))
               else:
                   files.append((rel_path, 'modified', 'M'))
           
           for item in self.repo.untracked_files:
               abs_path = os.path.join(self.repo_path, item)
               rel_path = os.path.relpath(abs_path, self.repo_path)
               files.append((rel_path, 'untracked', 'A'))
               
       except Exception as e:
           print(f"Error getting unstaged files: {str(e)}")
           
       return files

   def get_unpushed_commits(self) -> List[git.Commit]:
       if not self.repo:
           return []
       
       try:
           if not self.repo.remotes:
               return []

           remote = self.repo.remote()
           current_branch = self.get_current_branch()
           
           try:
               tracking_branch = f'{remote.name}/{current_branch}'
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
           remote.push()
           return True
       except Exception as e:
           print(f"Error pushing changes: {str(e)}")
           return False