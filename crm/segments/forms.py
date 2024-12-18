from django import forms
from .models import Segment
from settings.models import Status, Tag


class SegmentForm(forms.ModelForm):
    class Meta:
        model = Segment
        fields = ['name', 'description', 'conditions', 'status_value', 'tag_value']

    # Dynamic fields with Tailwind classes
    status_value = forms.ModelMultipleChoiceField(
        queryset=Status.objects.all(),
        required=False,
    )

    tag_value = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conditions'].widget = forms.HiddenInput()
        self.fields['name'].widget.attrs.update({
           'class': 'form-select block w-full rounded border border-black p-2 mb-2',
            'style': 'background-color: #f5f5f5;',
            'placeholder': 'Enter Segment Name',
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-select block w-full rounded border border-black p-2 mb-2',
            'style': 'background-color: #f5f5f5;',
            'placeholder': 'Enter Description',
            'rows': '4'
        })
    def clean(self):
        cleaned_data = super().clean()
        conditions = cleaned_data.get('conditions')
        # Ensure conditions are JSON serializable
        try:
            if conditions:
                import json
                json.loads(conditions)
        except ValueError:
            raise forms.ValidationError("Conditions must be valid JSON.")
        return cleaned_data
