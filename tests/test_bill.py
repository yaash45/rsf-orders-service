from json import dumps, loads

from fastapi import status

# TODO: add more tests after refactoring bills to be associated with orders


def test_issue_bill(test_app):
    # add one user
    response = test_app.post(
        "/v0/users",
        content=dumps(
            [
                {
                    "name": "test",
                    "email": "test@foo.com",
                    "kind": "client",
                },
            ]
        ),
    )

    new_user = loads(response.content)[0]
    user_id = new_user.get("id", None)

    if user_id is None:
        raise AssertionError("New user created with None id")

    # issue bill
    response = test_app.post(
        "/v0/bills",
        content=dumps(
            {
                "user_id": user_id,
                "amount": 100.0,
                "image_url": None,
                "paid": False,
            },
        ),
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_get_bill(test_app):
    # add one user
    response = test_app.post(
        "/v0/users",
        content=dumps(
            [
                {
                    "name": "test",
                    "email": "test@foo.com",
                    "kind": "client",
                },
            ]
        ),
    )

    new_user = loads(response.content)[0]
    user_id = new_user.get("id", None)

    if user_id is None:
        raise AssertionError("New user created with None id")

    # issue bill
    response = test_app.post(
        "/v0/bills",
        content=dumps(
            {
                "user_id": user_id,
                "amount": 100.0,
                "image_url": "https://example.com/image_bill_2025_30_10.jpg",
                "paid": False,
            },
        ),
    )

    new_bill = loads(response.content)
    bill_id = new_bill.get("id", None)

    if bill_id is None:
        raise AssertionError("New bill created with None id")

    # get bill
    response = test_app.get(f"/v0/bills/{bill_id}")

    assert response.status_code == status.HTTP_200_OK

    response_deserialized = loads(response.content)

    assert response_deserialized.get("id", None) == bill_id
    assert response_deserialized.get("user_id", None) == user_id
    assert response_deserialized.get("amount", None) == 100.0
    assert (
        response_deserialized.get("image_url", None)
        == "https://example.com/image_bill_2025_30_10.jpg"
    )
    assert response_deserialized.get("paid", None) is False
