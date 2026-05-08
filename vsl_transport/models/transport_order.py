from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VslTransportOrder(models.Model):
    _name = "vsl.transport.order"
    _description = "Transport Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "create_date desc"

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        tracking=True,
        index=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("assigned", "Assigned"),
            ("loading", "Loading"),
            ("in_transit", "In Transit"),
            ("delivered", "Delivered"),
            ("invoiced", "Invoiced"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
        copy=False,
        index=True,
    )
    planned_date_start = fields.Datetime(string="Planned Start", tracking=True)
    planned_date_end = fields.Datetime(string="Planned End", tracking=True)
    actual_date_start = fields.Datetime(string="Actual Start", readonly=True)
    actual_date_end = fields.Datetime(string="Actual End", readonly=True)
    amount_total = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    notes = fields.Text(string="Notes")
    stop_ids = fields.One2many(
        "vsl.transport.stop",
        "order_id",
        string="Stops",
        copy=True,
    )
    assignment_ids = fields.One2many(
        "vsl.vehicle.assignment",
        "order_id",
        string="Assignments",
    )
    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        copy=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "vsl.transport.order"
                ) or _("New")
        return super().create(vals_list)

    def action_confirm(self):
        for order in self:
            if order.state != "draft":
                raise UserError(_("Only draft orders can be confirmed."))
            if not order.customer_id:
                raise UserError(_("Please set a customer before confirming."))
            load_stops = order.stop_ids.filtered(lambda s: s.stop_type == "loading")
            unload_stops = order.stop_ids.filtered(lambda s: s.stop_type == "unloading")
            if not load_stops or not unload_stops:
                raise UserError(
                    _("At least one loading and one unloading stop is required.")
                )
            order.state = "open"

    def action_assign(self):
        for order in self:
            if order.state != "open":
                raise UserError(_("Only open orders can be assigned."))
            if not order.assignment_ids:
                raise UserError(
                    _("Please create a vehicle assignment before assigning.")
                )
            valid_assignments = order.assignment_ids.filtered(
                lambda a: a.state == "assigned"
            )
            if not valid_assignments:
                raise UserError(
                    _("No active assignment found. All assignments must be in 'Assigned' state.")
                )
            order.state = "assigned"

    def action_cancel(self):
        for order in self:
            if order.state == "invoiced":
                raise UserError(_("Invoiced orders cannot be cancelled."))
            order.state = "cancelled"

    def action_start_loading(self):
        for order in self:
            if order.state != "assigned":
                raise UserError(_("Only assigned orders can start loading."))
            if not order.assignment_ids:
                raise UserError(
                    _("Please assign a vehicle and driver before starting loading.")
                )
            active_assignments = order.assignment_ids.filtered(lambda a: a.state == "assigned")
            if not active_assignments:
                raise UserError(
                    _("No active assignment found. All assignments must be in 'Assigned' state.")
                )
            order.actual_date_start = fields.Datetime.now()
            order.state = "loading"

    def action_depart(self):
        for order in self:
            if order.state != "loading":
                raise UserError(_("Only loading orders can depart."))
            load_stops = order.stop_ids.filtered(lambda s: s.stop_type == "loading")
            unfinished = [s for s in load_stops if s.state != "done"]
            if unfinished:
                raise UserError(
                    _("All loading stops must be completed before departure.")
                )
            valid_assignment = order.assignment_ids.filtered(
                lambda a: a.state == "assigned"
            )
            if valid_assignment:
                valid_assignment.state = "departed"
            order.state = "in_transit"

    def action_deliver(self):
        for order in self:
            if order.state != "in_transit":
                raise UserError(_("Only in-transit orders can be delivered."))
            unload_stops = order.stop_ids.filtered(lambda s: s.stop_type == "unloading")
            unfinished = [s for s in unload_stops if s.state != "done"]
            if unfinished:
                raise UserError(
                    _("All unloading stops must be completed before delivery.")
                )
            order.actual_date_end = fields.Datetime.now()
            order.state = "delivered"

    def action_view_history(self):
        self.ensure_one()
        first_stop = self.stop_ids.filtered(lambda s: s.stop_type == "loading")[:1]
        last_stop = self.stop_ids.filtered(lambda s: s.stop_type == "unloading")[-1:]
        domain = [("id", "!=", self.id)]
        if first_stop and last_stop:
            domain += [
                ("stop_ids.address_id", "=", first_stop.address_id.id),
                ("stop_ids.stop_type", "=", "loading"),
            ]
            domain += [
                ("stop_ids.address_id", "=", last_stop.address_id.id),
                ("stop_ids.stop_type", "=", "unloading"),
            ]
        return {
            "type": "ir.actions.act_window",
            "name": _("Previous Orders on Same Route"),
            "res_model": "vsl.transport.order",
            "view_mode": "tree,form",
            "domain": domain,
            "target": "current",
        }

    @api.constrains("state", "assignment_ids")
    def _check_assignment_for_assigned(self):
        for order in self:
            if order.state == "assigned" and not order.assignment_ids:
                raise UserError(
                    _("Order cannot be in 'Assigned' state without an assignment.")
                )
