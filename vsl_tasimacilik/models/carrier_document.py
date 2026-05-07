from odoo import api, fields, models


class VslCarrierDocument(models.Model):
    _name = "vsl.carrier.document"
    _description = "Carrier Document"
    _rec_name = "doc_type"
    _order = "expiry_date asc"

    carrier_id = fields.Many2one(
        "res.partner",
        string="Carrier",
        required=True,
        domain=[("is_carrier", "=", True)],
        ondelete="cascade",
    )
    doc_type = fields.Selection(
        [
            ("driving_license", "Driving License"),
            ("vehicle_registration", "Vehicle Registration"),
            ("insurance", "Insurance"),
            ("src_certificate", "SRC Certificate"),
            ("other", "Other"),
        ],
        string="Document Type",
        required=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="File",
        required=True,
        ondelete="cascade",
    )
    issue_date = fields.Date(string="Issue Date")
    expiry_date = fields.Date(string="Expiry Date")
    state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expired", "Expired"),
        ],
        string="Status",
        default="valid",
        compute="_compute_state",
        store=True,
    )

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.today()
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
