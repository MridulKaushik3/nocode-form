from django.shortcuts import render, get_object_or_404, redirect
from .models import Form, FormResponse, FieldResponse
from django.contrib.auth.decorators import login_required
import csv
from django.http import HttpResponse
from .models import FormField
from django.shortcuts import get_object_or_404, redirect
from .models import Form, FormField

def home(request):
    forms = Form.objects.all()
    return render(request, 'home.html', {'forms': forms})


def fill_form(request, form_id):
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
    forms = Form.objects.all()
    return render(request, 'dashboard.html', {'forms': forms})


@login_required
def form_responses(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    responses = FormResponse.objects.filter(form=form).prefetch_related('answers__field')
    return render(request, 'responses.html', {
        'form': form,
        'responses': responses
    })


@login_required
def export_responses_csv(request, form_id):
    form = get_object_or_404(Form, id=form_id)
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
            form = Form.objects.create(title=title, description=description)
            return redirect('add_fields', form_id=form.id)

    return render(request, 'create_form.html')

from .models import FormField

@login_required
def add_fields(request, form_id):
    form = get_object_or_404(Form, id=form_id)

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
    return render(request, 'add_fields.html', {
        'form': form,
        'fields': fields
    })

@login_required
def duplicate_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)

    new_form = Form.objects.create(
        title=form.title + " (Copy)",
        description=form.description
    )

    for field in form.fields.all():
        FormField.objects.create(
            form=new_form,
            label=field.label,
            field_type=field.field_type,
            options=field.options,
            required=field.required
        )

    return redirect('dashboard')

@login_required
def delete_form(request, form_id):
    form = get_object_or_404(Form, id=form_id)
    form.delete()
    return redirect('dashboard')
