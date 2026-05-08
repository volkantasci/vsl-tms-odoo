from odoo import fields, models


class VslVehicleType(models.Model):
    _name = "vsl.vehicle.type"
    _description = "Vehicle Type"
    _order = "name"

    name = fields.Char(string="Vehicle Type", required=True, translate=True)


class VslVehicleTrailerClass(models.Model):
    _name = "vsl.vehicle.trailer.class"
    _description = "Vehicle Trailer Class"
    _order = "name"

    name = fields.Char(string="Trailer Class", required=True, translate=True)


class VslVehicleCaseType(models.Model):
    _name = "vsl.vehicle.case.type"
    _description = "Vehicle Case Type"
    _order = "name"

    name = fields.Char(string="Case Type", required=True, translate=True)


class VslVehiclePassSystem(models.Model):
    _name = "vsl.vehicle.pass.system"
    _description = "Vehicle Pass System"
    _order = "name"

    name = fields.Char(string="Pass System", required=True, translate=True)


class VslVehicleOwnership(models.Model):
    _name = "vsl.vehicle.ownership"
    _description = "Vehicle Ownership Status"
    _order = "name"

    name = fields.Char(string="Ownership Status", required=True, translate=True)
