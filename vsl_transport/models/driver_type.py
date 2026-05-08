from odoo import fields, models


class VslDriverType(models.Model):
    _name = "vsl.driver.type"
    _description = "Driver Type"
    _order = "name"

    name = fields.Char(string="Driver Type", required=True, translate=True)
