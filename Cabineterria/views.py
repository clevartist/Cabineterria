from django.shortcuts import render, redirect
from django.views import View
from .models import CabinetModel
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .forms import CabinetForm, LoginForm, SignupForm

class Home(View):
    def get(self, request):
        cabinets = CabinetModel.objects.filter(parent=None)
        return render(request, 'home.html', {'cabinets': cabinets})

class CabinetView(View):
    def get(self, request, pk):
        try:
            cab = CabinetModel.objects.get(id=pk)
            context = {
                'cabinet': cab,
                'children': cab.children.all()
            }
            return render(request, 'cabinet.html', context)
        except CabinetModel.DoesNotExist:
            return redirect('home')


class BuildCabinet(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        form = CabinetForm()
        return render(request, 'buildCab.html', {'form': form, 'cabinets': CabinetModel.objects.all()})
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request):
        form = CabinetForm(request.POST)
        if form.is_valid():
            cabinet = form.save(commit=False)
            cabinet.owner = request.user
            cabinet.save()
            return redirect('home')
        
        context = {
            'cabinets': CabinetModel.objects.all(),
            'form': form
        }
        return render(request, 'buildCab.html', context)


class Login(View):
    def get(self, request):
        err = False
        form = LoginForm()
        context = {
            'error': err,
            'form': form
        }
        return render(request, 'login.html', context)
    
    def post(self, request):
        form = LoginForm()
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        err = True
        context = {
            'error': err,
            'form': form
        }
        return render(request, 'login.html', context)

class Signup(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'signup.html', {'form': form})
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.create_user(username, email, password)
        user.save()
        login(request, user)
        return redirect('home')

class Logout(View):
    def post(self, request):
        logout(request)
        return redirect('home')