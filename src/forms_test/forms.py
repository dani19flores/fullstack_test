from django import forms

OPTION_CHOICES = [
    ('option1', 'Option 1'),
    ('option2', 'Option 2'),
    ('option3', 'Option 3'),
]

RADIO_CHOICES = [
    ('radio1', 'Radio 1'),
    ('radio2', 'Radio 2'),
    ('radio3', 'Radio 3'),
]

class TestForm(forms.Form):
    date = forms.DateField(label='Enter a date', widget=forms.SelectDateWidget())
    some_text = forms.CharField(label='Ingresa un texto:', max_length=100, widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))
    bolean = forms.BooleanField(label='Check this box', required=False, initial=True)
    integer = forms.IntegerField(label='Enter a number', min_value=0, max_value=100)
    email = forms.EmailField(label='Enter your email')
    option = forms.ChoiceField(label='Choose an option', choices=OPTION_CHOICES, widget=forms.Select)
    radio_option = forms.ChoiceField(label='Choose one', choices=RADIO_CHOICES, widget=forms.RadioSelect)
    checkbox = forms.MultipleChoiceField(label='Select multiple options', choices=OPTION_CHOICES, widget=forms.CheckboxSelectMultiple)

    def clean_integer(self, *args, **kwargs):
        integer = self.cleaned_data.get('integer')
        if integer > 100:
            raise forms.ValidationError('El número debe ser menor o igual a 100.')
        return integer

    def clean_some_text(self, *args, **kwargs):
        some_text = self.cleaned_data.get('some_text')
        if len(some_text) < 10:
            raise forms.ValidationError('El texto debe tener más de 10 caracteres.')
        return some_text