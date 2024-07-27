from odoo import fields

class ModelUtils:

    def get_selection_label(model, field_name, value):
        field = model._fields[field_name]
        if isinstance(field, fields.Selection):
            selection_dict = dict(field.selection)
            return selection_dict.get(value, value)
        return value