from django.test import TestCase
from accounts.utils import Util


class UtilsFunctionTest(TestCase):
    """Test for methods of the Utils Classe"""
    def test_validate_phone_success(self):
        """Test validating a phone number success"""
        phone1 = '19 99999-9999'
        phone2 = '(19) 99999-9999'
        phone3 = '19 9999-9999'
        phone4 = '(19) 9999-9999'
        phone5 = '9999-9999'
        phone6 = '99999-9999'

        self.assertTrue(Util.validate_phone(phone1))
        self.assertTrue(Util.validate_phone(phone2))
        self.assertTrue(Util.validate_phone(phone3))
        self.assertTrue(Util.validate_phone(phone4))
        self.assertTrue(Util.validate_phone(phone5))
        self.assertTrue(Util.validate_phone(phone6))

    def test_validate_phone_error(self):
        """Test that validte phone return false for an invalid phone mask"""
        phone = '19999999999'
        self.assertFalse(Util.validate_phone(phone))

    def test_validate_cpf_success(self):
        """Test that true is returned for a valid cpf"""
        cpf = '204.782.150-96'
        self.assertTrue(Util.validate_cpf(cpf))

    def test_validate_cpf_error(self):
        """Test that false is returned for invalid cpf's"""
        cpf1 = '111.111.111-11'
        cpf2 = '142.141.033.01'

        self.assertFalse(Util.validate_cpf(cpf1))
        self.assertFalse(Util.validate_cpf(cpf2))
