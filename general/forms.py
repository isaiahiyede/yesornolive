from django import forms
from django.contrib.auth.models import User
from general.models import UserAccount, Event
from general.modelchoices import *
# from tinymce.models import HTMLField
from general.models import UserAccount, MessageCenterComment, Replies
from general.modelchoices import BANK, GENDER


class DateInput(forms.DateInput):
    input_type = 'date'


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=128, help_text="",
                               widget=forms.TextInput(attrs={'required': 'true', 'Placeholder': 'Username'}))
    email = forms.EmailField(max_length=128, help_text="",
                             widget=forms.EmailInput(attrs={'required': 'true', 'Placeholder': 'E-mail'}))
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserForm2(forms.ModelForm):
    username = forms.CharField(max_length=128, help_text="",
                               widget=forms.TextInput(attrs={'required': 'true', 'Placeholder': 'Username'}))
    first_name = forms.CharField(max_length=128, help_text="",
                               widget=forms.TextInput(attrs={'required': 'true', 'Placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=128, help_text="",
                               widget=forms.TextInput(attrs={'required': 'true', 'Placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=128, help_text="",
                             widget=forms.EmailInput(attrs={'required': 'true', 'Placeholder': 'E-mail'}))
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')


# forms.DateField(widget=forms.TextInput(attrs=
#                                 {
#                                     'class':'datepicker'
#                                 }))

class EventForm(forms.ModelForm):
    title = forms.CharField(help_text="Title", required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    category = forms.ChoiceField(choices=CATEGORY, error_messages={'required': 'Please select a category.'},
                                 widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))
    # start_date             = forms.DateField(required=True, widget=forms.DateInput(attrs={'class':'form-control id_date','required':'required'}))
    end_date = forms.DateField(required=True,
                               widget=forms.DateInput(attrs={'class': 'form-control id_date', 'required': 'required'}))
    # start_time             = forms.TimeField(required=True, widget=forms.TimeInput(attrs={'class':'form-control id_time','required':'required'}))
    end_time = forms.TimeField(required=True,
                               widget=forms.TimeInput(attrs={'class': 'form-control id_time', 'required': 'required'}))
    publish = forms.BooleanField(required=False)
    realityTV = forms.BooleanField(required=False)
    event_image = forms.ImageField(required=False, help_text='Photo', widget=forms.widgets.ClearableFileInput())
    event_msg_body = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))
    bet_question = forms.CharField(required=True,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}))
    not_validated_reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    estimated_wining = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    game_ratio = forms.ChoiceField(choices=RATIO, error_messages={'required': 'Please select a ratio.'},
                                   widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}))

    class Meta:
        model = Event
        fields = (
        'title', 'category', 'end_date', 'end_time', 'publish', 'event_image', 'event_msg_body', 'bet_question',
        'event_decision', 'event_id', 'decided', 'not_validated_reason', 'estimated_wining', 'game_ratio')


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('event_decision',)


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(help_text="First Name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'First Name', 'class': 'form-control', 'readonly': 'readonly'}))
    last_name = forms.CharField(help_text="Last Name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Last Name', 'class': 'form-control', 'readonly': 'readonly'}))
    username = forms.CharField(help_text="Username", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'class': 'form-control', 'readonly': 'readonly'}))
    email = forms.EmailField(help_text="E-Mail", required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Email Address', 'required': 'required', 'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)


class bankForm(forms.ModelForm):
    gender = forms.ChoiceField(help_text="gender", choices=GENDER, required=True,
                               widget=forms.Select(attrs={'required': 'required', 'class': 'form-control'}))
    dob = forms.DateField(help_text="Date of Birth", required=True, widget=forms.DateInput(
        attrs={'placeholder': 'mm/dd/yyyy', 'required': 'required', 'class': 'form-control id_dob', 'type': 'date'}))
    phone_number = forms.CharField(help_text="Phone Number", required=True, widget=forms.NumberInput(
        attrs={'placeholder': 'Phone Number (080 . . . )', 'required': 'required', 'class': 'form-control', "maxlength":"11"}))
    
    bank = forms.ChoiceField(help_text="Bank", choices=BANK, required=True, widget=forms.Select(
        attrs={'placeholder': 'Bank', 'class': 'form-control', 'required': 'required'}))
    
    class Meta:
        model = UserAccount
        fields = ('bank','gender','dob')


class UserAccountForm(forms.ModelForm):
    gender = forms.ChoiceField(help_text="gender", choices=GENDER, required=True,
                               widget=forms.Select(attrs={'required': 'required', 'class': 'form-control'}))
    phone_number = forms.CharField(help_text="Phone Number", required=True, widget=forms.NumberInput(
        attrs={'placeholder': 'Phone Number (080 . . . )', 'required': 'required', 'class': 'form-control', "maxlength":"11"}))
    dob = forms.DateField(help_text="Date of Birth", required=True, widget=forms.DateInput(
        attrs={'placeholder': 'mm/dd/yyyy', 'required': 'required', 'class': 'form-control id_dob', 'type': 'date'}))
    bank = forms.ChoiceField(help_text="Bank", choices=BANK, required=False, widget=forms.Select(
        attrs={'placeholder': 'Bank', 'class': 'form-control', 'readonly': 'readonly'}))
    account_number = forms.CharField(help_text="Account Number", required=True, widget=forms.NumberInput(
        attrs={'placeholder': 'Account Number','class': 'form-control', 'readonly': 'readonly'}))
    user_image = forms.ImageField(help_text="User Image", required=False,
                                  widget=forms.ClearableFileInput(attrs={'class': 'dropify'}))

    # referred_by     = forms.CharField(help_text="Referred By", required = False,widget=forms.TextInput(attrs={'placeholder':"Referral's Phone Number", 'class':'form-control'}))

    class Meta:
        model = UserAccount
        fields = ('bank', 'dob', 'account_number', 'gender', 'phone_number', 'user_image')

    def validate_bank_account_no(value):
        len_value = len(value)
        if (len_value < 10 or len_value > 10) and value.isdigit():
            raise ValidationError(
                'Please provide NUBAN 10 digits Bank Account Number. (It currently has %s)' % len_value)


class MessageCenterCommentForm(forms.ModelForm):
    message = forms.CharField(max_length=128, help_text="",
                              widget=forms.Textarea(attrs={'required': 'true', 'class': 'form-control'}))
    image_obj = forms.ImageField(required=False, help_text='Photo', widget=forms.widgets.ClearableFileInput())

    class Meta:
        model = MessageCenterComment
        fields = ('message', 'image_obj',)


class RepliesForm(forms.ModelForm):
    reply = forms.CharField(max_length=128, help_text="",
                            widget=forms.Textarea(attrs={'required': 'true', 'class': 'form-control'}))
    name = forms.CharField(help_text="Name", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Mame', 'required': 'required', 'class': 'form-control', 'readonly': 'readonly'}))
    email = forms.EmailField(help_text="E-Mail", required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'E-mail', 'required': 'required', 'class': 'form-control'}))

    class Meta:
        model = Replies
        fields = ('reply', 'name', 'email')
