import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from features.picpay.forms import PicPayRegisterForm
from features.picpay.models import PicPayAccount


VALID_CPF = "529.982.247-25"
VALID_CNPJ = "11.222.333/0001-81"


def valid_form_data(**kwargs):
    data = {
        "complete_name": "John Doe",
        "email": "john@test.com",
        "document": VALID_CPF,
        "sex": "M",
        "password1": "StrongPass123!",
    }
    data.update(kwargs)
    return data


def make_user(username, email):
    return User.objects.create_user(username=username, email=email, password="password123")


def make_account(user, document):
    return PicPayAccount.objects.create(
        user=user,
        complete_name="Existing User",
        email=user.email,
        document=document,
        document_type="cpf",
        sex="M",
        account_type="personal",
    )


@pytest.mark.unit
class CleanCompleteNameTest(TestCase):

    def test_valid_name_passes(self):
        form = PicPayRegisterForm(data=valid_form_data())
        form.is_valid()
        self.assertNotIn("complete_name", form.errors)

    def test_name_with_numbers_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(complete_name="John123"))
        form.is_valid()
        self.assertIn("complete_name", form.errors)

    def test_name_with_special_characters_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(complete_name="John@Doe"))
        form.is_valid()
        self.assertIn("complete_name", form.errors)

    def test_name_too_short_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(complete_name="Jo"))
        form.is_valid()
        self.assertIn("complete_name", form.errors)

    def test_name_with_accented_characters_passes(self):
        form = PicPayRegisterForm(data=valid_form_data(complete_name="João Ávila"))
        form.is_valid()
        self.assertNotIn("complete_name", form.errors)


@pytest.mark.unit
class CleanEmailTest(TestCase):

    def test_unique_email_passes(self):
        form = PicPayRegisterForm(data=valid_form_data())
        form.is_valid()
        self.assertNotIn("email", form.errors)

    def test_duplicate_email_is_invalid(self):
        User.objects.create_user(username="existing", email="john@test.com", password="password123")
        form = PicPayRegisterForm(data=valid_form_data())
        form.is_valid()
        self.assertIn("email", form.errors)

    def test_invalid_email_format_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(email="not-an-email"))
        form.is_valid()
        self.assertIn("email", form.errors)


@pytest.mark.unit
class CleanPasswordTest(TestCase):

    def test_password_with_6_or_more_characters_passes(self):
        form = PicPayRegisterForm(data=valid_form_data(password1="abc123"))
        form.is_valid()
        self.assertNotIn("password1", form.errors)

    def test_password_shorter_than_6_characters_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(password1="abc"))
        form.is_valid()
        self.assertIn("password1", form.errors)


@pytest.mark.unit
class CpfValidatorTest(TestCase):

    def test_valid_cpf_passes(self):
        form = PicPayRegisterForm(data=valid_form_data(document=VALID_CPF))
        form.is_valid()
        self.assertNotIn("document", form.errors)

    def test_invalid_cpf_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(document="111.111.111-11"))
        form.is_valid()
        self.assertIn("document", form.errors)

    def test_duplicate_cpf_is_invalid(self):
        user = make_user("existing", "existing@test.com")
        make_account(user, VALID_CPF)
        form = PicPayRegisterForm(data=valid_form_data(document=VALID_CPF))
        form.is_valid()
        self.assertIn("document", form.errors)


@pytest.mark.unit
class CnpjValidatorTest(TestCase):

    def test_valid_cnpj_passes(self):
        form = PicPayRegisterForm(data=valid_form_data(document=VALID_CNPJ))
        form.is_valid()
        self.assertNotIn("document", form.errors)

    def test_invalid_cnpj_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(document="11.111.111/1111-11"))
        form.is_valid()
        self.assertIn("document", form.errors)

    def test_duplicate_cnpj_is_invalid(self):
        user = make_user("existing", "existing@test.com")
        account = make_account(user, VALID_CNPJ)
        account.document_type = "cnpj"
        account.save()
        form = PicPayRegisterForm(data=valid_form_data(document=VALID_CNPJ))
        form.is_valid()
        self.assertIn("document", form.errors)


@pytest.mark.unit
class CleanDocumentTest(TestCase):

    def test_document_with_wrong_length_is_invalid(self):
        form = PicPayRegisterForm(data=valid_form_data(document="123.456"))
        form.is_valid()
        self.assertIn("document", form.errors)

    def test_cpf_sets_document_type_to_cpf(self):
        form = PicPayRegisterForm(data=valid_form_data(document=VALID_CPF))
        form.is_valid()
        self.assertEqual(form.cleaned_data.get("document_type"), "cpf")

    def test_cnpj_sets_document_type_to_cnpj(self):
        form = PicPayRegisterForm(data=valid_form_data(document=VALID_CNPJ))
        form.is_valid()
        self.assertEqual(form.cleaned_data.get("document_type"), "cnpj")
