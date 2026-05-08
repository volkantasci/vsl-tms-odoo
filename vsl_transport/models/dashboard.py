from odoo import fields, models


class VslDashboard(models.TransientModel):
    _name = "vsl.dashboard"
    _description = "Transport Dashboard"

    total_orders = fields.Integer(string="Total Orders", compute="_compute_metrics")
    open_orders = fields.Integer(string="Open Orders", compute="_compute_metrics")
    loading_orders = fields.Integer(string="Loading", compute="_compute_metrics")
    in_transit_orders = fields.Integer(string="In Transit", compute="_compute_metrics")
    delivered_month = fields.Integer(string="Delivered (This Month)", compute="_compute_metrics")
    cancelled_month = fields.Integer(string="Cancelled (This Month)", compute="_compute_metrics")

    total_vehicles = fields.Integer(string="Total Vehicles", compute="_compute_metrics")
    available_vehicles = fields.Integer(string="Available", compute="_compute_metrics")
    on_route_vehicles = fields.Integer(string="On Route", compute="_compute_metrics")
    maintenance_vehicles = fields.Integer(string="Maintenance", compute="_compute_metrics")

    total_drivers = fields.Integer(string="Total Drivers", compute="_compute_metrics")
    active_drivers = fields.Integer(string="Active Drivers", compute="_compute_metrics")
    on_leave_drivers = fields.Integer(string="On Leave", compute="_compute_metrics")

    total_carriers = fields.Integer(string="Carriers / Suppliers", compute="_compute_metrics")
    total_locations = fields.Integer(string="Locations", compute="_compute_metrics")

    def _compute_metrics(self):
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)

        orders = self.env["vsl.transport.order"]
        self.total_orders = orders.search_count([])
        self.open_orders = orders.search_count([("state", "in", ("open", "assigned"))])
        self.loading_orders = orders.search_count([("state", "=", "loading")])
        self.in_transit_orders = orders.search_count([("state", "=", "in_transit")])
        self.delivered_month = orders.search_count([
            ("state", "=", "delivered"),
            ("actual_date_end", ">=", month_start),
        ])
        self.cancelled_month = orders.search_count([
            ("state", "=", "cancelled"),
            ("write_date", ">=", month_start),
        ])

        vehicles = self.env["fleet.vehicle"]
        self.total_vehicles = vehicles.search_count([])
        self.available_vehicles = vehicles.search_count([("vsl_transport_status", "=", "available")])
        self.on_route_vehicles = vehicles.search_count([("vsl_transport_status", "=", "on_route")])
        self.maintenance_vehicles = vehicles.search_count([("vsl_transport_status", "=", "maintenance")])

        drivers = self.env["vsl.driver.profile"]
        self.total_drivers = drivers.search_count([])
        self.active_drivers = drivers.search_count([("status", "=", "active")])
        self.on_leave_drivers = drivers.search_count([("status", "=", "on_leave")])

        self.total_carriers = self.env["res.partner"].search_count([("is_carrier", "=", True)])
        self.total_locations = self.env["vsl.location"].search_count([])
