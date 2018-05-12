# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
from django.shortcuts import render, redirect
#from paystack.resource import TransactionResource
import string, random, ast, json
from general.models import UserAccount
from .models import Bank
from wallet.account_standing import account_standing, bank_codes, account_standing_new
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from wallet.Transfer import Transfer, Miscellaneous
from django.contrib import messages
from django.core.urlresolvers import reverse
from general.views import paginate_list
from gameplay.models import Gameplay
from django.contrib.auth.decorators import login_required,user_passes_test
from general.staff_access import *
from django.db.models import Q
from general.custom_functions import *
from django.http import JsonResponse
# Create your views here.


paystack_secret_key = "sk_live_af72e4a19446ff1ae9a5fe8e3d75028930e22f2b"
#paystack_secret_key = 'sk_test_3aecbec3433069bc0d7461895b17fe9c79369f24'  
paystack = Paystack(secret_key=paystack_secret_key)

@login_required
@user_passes_test(staff_check_for_gameplay, login_url='/backend/admin/all/events/', redirect_field_name=None)
def view_wallet(request):
    try:
        user = UserAccount.objects.get(user=request.user)
    except Exception as e :
        print "e", e
        user = None
    game    = Gameplay.objects.filter(user=user)
    balance = account_standing(request,request.user)
    try:
        if request.user.useraccount.trading_account:
            payment = Bank.objects.filter(~(Q(bank="DailyJackPot")),user=request.user)
        else:
            payment = Bank.objects.filter(user=request.user)
    except:
        payment = Bank.objects.filter(user=request.user)
    # query = request.GET.get('q')
    # if query:
    #     payment = payment.filter(
    #         Q(ref_no__iexact=query) |
    #         Q(status__icontains=query) |
    #         Q(message__icontains=query) 
    #         )
    wallet = payment
    
    return render(request, 'wallet/topup.html', {'balance':balance, 'wallet':wallet, 'user':user, 'game':game}) 


def generate_purchaseRef():
    rand = ''.join(
             [random.choice(
                 string.ascii_letters + string.digits) for n in range(16)]) 
    return rand

def purchase_ref():
    ref = generate_purchaseRef()#+ "|%s" %obj_id
    while Bank.objects.filter(ref_no = ref):
        ref = generate_purchaseRef() 
    # print "ref",ref
    return ref

@login_required
def main(request):
    try:
        useraccount = UserAccount.objects.get(user=request.user)
        if not useraccount.profile_updated:
            messages.info(request, 'Please Update your profile to top up your wallet')
            return redirect('general:profile')
    except Exception as e :
        print "e", e
        messages.info(request, 'Please Update your profile to top up your wallet')
        return redirect('general:profile')
    if request.method == "POST":
        bot_catcher = request.POST.get('bot_catcher')
        # print "bot_catcher",bot_catcher
        payment_method = request.POST.get('payment-method')
        if bot_catcher != "botty":
            return redirect(reverse('general:homepage'))

        try:    
            value = int(request.POST.get('amount'))
        except:
            messages.info(request, 'Invalid amount entered')
            return redirect('wallet:wallet')
        if payment_method == "bank":
            # print a
            random_ref = purchase_ref()
            bank_record = Bank.objects.create(user=request.user,txn_type="Add",amount=value, ref_no=random_ref,
                        created_at=timezone.now,date_created = timezone.now().date(), bank="BANK DEPOSIT", message="Wallet Top up Via Bank Deposit")
            bank_record.save()
            print bank_record
            payment = Bank.objects.filter(user=request.user)
            return render(request, 'general_snippets/bank_details.html', {'ref':random_ref, 'wallet':payment})
        if value > 20000:
            messages.info(request, 'You have exceeded the Top up Limit, Pls enter an amount less than 20,000')
            return redirect('wallet:wallet')
        # print "value", value
        amount = value * 100
        # print "amount", amount
        email = request.user.email
        
        #secret_key = 'sk_test_9fe140b2bf798accdc2aade269cac47bc2de7ecc'
        random_ref = purchase_ref()
        request.session['ref_no']= random_ref
        url = 'wallet:verify_payment'
        callback_url = request.build_absolute_uri(reverse(url))
        # print "callback-url", callback_url
        response = Transaction.initialize(reference=random_ref, 
                                  amount=amount, email=email, callback_url=callback_url)
        # print 'response:', response
        data = response.get('data')
        # print "data:", data
        authorization_code=data['access_code']
        # print "access_code", authorization_code
        url = data['authorization_url']
        # print 'url', url
        bank_record = Bank.objects.create(user=request.user,txn_type="Add",amount=value, ref_no=random_ref,
                        created_at=timezone.now,date_created = timezone.now().date())
        bank_record.save()
        return redirect(url)
        # response = Transaction.charge(reference=random_ref, 
        #                       authorization_code=authorization_code,
        #                       email=email,
        #                       amount=amount)
        # response_dict = Transaction.verify(reference=random_ref)
        # print "response_dict", response_dict
        #test_email = email
        #test_amount = amount
        #plan = 'Basic'
        # client = TransactionResource(secret_key, random_ref)
        # response = client.initialize(amount,email)
        # print"response",response
        # client.authorize() # Will open a browser window for client to enter card details
        # verify = client.verify() # Verify client credentials
        # print "verify", verify
        # print type(verify)
        # ref = verify.get('data')
        # print ref
        
        #client.charge(None,amount,email,random_ref)
        #print client.charge() # Charge an already exsiting client
    return render(request, 'wallet/topup.html')
   
   
