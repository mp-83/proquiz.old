import pytest
from codechallenge.app import StoreConfig
from codechallenge.play.cache import ClientFactory


class TestCaseConfigSingleton:
    def t_singletonHasToBeCreatedOnce(self):
        sc = StoreConfig()
        settings_mock = {"setting": True}
        sc.config = settings_mock
        for _ in range(2):
            assert sc is StoreConfig()
            assert sc.config is settings_mock


class TestCaseWrongMethod:
    def t_usingNotAllowedMethodsResultsIn404not405(self, testapp):
        testapp.post("/question", status=404)
        testapp.patch("/", status=404)


class TestCaseCache:
    @pytest.mark.skip("These test requires Redis container to be up and running.")
    def t_connectionSetupAndValueStore(self):
        rclient = ClientFactory().new_client()
        rclient.set("test_key", "test_value")
        v = rclient.get("test_key")
        assert v == b"test_value"
