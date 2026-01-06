from django.shortcuts import render, get_object_or_404, redirect
from .models import Form, FormResponse, FieldResponse, FormField
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
import csv


def register(request):
    """Custom registration view matching register.html template"""
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        # Basic validation
        if not username or not email or not password or not password2:
            messages.error(request, "All fields are required.")
            return render(request, 'register.html')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'register.html')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Auto-login after registration
        login(request, user)
        messages.success(request, "Registration successful! You are now logged in.")
        return redirect('dashboard')

    return render(request, 'register.html')


def home(request):
    """Public view - shows all forms"""
    forms = Form.objects.all()
    return render(request, 'home.html', {'forms': forms})

@login_required
def fill_form(request, form_id):
    """Public view - anyone can fill any form"""
    form = get_object_or_404(Form, id=form_id)

    if request.method == "POST":
        response = FormResponse.objects.create(form=form)

        for field in form.fields.all():
            value = request.POST.get(str(field.id))
            if value:
                FieldResponse.objects.create(
                    response=response,
                    field=field,
                    value=value
                )

        return render(request, 'success.html', {'form': form})

    return render(request, 'fill_form.html', {'form': form})


@login_required
def dashboard(request):
    """Admin dashboard - shows only user's own forms"""
    forms = Form.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'forms': forms})


@login_required
def form_responses(request, form_id):
    """View responses - only for forms created by the user"""
    form = get_object_or_404(Form, id=form_id)

    if form.created_by != request.user:
        messages.error(request, "You don't have permission to view this form's responses.")
        return redirect('dashboard')

    responses = FormResponse.objects.filter(form=form).prefetch_related('answers__field')
    return render(request, 'responses.html', {'form': form, 'responses': responses})


@login_required
def export_responses_csv(request, form_id):
    """Export CSV - only for forms created by the user"""
    form = get_object_or_404(Form, id=form_id)

    if form.created_by != request.user:
        messages.error(request, "You don't have permission to export this form's responses.")
        return redirect('dashboard')

    responses = FormResponse.objects.filter(form=form).prefetch_related('answers__field')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{form.title}_responses.csv"'

    writer = csv.writer(response)

    # Header
    headers = ['Submission Time'] + [field.label for field in form.fields.all()]
    writer.writerow(headers)

    # Data rows
    for resp in responses:
        row = [resp.submitted_at]
        answers = {a.field.id: a.value for a in resp.answers.all()}
        for field in form.fields.all():
            row.append(answers.get(field.id, ''))
        writer.writerow(row)

    return response


@login_required
def create_form(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title:
            form = Form.objects.create(
                title=title,
                description=description,
                created_by=request.user
            )
            return redirect('add_fields', form_id=form.id)
    return render(request, 'create_form.html')


@login_required
def add_fields(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        messages.error(request, "You don't have permission to edit this form.")
        return redirect('dashboard')

    if request.method == "POST":
        label = request.POST.get('label')
        field_type = request.POST.get('field_type')
        options = request.POST.get('options', '')
        required = request.POST.get('required') == 'on'

        if label and field_type:
            FormField.objects.create(
                form=form,
                label=label,
                field_type=field_type,
                options=options,
                required=required
            )

    fields = form.fields.all()
    return render(request, 'add_fields.html', {'form': form, 'fields': fields})


@login_required
def edit_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        messages.error(request, "You don't have permission to edit this form.")
        return redirect('dashboard')

    if request.method == "POST":
        form.title = request.POST.get('title')
        form.description = request.POST.get('description')
        form.save()
        messages.success(request, "Form updated successfully.")
        return redirect('dashboard')

    return render(request, 'edit_form.html', {'form': form})


@login_required
def delete_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    if form.created_by != request.user:
        messages.error(request, "You don't have permission to delete this form.")
        return redirect('dashboard')

    form_title = form.title
    form.delete()
    messages.success(request, f"Form '{form_title}' has been deleted successfully.")
    return redirect('dashboard')


@login_required
def duplicate_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)

    new_form = Form.objects.create(
        title=form.title + " (Copy)",
        description=form.description,
        created_by=request.user
    )

    for field in form.fields.all():
        FormField.objects.create(
            form=new_form,
            label=field.label,
            field_type=field.field_type,
            options=field.options,
            required=field.required
        )

    messages.success(request, f"Form '{form.title}' has been duplicated successfully.")
    return redirect('dashboard')


@login_required
def delete_field(request, field_id):
    field = get_object_or_404(FormField, id=field_id)
    form = field.form

    if form.created_by != request.user:
        messages.error(request, "You don't have permission to edit this form.")
        return redirect('dashboard')

    field.delete()
    messages.success(request, "Field deleted successfully.")
    return redirect('add_fields', form_id=form.id)

@login_required
def edit_field(request, field_id):
    field = get_object_or_404(FormField, id=field_id)
    form = field.form
    
    if form.created_by != request.user:
        messages.error(request, "You don't have permission to edit this field.")
        return redirect('add_fields', form_id=form.id)
    
    if request.method == "POST":
        field.label = request.POST.get("label")
        field.field_type = request.POST.get("field_type")
        field.options = request.POST.get("options", "")
        field.required = request.POST.get("required") == "on"
        field.save()
        messages.success(request, "Field updated successfully.")
        return redirect('add_fields', form_id=form.id)
    
    return render(request, 'edit_field.html', {'field': field})
