from odoo import fields, models


class VslTransportStop(models.Model):
    _name = "vsl.transport.stop"
    _description = "Transport Stop"
    _order = "sequence, id"

    order_id = fields.Many2one(
        "vsl.transport.order",
        string="Transport Order",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Sequence", default=10)
    stop_type = fields.Selection(
        [
            ("loading", "Loading"),
            ("unloading", "Unloading"),
        ],
        string="Stop Type",
        required=True,
    )
    address_id = fields.Many2one(
        "res.partner",
        string="Address",
        required=True,
        domain=[("is_company", "=", False)],
    )
    location_id = fields.Many2one("vsl.location", string="Location")
    planned_date = fields.Datetime(string="Planned Date")
    actual_date = fields.Datetime(string="Actual Date")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="pending",
        required=True,
    )
    line_ids = fields.One2many(
        "vsl.transport.stop.line",
        "stop_id",
        string="Stop Lines",
        copy=True,
    )
    notes = fields.Text(string="Notes")


class VslTransportStopLine(models.Model):
    _name = "vsl.transport.stop.line"
    _description = "Transport Stop Line"

    stop_id = fields.Many2one(
        "vsl.transport.stop",
        string="Stop",
        required=True,
        ondelete="cascade",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
    )
    product_desc = fields.Char(string="Product Description")
    quantity = fields.Float(string="Quantity")
    weight = fields.Float(string="Weight (kg)")
