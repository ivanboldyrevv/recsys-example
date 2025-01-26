import pytest
from fastapi.testclient import TestClient

from service import Service
from .mock_depends import BrokerMock, KeyValueStorageMock
from transport.response import Recommendation, UserItemRecommendation
from transport.handlers import fetch_service
from main import app


TEST_UID = "test_uid"
TEST_IID = "test_iid"
TEST_DESC = "test-desc"
TEST_IMAGE_URL = "http://test.com"


@pytest.fixture(scope="class")
def mocked_service():
    class MockedService(Service):
        def fetch_recommendations(self, *args, **kwargs):
            return UserItemRecommendation(uid=TEST_UID, recommendations=[Recommendation(iid=TEST_IID,
                                                                                        description=TEST_DESC,
                                                                                        image_url=TEST_IMAGE_URL)])

        def fetch_items(self):
            return [Recommendation(iid=TEST_IID, description=TEST_DESC, image_url=TEST_IMAGE_URL)]

    yield MockedService(BrokerMock(), KeyValueStorageMock())


@pytest.fixture(scope="class")
def client(mocked_service):
    app.dependency_overrides[fetch_service] = lambda: mocked_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestTransport:
    def test_fetch_personal_recommendation(self, client):
        item_seq = {
            "uid": TEST_UID,
            "item_sequence": [{"iid": TEST_IID, "description": TEST_DESC}]
        }

        response = client.post("/recommendation/personal", json=item_seq)
        content = response.json()

        current = content["recommendations"][0]

        assert response.status_code == 200
        assert current["iid"] == TEST_IID
        assert current["description"] == TEST_DESC
        assert current["image_url"] == TEST_IMAGE_URL

    def test_fetch_items(self, client):
        response = client.get("/recommendation/items")

        assert response.status_code == 200
