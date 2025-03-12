from django import forms
from .models import CabinetModel, Answers, Question
from django.contrib.auth.models import User

class CabinetForm(forms.ModelForm):
    class Meta:
        model = CabinetModel
        fields = ['name', 'description', 'requires_questions']

class AnswerForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        self.question = question

        answers = [(answer.id, answer.title)for answer in question.answers.all()]
        self.fields['answers'] = forms.ChoiceField(
            choices=answers,
            widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
            label = question.title
        )
    
    def clean_answer(self):
        answer_id = self.cleaned_data['answer']
        answer = Answers.objects.get(id=answer_id)
        return answer

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        help_texts = {
            'username': None,
        }

class SignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        help_texts = {
            'username': None,
        }
    
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")
        
        return username
