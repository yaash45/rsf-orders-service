import unittest
from uuid import uuid4

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.user.adapters.mock import MockUserAdapter
from app.user.domain.models import UserCreate, UserKind, UserPublic
from app.user.service import UserService


class UserDomainTests(unittest.TestCase):
    """
    Unit tests for the user service module
    """

    def setUp(self) -> None:
        self.service = UserService.instance(port=MockUserAdapter())
        return super().setUp()

    def test_no_users_in_system(self):
        """
        Tests queries against an empty database
        """
        assert self.service.get_all_users() == []

        non_existent_user_id = uuid4()
        with self.assertRaises(EntityNotFoundError) as e:
            self.service.get_user(user_id=non_existent_user_id)

        assert str(non_existent_user_id) in str(e.exception)

        fake_email = "fake.user@suspicious.ca"
        with self.assertRaises(EntityNotFoundError) as e:
            self.service.find_user_by_email(email=fake_email)

        assert fake_email in str(e.exception)

    def test_one_user_in_system(self):
        """
        Tests queries with a single user in the database
        """
        user = UserCreate(
            name="Lewis Hamilton",
            email="lewis.hamilton@ferrari.com",
            kind=UserKind.CLIENT,
        )

        created: UserPublic | None = None

        try:
            created = self.service.setup_new_user(
                new_user=user,
            )
        except ConflictError:
            raise AssertionError(
                f"User with email '{user.email}' should not be in the system yet"
            )

        all_result: list[UserPublic] = self.service.get_all_users()

        assert len(all_result) == 1

        one_result: UserPublic = self.service.get_user(
            user_id=created.id,
        )
        email_result: UserPublic = self.service.find_user_by_email(
            email=user.email,
        )

        assert all_result.pop() == one_result == email_result

    def test_multiple_users_in_system(self):
        """
        Tests queries with multiple users in the database
        """
        raw_user_data = [
            {
                "name": "Max Verstappen",
                "email": "max@redbull.com",
                "kind": UserKind.ADMIN,
            },
            {
                "name": "George Russell",
                "email": "george@mercedes.com",
                "kind": UserKind.TEST,
            },
            {
                "name": "Oscar Piastri",
                "email": "oscar@piastri.com",
                "kind": UserKind.CLIENT,
            },
        ]

        created_users = [
            self.service.setup_new_user(
                new_user=UserCreate(**u),
            )
            for u in raw_user_data
        ]

        all_result = self.service.get_all_users()

        assert sorted(created_users, key=lambda u: u.name) == sorted(
            all_result, key=lambda u: u.name
        )

        def assert_get_by_id_and_email_succeeds(user: UserPublic):
            assert (
                self.service.get_user(
                    user_id=user.id,
                )
                == user
            )

            assert (
                self.service.find_user_by_email(
                    email=user.email,
                )
                == user
            )

        for u in created_users:
            assert_get_by_id_and_email_succeeds(u)


if __name__ == "__main__":
    unittest.main()
