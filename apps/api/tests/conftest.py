import os

# config.Settings() is instantiated at import time and DATABASE_URL has no
# default, so it must be set before anything imports `config`.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")