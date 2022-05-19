from django.shortcuts import render,redirect
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        username = request.POST['username']
        password = request.POST['password']        
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.profile.access_id = password
            user.save()
            u = authenticate(username=username, password=password)
            login(request,u)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'homepage.html', {'form': form})


def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'sign_in.html', {'error': 'Invalid Credentials'})    
    return render(request, 'sign_in.html')

        
def logout_user(request):
    logout(request) 
    return redirect('homepage')