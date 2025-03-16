from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CabinetModel, UserCabinetStatus
from .forms import CabinetForm, LoginForm, SignupForm, AnswerForm
from .utils import get_cabinet_from_path, validate_cabinet_access


class Home(View):
    def get(self, request):
        self._reset_question_cabinets(request.user)
        cabinets = CabinetModel.objects.filter(parent=None)
        return render(request, 'home.html', {'cabinets': cabinets})

    def _reset_question_cabinets(self, user):
        """Reset cabinets requiring questions and user lock status"""
        cabinets = CabinetModel.objects.filter(requires_questions_remember=True)
        cabinets.update(requires_questions=True)
        
        if user.is_authenticated:
            UserCabinetStatus.objects.filter(
                cabinet__in=cabinets, 
                user=user
            ).update(locked=True)
            
            existing = UserCabinetStatus.objects.filter(
                user=user, 
                cabinet__in=cabinets
            ).values_list('cabinet_id', flat=True)
            
            bulk_create = [
                UserCabinetStatus(user=user, cabinet=cab, locked=True)
                for cab in cabinets.exclude(id__in=existing)
            ]
            UserCabinetStatus.objects.bulk_create(bulk_create)


class CabinetView(View):
    def get(self, request, cabinet_path):
        cabinet = get_cabinet_from_path(cabinet_path)
        if not cabinet:
            return redirect('home')

        if not validate_cabinet_access(request.user, cabinet):
            return redirect('answer_questions', cabinet_id=cabinet.id)

        return render(request, 'cabinet.html', {
            'cabinet': cabinet,
            'children': cabinet.children.all(),
            'cabinet_path': cabinet_path
        })


@method_decorator(login_required, name='dispatch')
class BuildCabinet(View):
    def get(self, request, cabinet_path=None):
        parent = self._get_valid_parent(request.user, cabinet_path)
        if cabinet_path and not parent:
            return redirect('home')
        return render(request, 'buildCab.html', {'form': CabinetForm()})

    def post(self, request, cabinet_path=None):
        parent = self._get_valid_parent(request.user, cabinet_path)
        form = CabinetForm(request.POST)
        
        if form.is_valid():
            return self._handle_valid_form(form, request.user, parent)
        
        return render(request, 'buildCab.html', {'form': form})

    def _get_valid_parent(self, user, path):
        """Validate and return parent cabinet if path exists"""
        if not path:
            return None
            
        parent = get_cabinet_from_path(path)
        if parent and parent.owner != user:
            messages.error(self.request, "Permission denied")
            return None
        return parent

    def _handle_valid_form(self, form, user, parent):
        """Process valid cabinet form"""
        cabinet = form.save(commit=False)
        cabinet.owner = user
        cabinet.parent = parent
        cabinet.requires_questions_remember = cabinet.requires_questions
        cabinet.save()
        messages.success(self.request, "Cabinet created successfully")
        return redirect('home')


class Answer(View):
    def get(self, request, cabinet_id):
        cabinet = get_object_or_404(CabinetModel, id=cabinet_id)
        return self._handle_question_flow(request, cabinet)

    def post(self, request, cabinet_id):
        cabinet = get_object_or_404(CabinetModel, id=cabinet_id)
        form = AnswerForm(cabinet.questions.first(), request.POST)
        
        if not form.is_valid():
            return render(request, 'quiz.html', {'form': form, 'cabinet': cabinet})

        if form.cleaned_data['answer'].is_correct:
            self._unlock_cabinet(request.user, cabinet)
            return redirect('cabinet', cabinet_path=cabinet.get_path())
        
        messages.error(request, "Incorrect answer. Please try again.")
        return redirect('home')

    def _handle_question_flow(self, request, cabinet):
        """Handle question validation flow"""
        if not cabinet.requires_questions:
            return redirect('cabinet', cabinet_path=cabinet.get_path())
            
        if not cabinet.questions.exists():
            messages.error(request, "No questions available")
            return redirect('home')
            
        return render(request, 'quiz.html', {
            'form': AnswerForm(cabinet.questions.first()),
            'cabinet': cabinet
        })

    def _unlock_cabinet(self, user, cabinet):
        """Update or create user cabinet status"""
        UserCabinetStatus.objects.update_or_create(
            user=user,
            cabinet=cabinet,
            defaults={'locked': False}
        )


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
