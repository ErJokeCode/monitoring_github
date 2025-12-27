from .base import IBaseRepo
from infrastructure.database.models import GitHubEvent


class IGitHubEventRepo(IBaseRepo[GitHubEvent]):
    pass
