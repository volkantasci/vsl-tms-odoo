from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError


class VslTransportAssignmentWizard(models.TransientModel):
    _name = "vsl.transport.assignment.wizard"
    _description = "Transport Assignment Wizard"

    order_id = fields.Many2one(
        "vsl.transport.order",
        string="Transport Order",
        required=True,
        readonly=True,
    )
    driver_id = fields.Many2one(
        "res.partner",
        string="Tedarikçi / Şoför",
        required=True,
        domain=[("parent_id", "=", False)],
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Araç (Filo)",
    )
    external_vehicle_plate = fields.Char(
        string="Harici Plaka",
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get("active_id"):
            order = self.env["vsl.transport.order"].browse(
                self.env.context["active_id"]
            )
            defaults["order_id"] = order.id
            if order.assignment_ids:
                assignment = order.assignment_ids[0]
                defaults["driver_id"] = assignment.driver_id.id
                defaults["vehicle_id"] = assignment.vehicle_id.id
                defaults["external_vehicle_plate"] = assignment.external_vehicle_plate
        return defaults

    def action_assign(self):
        self.ensure_one()
        order = self.order_id

        if order.state not in ("open",):
            raise UserError(_("Only open orders can be assigned."))

        if not self.driver_id:
            raise UserError(_("Please select a driver/carrier."))

        if not self.vehicle_id and not self.external_vehicle_plate:
            raise UserError(_("Please select a vehicle or enter an external plate."))

        if len(order.assignment_ids) >= 2:
            raise UserError(_("A transport order can have at most 2 vehicle assignments."))

        # Check vehicle type compatibility
        if order.requested_vehicle_type_id and self.vehicle_id:
            assigned_type = self.vehicle_id.vsl_vehicle_type_id
            if assigned_type and assigned_type != order.requested_vehicle_type_id:
                _logger.warning(
                    "Vehicle type mismatch for order %s: requested %s, assigned %s",
                    order.name,
                    order.requested_vehicle_type_id.name,
                    assigned_type.name,
                )

        assignment_vals = {
            "order_id": order.id,
            "driver_id": self.driver_id.id,
            "vehicle_id": self.vehicle_id.id if self.vehicle_id else False,
            "external_vehicle_plate": self.external_vehicle_plate or False,
            "assignment_date": fields.Datetime.now(),
            "state": "assigned",
        }

        self.env["vsl.vehicle.assignment"].create(assignment_vals)

        order.state = "assigned"

        return {"type": "ir.actions.act_window_close"}