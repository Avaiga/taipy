class LoadingError(Exception):
    """Raised if an error occurs while loading the configuration file."""

    pass


class ConfigurationIssueError(Exception):
    """Raised if an inconsistency has been detected in the configuration."""

    pass
