from typing import Any

from app.main import app


def reverse(name: str, **kwargs: Any) -> str:
    return app.url_path_for(name, **kwargs)
