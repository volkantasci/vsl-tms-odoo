from odoo import api, fields, models


class VslVehicleDocument(models.Model):
    _name = "vsl.vehicle.document"
    _description = "Araç Evrakı"
    _rec_name = "doc_type"
    _order = "expiry_date asc nulls last"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Araç",
        required=True,
        ondelete="cascade",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("insurance", "Sigorta"),
            ("vehicle_registration", "Ruhsat"),
            ("inspection", "Muayene"),
            ("other", "Diğer"),
        ],
        string="Evrak Tipi",
        required=True,
    )
    datas = fields.Binary(string="Dosya", attachment=True)
    issue_date = fields.Date(string="Düzenlenme Tarihi")
    expiry_date = fields.Date(string="Son Geçerlilik Tarihi")
    state = fields.Selection(
        [
            ("valid", "Geçerli"),
            ("expired", "Süresi Doldu"),
        ],
        string="Durum",
        default="valid",
        compute="_compute_state",
    )
    notes = fields.Text(string="Notlar")

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
