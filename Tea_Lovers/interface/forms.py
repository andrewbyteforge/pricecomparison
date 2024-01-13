from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms



class SearchForm(forms.Form):
    search_query = forms.CharField(label='Enter Product Names', max_length=200)




# This is the Registraion User page.

class RegisterUserForm(UserCreationForm):
    #These are not built into the authentication system
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'})) #attrs is the address of the class
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'})) #charfield is a string of text or characters
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'})) #class 'form-control' relates to bootstrap 

       

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2' )

    
    
    #To access Username, Password use the following. This allows us to designate the fields:
    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        #Has to be done this way as its built into the authentication system
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'