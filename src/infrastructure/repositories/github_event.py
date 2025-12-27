from ..database.models import GitHubEvent
from domain.interfaces.github_event import IGitHubEventRepo
from .base import BaseRepo


class TaskRepo(IGitHubEventRepo, BaseRepo[GitHubEvent]):
    model = GitHubEvent
