from django import forms

class TestForm(forms.Form):
    some_text = forms.CharField(label='Search', max_length=100)
    bolean = forms.BooleanField(label='Check this box', required=False)
    integer = forms.IntegerField(label='Enter a number', min_value=0, max_value=100)
    email = forms.EmailField(label='Enter your email')

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