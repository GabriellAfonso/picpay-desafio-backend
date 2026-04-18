import pytest
from django.test import TestCase
from apps.picpay.utils import get_first_and_last_name


@pytest.mark.unit
class GetFirstAndLastNameTest(TestCase):

    def test_full_name_returns_first_and_last(self):
        result = get_first_and_last_name("gabriel afonso")
        self.assertEqual(result, "Gabriel Afonso")

    def test_multiple_middle_names_returns_first_and_last(self):
        result = get_first_and_last_name("gabriel silva de afonso")
        self.assertEqual(result, "Gabriel Afonso")

    def test_single_name_returns_only_first(self):
        result = get_first_and_last_name("gabriel")
        self.assertEqual(result, "Gabriel")

    def test_capitalizes_lowercase_input(self):
        result = get_first_and_last_name("joao silva")
        self.assertEqual(result, "Joao Silva")

    def test_capitalizes_uppercase_input(self):
        result = get_first_and_last_name("JOAO SILVA")
        self.assertEqual(result, "Joao Silva")
