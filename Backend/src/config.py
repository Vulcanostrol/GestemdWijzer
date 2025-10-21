# -*- coding: utf-8 -*-
import os
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Environment(str, Enum):
    """
    Application environment types.

    Defines the possible environments the application can run in:
    development, staging, production, and test.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


def get_environment() -> Environment:
    """
    Get the current environment.

    Returns:
        Environment: The current environment (development, staging, production, or test)
    """
    match os.getenv("APP_ENV", "development").lower():
        case "production" | "prod":
            return Environment.PRODUCTION
        case "staging" | "stage":
            return Environment.STAGING
        case "test":
            return Environment.TEST
        case _:
            return Environment.DEVELOPMENT


def parse_list(env_value: Optional[str], default: Optional[list] = None) -> list:
    """Parse a comma-separated string into a list."""
    if env_value == "" or env_value is None:
        return default or []

    # Remove quotes if they exist
    value = env_value.strip("\"'")
    # Handle single value case
    if "," not in value:
        return [value]
    # Split comma-separated values
    return [item.strip() for item in value.split(",") if item.strip()]


def load_env_file() -> Optional[str]:
    """Load environment-specific .env file."""
    env = get_environment()
    print(f"Loading environment: {env}")
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Define env files in priority order
    env_files = [
        os.path.join(base_dir, f".env.{env.value}.local"),
        os.path.join(base_dir, f".env.{env.value}"),
        os.path.join(base_dir, ".env.local"),
        os.path.join(base_dir, ".env"),
    ]

    # Load the first env file that exists
    for env_file in env_files:
        if Path(env_file).exists():
            load_dotenv(dotenv_path=env_file)
            print(f"Loaded environment from {env_file}")
            return env_file

    # Fall back to default if no env file found
    return None


ENV_FILE = load_env_file()


def get_secret_or_env(
    env_secret: str, env_name: str, default: Optional[str] = None
) -> str:
    """
    Looks up `env_secret` in the environment variables and uses it as a path to load from the mounted secret. If  it
    cannot find the path in the environment variables, or the secret file does not exist, it will instead look for the
    `env_name` in the environment variables.
    """
    if env_secret in os.environ:
        secret_path = Path(os.getenv(env_secret, ""))
        if secret_path.is_file() and secret_path.exists():
            with open(secret_path, "r") as f:
                return f.read().strip()

    if env_name in os.environ:
        return os.getenv(env_name, "")

    if default is not None:
        print(
            f"WARNING: Using default for env variable {env_name}. Make sure this is intended, or set a value in the "
            f".env file"
        )
        return default

    raise ValueError(
        f"Invalid usage of get_secret_or_env function. If env_secret {env_secret} and the env_name {env_name} are not "
        f"in the .env file, a default value must be provided."
    )


class Settings:
    def __init__(self) -> None:
        self.ENVIRONMENT = get_environment()

        # General settings
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "GestemdWijzer")
        self.VERSION = os.getenv("VERSION", "0.1.0")
        self.DESCRIPTION = os.getenv(
            "DESCRIPTION",
            "GestemdWijzer - Inzage in het stemmen van partijen in de Tweede Kamer met data van moties.",
        )
        self.API_V1_STR = os.getenv("API_V1_STR", "api/v1")
        self.DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t", "yes")

        # CORS Settings
        self.ALLOWED_ORIGINS = parse_list(
            env_value=os.getenv("ALLOWED_ORIGINS"),
            default=["*"],
        )

        # Authorization tokens
        self.AUTH_TOKENS = parse_list(
            env_value=get_secret_or_env("AUTH_TOKENS_FILE", "AUTH_TOKENS", default=""),
            default=["*"],
        )
        # By doing the auth-enabled flag this way, we enable auth by default (even with typos in configs), unless
        # specifically specified to be disabled.
        self.AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() not in [
            "false",
            "0",
            "f",
            "n",
            "no",
        ]
        if not self.AUTH_ENABLED:
            print(
                "WARNING: AUTH_ENABLED is set to false. Make sure this is intended, or set the env variable."
            )

        # Logging config
        self.LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" or "console"

        # Scraping
        self.USER_AGENT = os.getenv("USER_AGENT", "GestemdWijzer")

        self.apply_environment_settings()

    def apply_environment_settings(self) -> None:
        """Apply environment-specific settings based on the current environment."""
        match self.ENVIRONMENT:
            case Environment.PRODUCTION:
                self.DEBUG = False
                self.LOG_LEVEL = "WARNING"
                self.LOG_FORMAT = "console"
            case Environment.STAGING:
                self.DEBUG = False
                self.LOG_LEVEL = "INFO"
            case Environment.TEST:
                self.DEBUG = True
                self.LOG_LEVEL = "DEBUG"
                self.LOG_FORMAT = "console"
            case Environment.DEVELOPMENT:
                self.DEBUG = True
                self.LOG_LEVEL = "DEBUG"


settings = Settings()
