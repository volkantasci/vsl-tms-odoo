from odoo import api, fields, models


class VslDriverDocument(models.Model):
    _name = "vsl.driver.document"
    _description = "Driver Document"
    _rec_name = "doc_type"
    _order = "expiry_date asc nulls last"

    driver_id = fields.Many2one(
        "vsl.driver.profile",
        string="Driver",
        required=True,
        ondelete="cascade",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("driving_license", "Driving License"),
            ("src_certificate", "SRC Certificate"),
            ("psychotechnic", "Psychotechnic"),
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
    )
    notes = fields.Text(string="Notes")

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
