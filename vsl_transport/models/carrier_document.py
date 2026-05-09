from odoo import api, fields, models


class VslCarrierDocument(models.Model):
    _name = "vsl.carrier.document"
    _description = "Tedarikçi Evrakı"
    _rec_name = "doc_type"
    _order = "expiry_date asc nulls last"

    carrier_id = fields.Many2one(
        "res.partner",
        string="Tedarikçi",
        required=True,
        domain=[("parent_id", "=", False)],
        ondelete="cascade",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("driving_license", "Ehliyet"),
            ("vehicle_registration", "Ruhsat"),
            ("insurance", "Sigorta"),
            ("src_certificate", "SRC Belgesi"),
            ("other", "Diğer"),
        ],
        string="Evrak Tipi",
        required=True,
    )
    datas = fields.Binary(string="Dosya", attachment=False)
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

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
