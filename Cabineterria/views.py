from django.shortcuts import render, redirect
from django.views import View
from .models import CabinetModel, UserCabinetStatus
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .forms import CabinetForm, LoginForm, SignupForm, AnswerForm
from django.contrib import messages


class Home(View):
    def get(self, request):
        cabinets = CabinetModel.objects.filter(parent=None)

        all_cabinets = CabinetModel.objects.all()
        all_cabinets.requires_questions = True

        context = {'cabinets': cabinets, 'user': request.user}
        return render(request, 'home.html', context)


class CabinetView(View):
    def get(self, request, cabinet_path):
        try:
            cabinet_names = cabinet_path.split('/')
            current_cabinet = None
            for name in cabinet_names:
                if current_cabinet is None:
                    current_cabinet = CabinetModel.objects.get(name=name, parent=None)
                else:
                    current_cabinet = CabinetModel.objects.get(name=name, parent=current_cabinet)
            if current_cabinet is None:
                return redirect('home')
            # Check if the current user locked this cabinet.
            try:
                status = UserCabinetStatus.objects.get(user=request.user, cabinet=current_cabinet)
                user_locked = status.locked
            except UserCabinetStatus.DoesNotExist:
                user_locked = True

            if current_cabinet.requires_questions and user_locked:
                return redirect('answer_questions', cabinet_id=current_cabinet.id)
                
            context = {
                'cabinet': current_cabinet,
                'children': current_cabinet.children.all(),
                'cabinet_path': cabinet_path
            }
            return render(request, 'cabinet.html', context)
        except CabinetModel.DoesNotExist:
            return redirect('home')


class BuildCabinet(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request, cabinet_path=None):
        if cabinet_path:
            # Existing logic for building a subcabinet
            try:
                cabinet_names = cabinet_path.split('/')
                current_cabinet = None
                for name in cabinet_names:
                    if current_cabinet is None:
                        current_cabinet = CabinetModel.objects.get(
                            name=name, parent=None)
                    else:
                        current_cabinet = CabinetModel.objects.get(
                            name=name, parent=current_cabinet)
            except CabinetModel.DoesNotExist:
                messages.error(request, "Cabinet not found")
                return redirect('home')

            if request.user != current_cabinet.owner:
                messages.error(
                    request, "You do not have permission to build a subcabinet in a strange cabinet")
                return redirect('home')

            form = CabinetForm()
            return render(request, 'buildCab.html', {'form': form})
        else:
            # Logic for building a top-level cabinet (no parent)
            form = CabinetForm()
            return render(request, 'buildCab.html', {'form': form})

    @method_decorator(login_required(login_url='login'))
    def post(self, request, cabinet_path=None):
        if cabinet_path:
            try:
                cabinet_names = cabinet_path.split('/')
                current_cabinet = None
                for name in cabinet_names:
                    if current_cabinet is None:
                        current_cabinet = CabinetModel.objects.get(
                            name=name, parent=None)
                    else:
                        current_cabinet = CabinetModel.objects.get(
                            name=name, parent=current_cabinet)
            except CabinetModel.DoesNotExist:
                messages.error(request, "Cabinet not found")
                return redirect('home')

            form = CabinetForm(request.POST)
            if form.is_valid():
                cabinet = form.save(commit=False)
                cabinet.owner = request.user
                cabinet.parent = current_cabinet
                cabinet.save()
                return redirect('home')
            context = {'form': form}
            return render(request, 'buildCab.html', context)
        else:
            # For top-level cabinet building
            form = CabinetForm(request.POST)
            if form.is_valid():
                cabinet = form.save(commit=False)
                cabinet.owner = request.user
                # parent remains None for top-level cabinets
                cabinet.save()
                return redirect('home')
            return render(request, 'buildCab.html', {'form': form})


class Answer(View):
    def get(self, request, cabinet_id):
        cabinet = CabinetModel.objects.get(id=cabinet_id)
        if not cabinet.requires_questions:
            return redirect('cabinet', cabinet_path=cabinet.name)

        questions = cabinet.questions.all()
        if not questions:
            messages.error(request, "No questions available for this cabinet")
            return redirect('home')

        form = AnswerForm(questions.first())
        return render(request, 'quiz.html', {
            'form': form,
            'cabinet': cabinet
        })

    def post(self, request, cabinet_id):
        cabinet = CabinetModel.objects.get(id=cabinet_id)
        question = cabinet.questions.first()
        form = AnswerForm(question, request.POST)
    
        if form.is_valid():
            selected_answer = form.cleaned_data['answer']
            if selected_answer.is_correct:
                status, created = UserCabinetStatus.objects.get_or_create(
                    user = request.user,
                    cabinet = cabinet,
                    defaults={"locked": False}
                )
                if not created:
                    status.locked = False
                    status.save()

                # Build the full path for the cabinet
                path_parts = []
                current = cabinet
                while current:
                    path_parts.insert(0, current.name)
                    current = current.parent
                cabinet_path = '/'.join(path_parts)
                return redirect('cabinet', cabinet_path=cabinet_path)
            else:
                messages.error(request, "Incorrect answer. Please try again.")
                return redirect('home')
        
        return render(request, 'quiz.html', {
            'form': form,
            'cabinet': cabinet
    })


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


class Profile(View):
    @method_decorator(login_required(login_url='login'))
    def get(self, request, username):
        try:
            profile_user = User.objects.get(username__iexact=username)
            user_cabinets = CabinetModel.objects.filter(
                owner=profile_user, parent=None)

            context = {
                'profile_user': profile_user,
                'user_cabinets': user_cabinets,
                'is_owner': request.user == profile_user
            }
            return render(request, 'profile.html', context)
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('home')
