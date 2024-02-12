from .models import SiteSettings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from interface.forms import RegisterUserForm

from loggingapp.custom_logging import Logger
from django.contrib.auth.models import User


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
        messages.warning(request, "You are already logged in.")
        return redirect("/products/")  # Redirect to a suitable page
    try:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back!")                
                return redirect('show_products') 
            else:
                messages.error(
                    request, "There was an error with your login. Please try again")
                return render(request, 'userarea/login.html', {})
        else:
            return render(request, 'userarea/login.html', {})
    except Exception as e:
        log.error(f'Error logging in, please try again {e}')
        return render(request, 'userarea/login.html', {})

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
# views.py


def register_user(request):
    user_count = User.objects.count()  # Actual number of users in the database
    site_settings = None  # Initialize site_settings variable

    try:
        if request.method == "POST":
            # Ensure that site_settings exists or create a new one
            site_settings = SiteSettings.objects.first()
            if not site_settings:
                site_settings = SiteSettings.objects.create(registered_users_count=user_count)
            else:
                # Synchronize the registered_users_count with the actual user count
                site_settings.registered_users_count = user_count
                site_settings.save()

            if site_settings.registered_users_count >= 3:
                messages.error(
                    request, "Registration limit reached. You cannot register at this time.")
                # Make sure to pass the correct template path
                return render(request, 'userarea/login.html', {})

            form = RegisterUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                user = authenticate(username=username, password=password)
                login(request, user)

                # Increment the registered users count
                if site_settings:  # Check if site_settings was successfully defined
                    site_settings.registered_users_count += 1
                    site_settings.save()

                messages.success(request, "Registration Successful!")
                return redirect('login')  # Ensure this is the correct redirect
        else:
            form = RegisterUserForm()
    except Exception as e:
        log.error(f"Error creating new account, please try again {e}")
        form = RegisterUserForm()  # Re-instantiate the form in case of exception

    # Return statement is now outside of the if-else block
    registration_limit_reached = site_settings.registered_users_count >= 3 if site_settings else False
    return render(request, 'userarea/register_user.html', {
        'form': form, 
        'user_count': user_count,
        'registration_limit_reached': registration_limit_reached
    })



# **************************************************************



def list_users(request):
    users = User.objects.all()  # Fetch all users
    return render(request, 'userarea/list_users.html', {'users': users})
