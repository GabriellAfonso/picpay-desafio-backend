import pytest
from django.test import TestCase
from unittest.mock import MagicMock, patch
from django.contrib.auth.models import User
from features.picpay.models import PicPayAccount
from features.picpay.repositories.account_repository import AccountRepository
from features.picpay.services.guest_login_service import GuestLoginService


def make_service(account_repo=None):
    return GuestLoginService(account_repo=account_repo or AccountRepository())


@pytest.mark.unit
class GuestLoginServiceTest(TestCase):

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_creates_guest_user_in_db(self, mock_assign_role):
        make_service().create_guest()
        self.assertEqual(User.objects.filter(username__startswith="guest_").count(), 1)

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_returns_the_created_user(self, mock_assign_role):
        user = make_service().create_guest()
        self.assertIsInstance(user, User)

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_username_starts_with_guest_prefix(self, mock_assign_role):
        user = make_service().create_guest()
        self.assertTrue(user.username.startswith("guest_"))

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_assigns_personal_role(self, mock_assign_role):
        user = make_service().create_guest()
        mock_assign_role.assert_called_once_with(user, "personal")

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_creates_picpay_account_for_guest(self, mock_assign_role):
        user = make_service().create_guest()
        self.assertTrue(PicPayAccount.objects.filter(user=user).exists())

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_guest_account_name_is_convidado(self, mock_assign_role):
        user = make_service().create_guest()
        account = PicPayAccount.objects.get(user=user)
        self.assertEqual(account.complete_name, "Convidado")

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_guest_account_type_is_personal(self, mock_assign_role):
        user = make_service().create_guest()
        account = PicPayAccount.objects.get(user=user)
        self.assertEqual(account.account_type, "personal")

    @patch("features.picpay.services.guest_login_service.assign_role")
    def test_two_guests_have_unique_usernames(self, mock_assign_role):
        user1 = make_service().create_guest()
        user2 = make_service().create_guest()
        self.assertNotEqual(user1.username, user2.username)

    def test_delegates_user_creation_to_repository(self):
        mock_repo = MagicMock()
        mock_repo.create_guest_user.return_value = MagicMock(spec=User)

        with patch("features.picpay.services.guest_login_service.assign_role"):
            GuestLoginService(account_repo=mock_repo).create_guest()

        mock_repo.create_guest_user.assert_called_once()
        mock_repo.create_account.assert_called_once()
