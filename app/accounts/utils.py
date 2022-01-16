import re


class Util:
    @staticmethod
    def validate_cpf(numbers):
        """Method to validate a CPF"""
        #  Obtém os números do CPF e ignora outros caracteres
        cpf = [int(char) for char in numbers if char.isdigit()]

        #  Verify if cpf has 11 digits
        if len(cpf) != 11:
            return False

        # Verify if all the digits are the same
        # A cpf with all the same digits passes the validation but is invalid
        if cpf == cpf[::-1]:
            return False

        # Validate check digits
        for i in range(9, 11):
            value = sum((cpf[num] * ((i+1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != cpf[i]:
                return False
        return True

    def validate_phone(value):
        """Method to validate a phone"""
        rule = re.compile(r'(\(?\d{2}\)?\s)?(\d{4,5}\-\d{4})')
        if not rule.search(value):
            return False
        return True
