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
    def get(self, request, cabinet_path):
        try:
            # Split the path into cabinet names
            cabinet_names = cabinet_path.split('/')
            print(f"CABINET_NAMES: {cabinet_names}")
            current_cabinet = None
            
            # Traverse through the path
            for name in cabinet_names:
                if current_cabinet is None:
                    current_cabinet = CabinetModel.objects.get(name=name, parent=None)
                    print(f"NAME: {name}")
                    print(f"CURRENT_CABINET: {current_cabinet}")
                else:
                    current_cabinet = CabinetModel.objects.get(name=name, parent=current_cabinet)
                    print(f"CURRENT_CABINET: {current_cabinet}")
            
            if current_cabinet is None:
                return redirect('home')
                
            context = {
                'cabinet': current_cabinet,
                'children': current_cabinet.children.all(),
                'cabinet_path': cabinet_path
            }
            return render(request, 'cabinet.html', context)
        except CabinetModel.DoesNotExist:
            print(f"Cabinet not found: {cabinet_path}")
            return redirect('home')


class BuildCabinet(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request, cabinet_path):
        form = CabinetForm()
        return render(request, 'buildCab.html', {'form': form})
    
    @method_decorator(login_required(login_url='login'))
    def post(self, request, cabinet_path):

        # deifining current cabinet...
        
        cabinet_names = cabinet_path.split('/')
        current_cabinet = None

        for name in cabinet_names:
            if current_cabinet is None:
                current_cabinet = CabinetModel.objects.get(name=name, parent=None)
            else:
                current_cabinet = CabinetModel.objects.get(name=name, parent=current_cabinet)
        
        # ...until here


        form = CabinetForm(request.POST)
        if form.is_valid():
            cabinet = form.save(commit=False)
            cabinet.owner = request.user
            cabinet.parent = current_cabinet
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