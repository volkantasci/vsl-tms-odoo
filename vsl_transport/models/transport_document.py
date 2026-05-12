from odoo import api, fields, models


class VslTransportDocument(models.Model):
    _name = "vsl.transport.document"
    _description = "Transport Order Document"
    _rec_name = "doc_type_id"
    _order = "expiry_date asc nulls last"

    order_id = fields.Many2one(
        "vsl.transport.order",
        string="Transport Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    doc_type_id = fields.Many2one(
        "vsl.transport.document.type",
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