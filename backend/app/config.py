import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://shopuser:shoppass@localhost:5432/shopdb",
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
