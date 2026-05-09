from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VslVehicleAssignment(models.Model):
    _name = "vsl.vehicle.assignment"
    _description = "Vehicle Assignment"
    _order = "assignment_date desc"

    order_id = fields.Many2one(
        "vsl.transport.order",
        string="Transport Order",
        required=True,
        ondelete="cascade",
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle (Fleet)",
    )
    external_vehicle_plate = fields.Char(
        string="External Vehicle Plate",
    )
    driver_id = fields.Many2one(
        "res.partner",
        string="Driver / Carrier",
        required=True,
        domain=[("is_carrier", "=", True)],
    )
    assignment_date = fields.Datetime(
        string="Assignment Date",
        default=fields.Datetime.now,
    )
    state = fields.Selection(
        [
            ("assigned", "Atandı"),
            ("departed", "Yola Çıktı"),
            ("completed", "Tamamlandı"),
            ("cancelled", "İptal"),
        ],
        string="Status",
        default="assigned",
        required=True,
    )

    @api.constrains("vehicle_id", "external_vehicle_plate")
    def _check_vehicle_info(self):
        for rec in self:
            if not rec.vehicle_id and not rec.external_vehicle_plate:
                raise ValidationError(
                    _("You must provide either a fleet vehicle or an external plate.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_vehicle_info()
        return records

    def write(self, vals):
        result = super().write(vals)
        if "vehicle_id" in vals or "external_vehicle_plate" in vals:
            self._check_vehicle_info()
        return result
