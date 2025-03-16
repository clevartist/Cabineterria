from django.db import models
from django.contrib.auth.models import User

class CabinetModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    requires_questions = models.BooleanField(default=False)
    requires_questions_remember = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    def get_children_recursive(self):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'children': []
        }

        for child in self.children.all():
            result['children'].append(child.get_children_recursive())
        return result


    def get_path(self):
        """Generate cabinet URL path from hierarchy"""
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.parent
        return '/'.join(path)



class Question(models.Model):
    cabinet = models.ForeignKey(CabinetModel, on_delete=models.CASCADE, related_name="questions")
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title



class Answers(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    title = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question'], condition=models.Q(is_correct=True), name="unique_correct_choice")
        ]


class UserCabinetStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cabinet = models.ForeignKey(CabinetModel, on_delete=models.CASCADE)
    locked = models.BooleanField(default=True)

    class Meta:
        unique_together=('user', 'cabinet')
    
    def __str__(self):
        return f"{self.user.username} : {self.cabinet.name} -> {"LOCKED" if self.locked else "UNLOCKED"}"