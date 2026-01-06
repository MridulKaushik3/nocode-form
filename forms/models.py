from django.db import models
from django.contrib.auth.models import User

FIELD_TYPES = [
    ('text', 'Text'),
    ('textarea', 'Textarea'),
    ('select', 'Dropdown'),
    ('radio', 'Radio'),
    ('checkbox', 'Checkbox'),
]

class Form(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forms',default=1)

    def __str__(self):
        return self.title


class FormField(models.Model):
    form = models.ForeignKey(Form, related_name='fields', on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    options = models.TextField(blank=True, help_text="Comma separated options")
    required = models.BooleanField(default=False)

    def get_options(self):
        return [opt.strip() for opt in self.options.split(',') if opt.strip()]

    def __str__(self):
        return self.label


class FormResponse(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)


class FieldResponse(models.Model):
    response = models.ForeignKey(FormResponse, related_name='answers', on_delete=models.CASCADE)
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    value = models.TextField()