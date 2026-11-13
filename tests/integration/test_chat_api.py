from fastapi import FastAPI
from fastapi.testclient import TestClient

from policy_assistant.api.routes.chat import router


class FakeQueryResult:
    def __init__(self, answer, sources):
        self.answer = answer
        self.sources = sources


class FakeQueryUseCase:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def execute(self, question):
        if self.should_fail:
            raise RuntimeError("Internal database credentials leaked")

        return FakeQueryResult(
            answer="Employees receive 20 annual leaves.",
            sources=[],
        )


def create_test_client(should_fail=False):
    app = FastAPI()
    app.include_router(router)

    app.state.dependencies = {
        "query_use_case": FakeQueryUseCase(
            should_fail=should_fail
        )
    }

    return TestClient(app)


def test_chat_endpoint_returns_answer():
    client = create_test_client()

    response = client.post(
        "/api/v1/chat/query",
        json={"question": "How many annual leaves?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Employees receive 20 annual leaves."
    )
    assert response.json()["sources"] == []


def test_chat_endpoint_rejects_empty_question():
    client = create_test_client()

    response = client.post(
        "/api/v1/chat/query",
        json={"question": "   "},
    )

    assert response.status_code == 422


def test_chat_endpoint_rejects_missing_question():
    client = create_test_client()

    response = client.post(
        "/api/v1/chat/query",
        json={},
    )

    assert response.status_code == 422


def test_chat_endpoint_hides_internal_errors():
    client = create_test_client(should_fail=True)

    response = client.post(
        "/api/v1/chat/query",
        json={"question": "How many annual leaves?"},
    )

    assert response.status_code == 500
    assert "Internal database credentials leaked" not in response.text