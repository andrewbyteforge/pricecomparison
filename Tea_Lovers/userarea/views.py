from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from interface.forms import RegisterUserForm
from django.contrib.auth.decorators import login_required
import sys
from loggingapp.custom_logging import Logger

# create an instance of the logger which is at loggingapp.custom_logging
log = Logger().logger

# ********************************THIS IS THE LOGIN**************
def login_user(request): 
    """
    This function is used to handle the user login request and return a response accordingly.
    
    Params:
    None
    
    Raises:
    Exception : If any exception occurs during execution of this method
    
    Returns:
    A HttpResponse object with either a success message or an error message.
    """
    # Check if user is already authenticated
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("/products/")  # Redirect to a suitable page        
    try:        
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']        
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, "You need to enter your details")
                return redirect("/products/")  # Redirect to a success page.
            else:
                messages.error(request, "There was an error with your login. Please try again")
                return render('login')
        else:
            return render(request, 'userarea/login.html', {})
    except Exception as e:        
        log.error(f'Error logging in, please try again {e}')
        
# **************************************************************




# ********************************THIS IS THE LOGOUT**************
def logout_user(request):
    """
    This function is used to handle the user logout request and return a response accordingly.
    
    Params:
    None
    
    Raises:
    Exception : If any exception occurs during execution of this method
    
    Returns:
    A HttpResponse object with either a success message or an error message.
    """
    try:
        logout(request)
        messages.success(request, ('You were logged out'))
        return redirect('login_user/')  # Use the URL name here
    except Exception as e:
        log.error(f'Error logging out, please try again {e}')
        
# **************************************************************




# ********************************THIS IS THE REGISTER USER**************
def register_user(request):
    """
    This function is used to handle the user registration request and return a response accordingly.
    
    Params:
    None
    
    Raises:    
    ValidationError : If there are validation errors while creating new User instance
    
    Returns:
    A HttpResponse object with either a success message or an error message.
    """
    try:
        if request.method == "POST":
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, ("Registration Successful!"))
                return redirect('login')  # Ensure this is the correct redirect
    except Exception as e:  
        log.error(f"Error creating new account, please try again {e}")
        form = RegisterUserForm()  # Re-instantiate the form in case of exception

    if request.method != "POST":
        form = RegisterUserForm()
    return render(request, 'userarea/register_user.html', {'form': form})        
        
# **************************************************************