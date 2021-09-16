class AppConfig(object):
    def __init__(self):
        self.pages = []
        self.routes = []
        self.app_config = {}
        self.style_config = {}

    def load_config(self, app_config={}, style_config={}):
        self.app_config.update(app_config)
        self.style_config.update(style_config)
