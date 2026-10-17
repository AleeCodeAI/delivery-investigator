from sqlalchemy import create_engine

from configs.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database.postgresql_url, echo=False)