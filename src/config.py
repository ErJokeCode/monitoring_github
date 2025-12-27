from pydantic_settings import BaseSettings
import logging
import os 

_log = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Базовые настройки приложения"""
    CORS: str = "*"
    VIEW_DOCS: bool = True
    ROOT_PATH: str = ""
    
    GITHUB_OWNER: str = "ErJokeCode"
    GITHUB_REPO: str = "monitoring_github"
    GITHUB_TOKEN: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    NATS_HOST: str
    NATS_PORT: int

    LOG_LEVEL: str = "INFO"

    def __init__(self):
        super().__init__()

        log_level = getattr(logging, self.LOG_LEVEL)
        self.config_logging(log_level)
        
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        self._name_dir = os.path.basename(script_dir)

    def config_logging(self, level: int = logging.INFO) -> None:
        logging.basicConfig(
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(module)20s:%(lineno)-3d %(levelname)-7s - %(message)s",
        )
        
    @property
    def SERVICE_NAME(self):
        return self._name_dir
    
    @property
    def NATS_subject_events(self):
        return "github.events"

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def NATS_URL(self):
        return f"nats://{self.NATS_HOST}:{self.NATS_PORT}"

    @property
    def URLS_CORS(self) -> list[str]:
        return [c.strip() for c in self.CORS.split(",")]


settings = Settings()
