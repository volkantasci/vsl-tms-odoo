from odoo import fields, models


class VslLocation(models.Model):
    _name = "vsl.location"
    _description = "Location"
    _order = "name"

    name = fields.Char(string="Location Name", required=True, index=True)
    type = fields.Selection(
        [
            ("warehouse", "Warehouse"),
            ("port", "Port"),
            ("customs", "Customs"),
            ("factory", "Factory"),
            ("office", "Office"),
            ("other", "Other"),
        ],
        string="Location Type",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Address",
        help="Optional link to a partner address record.",
    )
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    country_id = fields.Many2one("res.country", string="Country")
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")
    contact_name = fields.Char(string="Contact Name")
    contact_phone = fields.Char(string="Contact Phone")
    features = fields.Text(string="Features")
    notes = fields.Text(string="Notes")
