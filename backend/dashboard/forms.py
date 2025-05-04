from django import forms
from .models import NutrientProgress


class NutrientProgressForm(forms.ModelForm):
    class Meta:
        model = NutrientProgress
        fields = ['current_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_amount'].widget.attrs.update({
            'class': 'form-control nutrient-progress-input',
            'min': '0',
            'max': self.instance.nutrient.target_amount if self.instance and self.instance.nutrient else 100,
            'step': '0.1',
        })
