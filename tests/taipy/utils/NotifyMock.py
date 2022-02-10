class NotifyMock:
    """
    A shared class for testing notification on jobStatus of pipeline level and scenario level

    "entity" can be understood as either "scenario" or "pipeline".
    """

    def __init__(self, entity):
        self.scenario = entity
        self.nb_called = 0
        self.__name__ = "NotifyMock"

    def __call__(self, entity, job):
        assert entity == self.scenario
        if self.nb_called == 0:
            assert job.is_pending()
        if self.nb_called == 1:
            assert job.is_running()
        if self.nb_called == 2:
            assert job.is_finished()
        self.nb_called += 1

    def assert_called_3_times(self):
        assert self.nb_called == 3

    def assert_not_called(self):
        assert self.nb_called == 0

    def reset(self):
        self.nb_called = 0
