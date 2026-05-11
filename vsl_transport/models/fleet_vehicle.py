from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    vsl_vehicle_type_id = fields.Many2one(
        "vsl.vehicle.type",
        string="Vehicle Type",
    )
    vsl_trailer_class_id = fields.Many2one(
        "vsl.vehicle.trailer.class",
        string="Trailer Class",
    )
    vsl_case_type_id = fields.Many2one(
        "vsl.vehicle.case.type",
        string="Case Type",
    )
    vsl_pass_system_id = fields.Many2one(
        "vsl.vehicle.pass.system",
        string="Pass System",
    )
    vsl_ownership_id = fields.Many2one(
        "vsl.vehicle.ownership",
        string="Ownership Status",
    )
    vsl_capacity = fields.Float(string="Capacity (ton)")
    vsl_transport_status = fields.Selection(
        [
            ("available", "Available"),
            ("on_route", "On Route"),
            ("maintenance", "Maintenance"),
        ],
        string="Transport Status",
        default="available",
    )
    vsl_document_ids = fields.One2many(
        "vsl.vehicle.document",
        "vehicle_id",
        string="Documents",
    )
