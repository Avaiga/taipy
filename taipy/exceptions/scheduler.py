class DependencyNotInstalled(Exception):
    def __init__(self, package_name: str):
        self.message = f"""
        Package '{package_name}' should be installed.
        Run 'pip install taipy[{package_name}]' to installed it.
        """
