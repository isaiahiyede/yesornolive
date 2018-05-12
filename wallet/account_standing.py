from django.contrib.auth.models import User
from general.models import UserAccount, WalletBalances
from wallet.models import Bank
from django.db.models import Q, Sum



def account_standing(request, user):
    if not request.user.is_authenticated():
        return 0,0
    
    #1. Added payments
    added_payments = Bank.objects.user_add_credit(user).aggregate(Sum('amount'))   
    if added_payments['amount__sum'] == None:
        total_added_payments = 0
    
    else:
        total_added_payments = added_payments['amount__sum']
    # print "total added payments", total_added_payments
    
    #2. Used payments
    used_payments = Bank.objects.user_remove_credit(user).aggregate(Sum('amount'))
    if used_payments['amount__sum'] == None:
        total_used_payments = 0
    
    else:
        total_used_payments = used_payments['amount__sum']
    # print "total used payments", total_used_payments
    
    #3. Refunded payments
    refunded_payments = Bank.objects.user_refund_credit(user).aggregate(Sum('amount'))
    if refunded_payments['amount__sum'] == None:
        total_refunded_payments = 0
    
    else:
        total_refunded_payments = refunded_payments['amount__sum']
    # print "total refunded payments", total_refunded_payments
    
    #4.  Transaction Fee
    transaction_fees = Bank.objects.user_remove_credit(user).aggregate(Sum('transaction_fee'))
    # print transaction_fees , "tfees"
    if transaction_fees['transaction_fee__sum'] == None:
        transaction_fees = 0
    else:
        transaction_fees = transaction_fees['transaction_fee__sum']
        # print "transaction_fees", transaction_fees
        
    #5. Calculate the user's credit standing as #1 - #4 - #2 + #3
    user_credit_amount = total_added_payments - (total_used_payments + transaction_fees) + total_refunded_payments
    # print "total balance", round(user_credit_amount, 2)
    return round(user_credit_amount, 2)


def bank_codes(bank):
    if bank == "ACCESS BANK":
        code = '044'
    elif bank == 'CITIBANK':
        code = "023"
    elif bank == 'DIAMOND BANK':
        code = "063"
    elif bank == 'ECOBANK':
        code = "050"
    elif bank == 'FIDELITY BANK':
        code = "070"
    elif bank == 'FIRST CITY MONUMENT BANK':
        code = "214"
    elif bank == 'FIRST BANK':
        code = "011"
    elif bank == 'GUARANTY TRUST BANK':
        code = "058"
    elif bank == 'HERITAGE BANK':
        code = "030"
    elif bank == 'KEYSTONE BANK':
        code = "082"
    elif bank == 'SKYE BANK':
        code = "076"
    elif bank == 'STANBIC IBTC':
        code = "221"
    elif bank == 'STANDARD CHARTERED BANK':
        code = "068"
    elif bank == 'STERLING BANK':
        code = "232"
    elif bank == 'UNION BANK OF NIGERIA':
        code = "032"
    elif bank == 'UNITED BANK OF AFRICA':
        code = "033"
    elif bank == 'UNITY BANK':
        code = "215"
    elif bank == 'WEMA BANK':
        code = "035"
    else:
        code = "057"
    return code


def account_standing_new(user):
    
    #1. Added payments
    added_payments = Bank.objects.user_add_credit(user).aggregate(Sum('amount'))   
    if added_payments['amount__sum'] == None:
        total_added_payments = 0
    
    else:
        total_added_payments = added_payments['amount__sum']
    # print "total added payments", total_added_payments
    
    #2. Used payments
    used_payments = Bank.objects.user_remove_credit(user).aggregate(Sum('amount'))
    if used_payments['amount__sum'] == None:
        total_used_payments = 0
    
    else:
        total_used_payments = used_payments['amount__sum']
    # print "total used payments", total_used_payments
    
    #3. Refunded payments
    refunded_payments = Bank.objects.user_refund_credit(user).aggregate(Sum('amount'))
    if refunded_payments['amount__sum'] == None:
        total_refunded_payments = 0
    
    else:
        total_refunded_payments = refunded_payments['amount__sum']
    # print "total refunded payments", total_refunded_payments
    
    #4. Transaction Fee
    transaction_fees = Bank.objects.user_remove_credit(user).aggregate(Sum('transaction_fee'))
    # print transaction_fees , "t-fees"
    if transaction_fees['transaction_fee__sum'] == None:
        transaction_fees = 0
    else:
        transaction_fees = transaction_fees['transaction_fee__sum']
        # print "transaction_fees", transaction_fees
        
    #5. Calculate the user's credit standing as #1 - #4 - #2 + #3
    user_credit_amount = total_added_payments - (total_used_payments + transaction_fees) + total_refunded_payments

    return round(user_credit_amount, 2)

