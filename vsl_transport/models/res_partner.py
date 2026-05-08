from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_carrier = fields.Boolean(
        string="Carrier / Supplier",
        help="This partner is a transport carrier/supplier.",
    )
    carrier_tax_office = fields.Char(string="Tax Office")
    carrier_tax_number = fields.Char(string="Tax Number")
    carrier_document_ids = fields.One2many(
        "vsl.carrier.document",
        "carrier_id",
        string="Documents",
    )
