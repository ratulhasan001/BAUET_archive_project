from django import forms


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = "checkbox"
            elif isinstance(widget, forms.FileInput):
                css = "file-input"
            elif isinstance(widget, forms.Select):
                css = "select"
            else:
                css = "input"
            widget.attrs["class"] = f"{css} {widget.attrs.get('class', '')}".strip()
