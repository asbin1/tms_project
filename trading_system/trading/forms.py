from django import forms
from .models import Trade, Stock

class TradeForm(forms.ModelForm):
    stock = forms.ModelChoiceField(
        queryset=Stock.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Trade
        fields = ['stock', 'trade_type', 'quantity']
        widgets = {
            'trade_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].label_from_instance = lambda obj: f"{obj.symbol} - {obj.name} (Rs.{obj.current_price})"