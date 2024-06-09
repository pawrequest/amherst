from datetime import date

from pydantic import BaseModel, EmailStr, PositiveInt


def generate_html_form(model: type[BaseModel], action: str) -> str:
    form_html = f'<form action="{action}" method="post">\n'
    for field, info in model.model_fields.items():
        form_html += f'<label for="{field}">{field.replace("_", " ").capitalize()}:</label>\n'
        input_type = 'text'
        if info.annotation == bool:
            input_type = 'checkbox'
        elif info.annotation in [int, PositiveInt]:
            input_type = 'number'
        elif info.annotation == EmailStr:
            input_type = 'email'
        elif info.annotation == date:
            input_type = 'date'
        # Other type checks can be added here
        form_html += (f'<input type="{input_type}" '
                      f'id="{field}" name="{field}" '
                      f'value="{{{{ {field} }}}}" {"checked" if input_type == "checkbox" and "{{{{  }}}}" else ""}>'
                      f'<br>\n')
    form_html += '<button type="submit">Submit</button>\n'
    form_html += '</form>\n'
    return form_html
