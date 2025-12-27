from infrastructure.repositories.github_event import TaskRepo
from infrastructure.ws_manager import WSManager
from infrastructure.nats_manager import NATSClient

from .stories.github_event_stories import TaskStories


class Application:
    ws_manager = WSManager()
    nats_client = NATSClient()
    
    task_repo = TaskRepo()

    github_stories = TaskStories(
        repo=task_repo,
        ws_manager=ws_manager, 
        nats_client=nats_client
    )
