from ynladmin.models import CostSetting
from gameplay.models import WeeklyJackPot, DailyJackPot
from django import forms


class CostSettingForm(forms.ModelForm):
    amount = forms.IntegerField(help_text="Amount", required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Amount(%)', 'max': '50'}))
    referal_percentage = forms.IntegerField(help_text="Amount", required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Amount(%)', 'max': '50'}))
    agent_percentage = forms.IntegerField(help_text="Amount", required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'required': 'required', 'placeholder': 'Amount(%)', 'max': '50'}))

    class Meta:
        model = CostSetting
        fields = ('amount', 'referal_percentage', 'agent_percentage')


class WeeklyJackpotForm(forms.ModelForm):
    class Meta:
        model = WeeklyJackPot
        fields = ('weekly_prize', 'grand_prize', 'consolation_prize', 'top_winner', 'consolation_winners', 'start_date',
                  'end_date')


class DailyJackPotForm(forms.ModelForm):
    class Meta:
        model = DailyJackPot
        fields = (
        'question', 'grand_prize', 'consolation_prize', 'top_winner', 'consolation_winners', 'amount', 'all_players')


class DailyJackPotEditForm(forms.ModelForm):
    class Meta:
        model = DailyJackPot
        fields = (
        'question', 'grand_prize', 'consolation_prize', 'top_winner', 'consolation_winners', 'amount', 'decision',
        'all_players')
