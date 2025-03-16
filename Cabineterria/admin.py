from django.contrib import admin
from .models import CabinetModel, Question, Answers

class AnswerInline(admin.TabularInline):
    model = Answers
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(CabinetModel)
admin.site.register(Question, QuestionAdmin)
