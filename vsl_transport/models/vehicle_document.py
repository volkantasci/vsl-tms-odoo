from odoo import api, fields, models


class VslVehicleDocument(models.Model):
    _name = "vsl.vehicle.document"
    _description = "Vehicle Document"
    _rec_name = "doc_type"
    _order = "expiry_date asc nulls last"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        required=True,
        ondelete="cascade",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("insurance", "Insurance"),
            ("vehicle_registration", "Vehicle Registration"),
            ("inspection", "Inspection"),
            ("other", "Other"),
        ],
        string="Document Type",
        required=True,
    )
    datas = fields.Binary(string="File", attachment=True)
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
