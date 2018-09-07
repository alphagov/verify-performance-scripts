import os


class MissingEnvironmentVariableError(Exception):
    def __init__(self, env_var):
        return super().__init__(f"Missing environment variable {env_var}")


def check_get_env(key):
    """Return the value of the environment variable _key_.

    Use this instead of os.getenv when the environment variable must be present
    and if not an exception should be raised.
    """
    value = os.getenv(key)
    if value is None:
        raise MissingEnvironmentVariableError(key)
    return value
