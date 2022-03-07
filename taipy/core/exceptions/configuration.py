class LoadingError(Exception):
    """Raised if an error occurs while loading the configuration file."""

    pass


class ConfigurationIssueError(Exception):
    """Raised if an inconsistency has been detected in the configuration."""

    pass


class InconsistentEnvVariableError(Exception):
    """Inconsistency value has been detected in an environment variable referenced by the configuration."""

    pass


class MissingEnvVariableError(Exception):
    """Environment variable referenced in configuration is missing."""

    pass


class InvalidConfigurationId(Exception):
    """Configuration id is not valid."""

    pass
