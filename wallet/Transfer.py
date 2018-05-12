"""Script used to define the paystack Transaction class."""

from paystackapi.base import PayStackBase


class Transfer(PayStackBase):
    """docstring for Transaction."""

    @classmethod
    def create_recipient(cls, **kwargs):
        """
        Create Transfer recipient.

        Args:
            type: nuban,
            name: name of user,
            description: description ,
            account_number: 01000000010,
            bank_code: 044,
            currency: NGN,
            
        Returns:
            Json data from paystack API.
        """

        return cls().requests.post('transferrecipient', data=kwargs)

    @classmethod
    def transfer(cls, **kwargs):
        """
        Initialize Transfer.

        Args:
            source: where the money is transferred from,
            reason: description,
            amount:amount to be transferred,
            recipient: recipient's code
            
        Returns:
            Json data from paystack API.
        """

        return cls().requests.post('transfer', data=kwargs)
    
    
    @classmethod
    def finalize_transfer(cls, **kwargs):
        """
        Finalize Transfer.

        Args:
           transfer_code: transfer code from previous response,
           otp: otp
            
        Returns:
            Json data from paystack API.
        """

        return cls().requests.post('transfer/finalize_transfer', data=kwargs)
    
    
    @classmethod
    def resend_otp(cls, **kwargs):
        """
        Resend OTP for Transfer.

        Args:
           transfer_code: transfer code from previous response,
           reason: can be either resend_otp or transfer
            
        Returns:
            Json data from paystack API.
        """

        return cls().requests.post('transfer/resend_otp', data=kwargs)
    
    
class Miscellaneous(PayStackBase):
    """docstring for Miscellaneous."""

    @classmethod
    def resolve_account_number(cls, account_number, bank_code):
        """
        Resolve Account Number.

        Args:
            account_number: 01000000010,
            bank_code: 044,
            
        Returns:
            Json data from paystack API.
        """

        return cls().requests.get('bank/resolve?account_number={account_number}&bank_code={bank_code}'.format(**locals()))