def verify_payment(request):
    try:
        ref = request.session['ref_no']
    except:
        pass
        return redirect('wallet:wallet')
    response_dict = Transaction.verify(reference=ref)
    data = response_dict.get('data')
    print 'status', data['status']
    if data['status'] == 'success':
        status = "Successful"
    else:
        status = data['status']
    bank_record = Bank.objects.get(ref_no=ref)
    bank_record.status = status
    bank_record.message = data['gateway_response']
    bank_record.save()
    del request.session['ref_no']
    return redirect('wallet:wallet')


def create_recipient(request):
    # user = UserAccount.objects.get(user=request.user)
    # first_name = user.user.first_name
    # last_name = user.user.last_name
    # name = first_name + last_name
    # print name
    # description = "Withdrawal from YNLwallet"
    # account_number = user.account_number
    # bank_code = '058'
    # response = Transfer.create_recipient(type='nuban',name=name,description=description,
    #                                      account_number=account_number,bank_code=bank_code)
    # print "response:", response
    # data = response.get('data')
    # recipient_code = data['recipient_code']
    # amount = 10000
    # reason = "Withdrawal from YNLwallet"
    # transfer = Transfer.transfer(source='balance',reason=reason,amount=amount,recipient=recipient_code)
    # print "transfer:", transfer
    # verify = transfer.get('data')
    transfer_code = 'TRF_2o8n1mj1zogql3l'
    # magic number
    otp = 782008
    finalize = Transfer.finalize_transfer(transfer_code=transfer_code,otp=otp)
    return redirect('wallet:wallet')
    
@login_required
def cash_out(request):
    if request.method == "POST":
        bot_catcher = request.POST.get('bot_catcher')
        if bot_catcher != '':
            return redirect(reverse('general:homepage'))
        credit = account_standing(request, request.user)
        transaction_fee = 100
        # print "credit:", credit
        try:
            amount = float(request.POST.get('amount'))
        except Exception as e:
            print e
            messages.warning(request, 'Invalid input supplied')
            return redirect('wallet:wallet')

        if amount < 1000 :
            messages.warning(request, 'The minimum withdrawal limit is 1000 naira')
            return redirect('wallet:wallet')
        #print amount > credit
        if (amount + transaction_fee) > credit:
            messages.warning(request, "You do not have Sufficient money in your wallet!!!")
        else:
            ref = purchase_ref()
            user = UserAccount.objects.get(user=request.user)
            print user.bank
            try:
                bank = user.bank
            except:
                messages.info(request, "Please go to 'Account settings' in your account page and fill in your correct bank name")
                return redirect('wallet:wallet')

            bank_obj = Bank.objects.filter(user=request.user,txn_type="Remove",status="Transfer",bank=bank)
            if len(bank_obj) == 1:
                messages.info(request, "You already have a pending request, it will be processed within the next 24 hours!!!")
            else:
                if not bank == None:
                    cash_out = Bank.objects.create(user=request.user,txn_type="Remove",amount=amount, ref_no=ref,status="Transfer",
                                    created_at=timezone.now(), bank=bank,message="Cash out from YNLwallet to Bank", transaction_fee=transaction_fee)
                    cash_out.date_created = timezone.now().date()
                    cash_out.save()
                    messages.info(request, "Your request will be processed within the next 24 hours!!!")
                else:
                    messages.info(request, "Please check to make sure your bank details have been properly updated in your Account Settings")
    return redirect('wallet:wallet')


