from odoo import fields, models


class VslDriverProfile(models.Model):
    _name = "vsl.driver.profile"
    _description = "Driver Profile"
    _order = "partner_id"

    partner_id = fields.Many2one(
        "res.partner",
        string="Driver / Partner",
        required=True,
        ondelete="cascade",
        index=True,
    )
    driver_type_id = fields.Many2one(
        "vsl.driver.type",
        string="Driver Type",
    )
    license_number = fields.Char(string="License Number")
    license_class = fields.Selection(
        [
            ("B", "B"),
            ("C", "C"),
            ("E", "E"),
            ("CE", "CE"),
        ],
        string="License Class",
    )
    status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("on_leave", "On Leave"),
        ],
        string="Status",
        default="active",
        required=True,
    )
    phone = fields.Char(string="Phone")
    document_ids = fields.One2many(
        "vsl.driver.document",
        "driver_id",
        string="Documents",
    )
