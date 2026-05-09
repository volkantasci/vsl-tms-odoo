from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    vsl_vehicle_type_id = fields.Many2one(
        "vsl.vehicle.type",
        string="Araç Tipi",
    )
    vsl_trailer_class_id = fields.Many2one(
        "vsl.vehicle.trailer.class",
        string="Dorse Sınıfı",
    )
    vsl_case_type_id = fields.Many2one(
        "vsl.vehicle.case.type",
        string="Kasa Tipi",
    )
    vsl_pass_system_id = fields.Many2one(
        "vsl.vehicle.pass.system",
        string="Geçiş Sistemi",
    )
    vsl_ownership_id = fields.Many2one(
        "vsl.vehicle.ownership",
        string="Sahiplik Durumu",
    )
    vsl_capacity = fields.Float(string="Kapasite (ton)")
    vsl_transport_status = fields.Selection(
        [
            ("available", "Müsait"),
            ("on_route", "Yolda"),
            ("maintenance", "Bakımda"),
        ],
        string="Taşımacılık Durumu",
        default="available",
    )
    vsl_document_ids = fields.One2many(
        "vsl.vehicle.document",
        "vehicle_id",
        string="Evraklar",
    )
