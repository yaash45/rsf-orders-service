from json import dumps, loads
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from .utils import is_valid_time_string, is_valid_uuid


def _build_create_users_payload(
    data: list[tuple[str, str, str]],
) -> list[dict[str, str]]:
    """
    Builds a http request payload for the POST request
    to the /users endpoint. The format of the payload looks like this:

    [
        {"name": "item1", "email": "item1@test.com", "kind": "admin"},
        {"name": "item2", "email": "item2@test.com", "kind": "admin"},
        ...
    ]
    """
    return [{"name": item[0], "email": item[1], "kind": item[2]} for item in data]


def test_basic_user_api(test_app: TestClient):
    """
    Tests various basic GET and POST calls to the user endpoint
    """

    # start with empty database
    response = test_app.get("/v0/users")
    assert response.status_code == status.HTTP_200_OK
    assert loads(response.content) == []

    # populate database
    request_payloads = _build_create_users_payload(
        [
            ("Max Verstappen", "max.v@redbull.com", "admin"),
            ("Lewis Hamilton", "lewis.h@mercedes.com", "test"),
            ("Sebastian Vettel", "seb.v@sbinnala.com", "client"),
        ]
    )

    user_id_map = {}

    for payload in request_payloads:
        response = test_app.post(
            "/v0/users",
            content=dumps(payload),
        )
        # verify that population succeeded
        assert response.status_code == status.HTTP_201_CREATED
        response_content = loads(response.content)
        assert is_valid_uuid(response_content.get("id", ""))
        assert is_valid_time_string(response_content.get("created", ""))
        assert is_valid_time_string(response_content.get("modified", ""))
        assert response_content.get("name", "") == payload["name"]
        assert response_content.get("email", "") == payload["email"]
        assert response_content.get("kind", "") == payload["kind"]

        # save ids to test querying by user id
        user_id_map[response_content["id"]] = response_content

    # query existing user by email
    response = test_app.get("/v0/users?email=max.v@redbull.com")
    assert response.status_code == status.HTTP_200_OK
    response_content = loads(response.content)
    assert len(response_content) == 1
    response_content = response_content[0]
    assert is_valid_uuid(response_content.get("id", ""))
    assert is_valid_time_string(response_content.get("created", ""))
    assert is_valid_time_string(response_content.get("modified", ""))
    assert response_content.get("name", "") == "Max Verstappen"
    assert response_content.get("email", "") == "max.v@redbull.com"
    assert response_content.get("kind", "") == "admin"

    # query non-existent user by email
    response = test_app.get("/v0/users?email=fake@f1.com")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # query users by id
    for user_id, expected in user_id_map.items():
        response = test_app.get(f"/v0/users/{user_id}")
        assert response.status_code == status.HTTP_200_OK
        response_content = loads(response.content)
        assert response_content == expected

    # query non-existent user
    response = test_app.get(f"/v0/users/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