@login_required
def confirm_account(request):
    print request.GET
    try:
        account_number = request.GET.get("acc_number")
        acc_name = request.GET.get('acc_name')
        bank_code = str(bank_codes(request.GET.get('acc_name')))
        check_acc_no = Miscellaneous.resolve_account_number(account_number=account_number,bank_code=bank_code)
        print "check_acc_no", check_acc_no
        bank_details = check_acc_no.get('data')
        acc_name = bank_details['account_name'].split(' ') 
        last_name = " ".join(acc_name[1:])
        return JsonResponse({'account_name':acc_name, 'account_number':account_number,'first_name': acc_name[0].replace(',',''), 'last_name':last_name, 'check':'True'})
    except:
        return JsonResponse({'check':'False'})
    

def initiate_transfer(request):
    print "I started transfer"
    pk = request.GET.get('pk')
    record = Bank.objects.get(pk=pk)
    user = UserAccount.objects.get(user=record.user)
    account_standing = account_standing_new(user.user)
    if not account_standing > record.amount:
        record.status = "failed"
        record.save()
        return JsonResponse({'status':'failed'})
    first_name = user.user.first_name
    last_name = user.user.last_name
    name = first_name +"" + last_name
    #print name
    description = "Withdrawal from YNLwallet"
    account_number = str(user.account_number)
    bank_code = str(bank_codes(user.bank))
    if 'check' in request.GET:
        check_acc_no = Miscellaneous.resolve_account_number(account_number=account_number,bank_code=bank_code)
        # print "check_acc_no", check_acc_no
        bank_details = check_acc_no.get('data')
        print bank_details['account_name']
        acc_name = bank_details['account_name']
        return JsonResponse({'account_name': acc_name, 'check':'True'})

    # acc_name = bank_details['account_name'].replace(','," ")
    # print acc_name
    # account_name = acc_name.split()
    # print account_name
    # if first_name in account_name and last_name in account_name:
    #     print "Yes am here", a
    # else:
    #     print "No am not here", a
    
    if 'confirmed' in request.GET:
        response = Transfer.create_recipient(type='nuban',name=name,description=description,
                                             account_number=account_number,bank_code=bank_code)
        print "response:", response
        data = response.get('data')
        recipient_code = data['recipient_code']
        amount = record.amount * 100
        reason = "Withdrawal from YNLwallet"
        transfer = Transfer.transfer(source='balance',reason=reason,amount=amount,recipient=recipient_code)
        #print "transfer:", transfer
        verify = transfer.get('data')
        transfer_code = verify['transfer_code']
        return render(request, 'wallet/finalize_transfer.html', {'transfer_code':transfer_code, 'ref':record.ref_no})
   

def finalize_transfer(request):
    print "i got here"
    if request.method == "POST":
        otp = str(request.POST.get('otp'))
        transfer_code = str(request.POST.get('transfer_code'))
        ref = request.POST.get('ref')
        finalize = Transfer.finalize_transfer(transfer_code=transfer_code,otp=otp)
        print "finalize:", finalize
        verify= finalize.get('data')
        #print "verify", verify
        #verify_list = verify[0]
        status = verify['status']
        #print "status",status
        bank = Bank.objects.get(ref_no=ref)
        if status == "success":
            bank.status = "Successful"
        else:
            bank.status = "failed"
        bank.payment_gateway_tranx_id = transfer_code
        bank.save()
        if request.session.get('page_to'):
            page_to = str(request.session['page_to'])
            del request.session['page_to']
            return redirect(reverse('ynladmin:admin_pages', args=[page_to]))
        else:
            return redirect(reverse('ynladmin:admin_pages', args=['payment']))


def resend_otp(request):
    print "i got to dis place"
    transfer_code = str(request.GET.get('transfer_code'))
    reason = 'resend_otp'
    response = Transfer.resend_otp(transfer_code=transfer_code)
    print "response", response
    return response


def verify_pending(request,pk):
    bank_record = Bank.objects.get(id=pk)
    request.session['ref_no']= bank_record.ref_no
    return redirect(reverse('wallet:verify_payment'))


def approve_bankpay(request):
    pk = request.GET.get('pk')
    bank_record = Bank.objects.get(id=pk)
    bank_record.status = "Approved"
    bank_record.save()
    return redirect(reverse('ynladmin:admin_pages', args=['payment']))
    