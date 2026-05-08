# Voslo Gap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add all voslo-missing features to vsl_transport: driver profiles, vehicle reference data, location management, enhanced document models, fleet.vehicle extension, dashboard.

**Architecture:** New Python models follow existing vsl_transport patterns (standard models.Model, TransientModel for dashboard). Reference data models use minimal `_name`/`name` structure. Views follow Odoo 19 XML conventions (`<list>` not `<tree>`, no `attrs`/`states`).

**Tech Stack:** Odoo 19.0, Python 3, PostgreSQL, existing vsl_transport module

---

## Task 1: Vehicle Reference Data Models (5 models)

**Files:**
- Create: `vsl_transport/models/vehicle_reference.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create vehicle_reference.py**

```python
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
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import vehicle_reference` after the existing imports:

```python
from . import res_partner
from . import carrier_document
from . import transport_order
from . import transport_stop
from . import vehicle_assignment
from . import vehicle_reference
```

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/vehicle_reference.py vsl_transport/models/__init__.py
git commit -m "feat: add vehicle reference data models (type, trailer, case, pass, ownership)"
```

---

## Task 2: Driver Type Reference Model

**Files:**
- Create: `vsl_transport/models/driver_type.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create driver_type.py**

```python
from odoo import fields, models


class VslDriverType(models.Model):
    _name = "vsl.driver.type"
    _description = "Driver Type"
    _order = "name"

    name = fields.Char(string="Driver Type", required=True, translate=True)
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import driver_type` after the vehicle_reference import:

```python
from . import res_partner
from . import carrier_document
from . import transport_order
from . import transport_stop
from . import vehicle_assignment
from . import vehicle_reference
from . import driver_type
```

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/driver_type.py vsl_transport/models/__init__.py
git commit -m "feat: add driver type reference model"
```

---

## Task 3: Driver Document Model

**Files:**
- Create: `vsl_transport/models/driver_document.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create driver_document.py**

```python
from odoo import api, fields, models


class VslDriverDocument(models.Model):
    _name = "vsl.driver.document"
    _description = "Driver Document"
    _rec_name = "doc_type"
    _order = "expiry_date asc nulls last"

    driver_id = fields.Many2one(
        "vsl.driver.profile",
        string="Driver",
        required=True,
        ondelete="cascade",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("driving_license", "Driving License"),
            ("src_certificate", "SRC Certificate"),
            ("psychotechnic", "Psychotechnic"),
            ("other", "Other"),
        ],
        string="Document Type",
        required=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="File",
        required=True,
        ondelete="cascade",
    )
    issue_date = fields.Date(string="Issue Date")
    expiry_date = fields.Date(string="Expiry Date")
    state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expired", "Expired"),
        ],
        string="Status",
        default="valid",
        compute="_compute_state",
    )
    notes = fields.Text(string="Notes")

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import driver_document` after the driver_type import.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/driver_document.py vsl_transport/models/__init__.py
git commit -m "feat: add driver document model"
```

---

## Task 4: Driver Profile Model

**Files:**
- Create: `vsl_transport/models/driver_profile.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create driver_profile.py**

```python
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
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import driver_profile` after the driver_document import.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/driver_profile.py vsl_transport/models/__init__.py
git commit -m "feat: add driver profile model"
```

---

## Task 5: Vehicle Document Model

**Files:**
- Create: `vsl_transport/models/vehicle_document.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create vehicle_document.py**

```python
from odoo import api, fields, models


class VslVehicleDocument(models.Model):
    _name = "vsl.vehicle.document"
    _description = "Vehicle Document"
    _rec_name = "doc_type"
    _order = "expiry_date asc nulls last"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        required=True,
        ondelete="cascade",
        index=True,
    )
    doc_type = fields.Selection(
        [
            ("insurance", "Insurance"),
            ("vehicle_registration", "Vehicle Registration"),
            ("inspection", "Inspection"),
            ("other", "Other"),
        ],
        string="Document Type",
        required=True,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="File",
        required=True,
        ondelete="cascade",
    )
    issue_date = fields.Date(string="Issue Date")
    expiry_date = fields.Date(string="Expiry Date")
    state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expired", "Expired"),
        ],
        string="Status",
        default="valid",
        compute="_compute_state",
    )
    notes = fields.Text(string="Notes")

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import vehicle_document` after the driver_profile import.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/vehicle_document.py vsl_transport/models/__init__.py
git commit -m "feat: add vehicle document model"
```

---

## Task 6: fleet.vehicle Inheritance

**Files:**
- Create: `vsl_transport/models/fleet_vehicle.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create fleet_vehicle.py**

```python
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
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import fleet_vehicle` after the vehicle_document import.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/fleet_vehicle.py vsl_transport/models/__init__.py
git commit -m "feat: extend fleet.vehicle with transport-specific fields"
```

---

## Task 7: Location Model

**Files:**
- Create: `vsl_transport/models/location.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create location.py**

```python
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
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import location` after the fleet_vehicle import.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/location.py vsl_transport/models/__init__.py
git commit -m "feat: add location model with type, coordinates and contact info"
```

---

## Task 8: vsl.transport.stop Inheritance (location_id)

**Files:**
- Modify: `vsl_transport/models/transport_stop.py`

- [ ] **Step 1: Add location_id field to transport_stop.py**

Replace the file content with the updated version. The current file content is:

```python
from odoo import fields, models


class VslTransportStop(models.Model):
    _name = "vsl.transport.stop"
    _description = "Transport Stop"
    _order = "sequence, id"

    order_id = fields.Many2one("vsl.transport.order", string="Transport Order", required=True, ondelete="cascade")
    sequence = fields.Integer(string="Sequence", default=10)
    stop_type = fields.Selection(
        [("loading", "Yükleme"), ("unloading", "Boşaltma")],
        string="Stop Type",
        required=True,
    )
    address_id = fields.Many2one("res.partner", string="Address", required=True)
    planned_date = fields.Datetime(string="Planned Date")
    actual_date = fields.Datetime(string="Actual Date")
    state = fields.Selection(
        [("pending", "Beklemede"), ("done", "Tamamlandı"), ("cancelled", "İptal")],
        string="State",
        default="pending",
        required=True,
    )
    line_ids = fields.One2many("vsl.transport.stop.line", "stop_id", string="Stop Lines", copy=True)
    notes = fields.Text(string="Notes")


class VslTransportStopLine(models.Model):
    _name = "vsl.transport.stop.line"
    _description = "Transport Stop Line"

    stop_id = fields.Many2one("vsl.transport.stop", string="Stop", required=True, ondelete="cascade")
    customer_id = fields.Many2one("res.partner", string="Customer")
    product_desc = fields.Char(string="Product / Description")
    quantity = fields.Float(string="Quantity")
    weight = fields.Float(string="Weight (kg)")
```

Add `location_id` field to VslTransportStop:

```python
from odoo import fields, models


class VslTransportStop(models.Model):
    _name = "vsl.transport.stop"
    _description = "Transport Stop"
    _order = "sequence, id"

    order_id = fields.Many2one("vsl.transport.order", string="Transport Order", required=True, ondelete="cascade")
    sequence = fields.Integer(string="Sequence", default=10)
    stop_type = fields.Selection(
        [("loading", "Yükleme"), ("unloading", "Boşaltma")],
        string="Stop Type",
        required=True,
    )
    address_id = fields.Many2one("res.partner", string="Address", required=True)
    location_id = fields.Many2one("vsl.location", string="Location")
    planned_date = fields.Datetime(string="Planned Date")
    actual_date = fields.Datetime(string="Actual Date")
    state = fields.Selection(
        [("pending", "Beklemede"), ("done", "Tamamlandı"), ("cancelled", "İptal")],
        string="State",
        default="pending",
        required=True,
    )
    line_ids = fields.One2many("vsl.transport.stop.line", "stop_id", string="Stop Lines", copy=True)
    notes = fields.Text(string="Notes")


class VslTransportStopLine(models.Model):
    _name = "vsl.transport.stop.line"
    _description = "Transport Stop Line"

    stop_id = fields.Many2one("vsl.transport.stop", string="Stop", required=True, ondelete="cascade")
    customer_id = fields.Many2one("res.partner", string="Customer")
    product_desc = fields.Char(string="Product / Description")
    quantity = fields.Float(string="Quantity")
    weight = fields.Float(string="Weight (kg)")
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/models/transport_stop.py
git commit -m "feat: add location_id field to transport stop"
```

---

## Task 9: Dashboard Transient Model

**Files:**
- Create: `vsl_transport/models/dashboard.py`
- Modify: `vsl_transport/models/__init__.py`

- [ ] **Step 1: Create dashboard.py**

```python
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
```

- [ ] **Step 2: Update models/__init__.py**

Add `from . import dashboard` after the location import.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/models/dashboard.py vsl_transport/models/__init__.py
git commit -m "feat: add dashboard transient model with KPI metrics"
```

---

## Task 10: Reference Data Seed File

**Files:**
- Create: `vsl_transport/data/vsl_reference_data.xml`
- Modify: `vsl_transport/__manifest__.py`

- [ ] **Step 1: Create vsl_reference_data.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <record id="driver_type_supplier" model="vsl.driver.type">
            <field name="name">Tedarik</field>
        </record>
        <record id="driver_type_contracted" model="vsl.driver.type">
            <field name="name">Sozlesmeli</field>
        </record>
        <record id="driver_type_non_contracted" model="vsl.driver.type">
            <field name="name">Sozlesmesiz</field>
        </record>

        <record id="vehicle_type_kamyonet" model="vsl.vehicle.type">
            <field name="name">Kamyonet</field>
        </record>
        <record id="vehicle_type_6teker" model="vsl.vehicle.type">
            <field name="name">6 Teker</field>
        </record>
        <record id="vehicle_type_atego" model="vsl.vehicle.type">
            <field name="name">Atego</field>
        </record>
        <record id="vehicle_type_10teker" model="vsl.vehicle.type">
            <field name="name">10 Teker</field>
        </record>
        <record id="vehicle_type_40ayak" model="vsl.vehicle.type">
            <field name="name">40 Ayak</field>
        </record>
        <record id="vehicle_type_cekici" model="vsl.vehicle.type">
            <field name="name">Cekici</field>
        </record>
        <record id="vehicle_type_dorse" model="vsl.vehicle.type">
            <field name="name">Dorse</field>
        </record>
        <record id="vehicle_type_lowbed" model="vsl.vehicle.type">
            <field name="name">Lowbed</field>
        </record>
        <record id="vehicle_type_forklift" model="vsl.vehicle.type">
            <field name="name">Forklift</field>
        </record>
        <record id="vehicle_type_vinc" model="vsl.vehicle.type">
            <field name="name">Vinc</field>
        </record>

        <record id="trailer_class_tenteli" model="vsl.vehicle.trailer.class">
            <field name="name">Tenteli</field>
        </record>
        <record id="trailer_class_tentesiz" model="vsl.vehicle.trailer.class">
            <field name="name">Tentesiz</field>
        </record>

        <record id="case_type_acik" model="vsl.vehicle.case.type">
            <field name="name">Acik</field>
        </record>
        <record id="case_type_kapali" model="vsl.vehicle.case.type">
            <field name="name">Kapali</field>
        </record>
        <record id="case_type_frigo" model="vsl.vehicle.case.type">
            <field name="name">Frigo</field>
        </record>

        <record id="pass_system_ogs" model="vsl.vehicle.pass.system">
            <field name="name">OGS</field>
        </record>
        <record id="pass_system_hgs" model="vsl.vehicle.pass.system">
            <field name="name">HGS</field>
        </record>

        <record id="ownership_ozmal" model="vsl.vehicle.ownership">
            <field name="name">Oz Mal</field>
        </record>
        <record id="ownership_tedarik" model="vsl.vehicle.ownership">
            <field name="name">Tedarik</field>
        </record>

    </data>
</odoo>
```

- [ ] **Step 2: Update __manifest__.py**

Add `"data/vsl_reference_data.xml",` to the data list, after the existing data file entry. The data section should become:

```python
    "data": [
        "security/transport_security.xml",
        "security/ir.model.access.csv",
        "data/transport_data.xml",
        "data/vsl_reference_data.xml",
        "wizards/transport_invoice_wizard.xml",
        "views/transport_order_views.xml",
        "views/transport_stop_views.xml",
        "views/vehicle_assignment_views.xml",
        "views/carrier_document_views.xml",
        "views/res_partner_views.xml",
        "views/menu_views.xml",
        "reports/transport_order_report.xml",
    ],
```

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/data/vsl_reference_data.xml vsl_transport/__manifest__.py
git commit -m "feat: add reference data seed file with driver/vehicle defaults"
```

---

## Task 11: Security — ir.model.access.csv

**Files:**
- Modify: `vsl_transport/security/ir.model.access.csv`

- [ ] **Step 1: Add ACL entries for all new models**

Add the following lines to the CSV file (after the last data row, before EOF):

```csv
access_vsl_vehicle_type_manager,vsl.vehicle.type.manager,model_vsl_vehicle_type,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_type_user,vsl.vehicle.type.user,model_vsl_vehicle_type,group_vsl_transport_user,1,0,0,0
access_vsl_vehicle_type_garage,vsl.vehicle.type.garage,model_vsl_vehicle_type,group_vsl_garage_operator,1,0,0,0
access_vsl_vehicle_type_admin,vsl.vehicle.type.admin,model_vsl_vehicle_type,base.group_system,1,1,1,1
access_vsl_vehicle_trailer_class_manager,vsl.vehicle.trailer.class.manager,model_vsl_vehicle_trailer_class,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_trailer_class_user,vsl.vehicle.trailer.class.user,model_vsl_vehicle_trailer_class,group_vsl_transport_user,1,0,0,0
access_vsl_vehicle_trailer_class_garage,vsl.vehicle.trailer.class.garage,model_vsl_vehicle_trailer_class,group_vsl_garage_operator,1,0,0,0
access_vsl_vehicle_trailer_class_admin,vsl.vehicle.trailer.class.admin,model_vsl_vehicle_trailer_class,base.group_system,1,1,1,1
access_vsl_vehicle_case_type_manager,vsl.vehicle.case.type.manager,model_vsl_vehicle_case_type,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_case_type_user,vsl.vehicle.case.type.user,model_vsl_vehicle_case_type,group_vsl_transport_user,1,0,0,0
access_vsl_vehicle_case_type_garage,vsl.vehicle.case.type.garage,model_vsl_vehicle_case_type,group_vsl_garage_operator,1,0,0,0
access_vsl_vehicle_case_type_admin,vsl.vehicle.case.type.admin,model_vsl_vehicle_case_type,base.group_system,1,1,1,1
access_vsl_vehicle_pass_system_manager,vsl.vehicle.pass.system.manager,model_vsl_vehicle_pass_system,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_pass_system_user,vsl.vehicle.pass.system.user,model_vsl_vehicle_pass_system,group_vsl_transport_user,1,0,0,0
access_vsl_vehicle_pass_system_garage,vsl.vehicle.pass.system.garage,model_vsl_vehicle_pass_system,group_vsl_garage_operator,1,0,0,0
access_vsl_vehicle_pass_system_admin,vsl.vehicle.pass.system.admin,model_vsl_vehicle_pass_system,base.group_system,1,1,1,1
access_vsl_vehicle_ownership_manager,vsl.vehicle.ownership.manager,model_vsl_vehicle_ownership,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_ownership_user,vsl.vehicle.ownership.user,model_vsl_vehicle_ownership,group_vsl_transport_user,1,0,0,0
access_vsl_vehicle_ownership_garage,vsl.vehicle.ownership.garage,model_vsl_vehicle_ownership,group_vsl_garage_operator,1,0,0,0
access_vsl_vehicle_ownership_admin,vsl.vehicle.ownership.admin,model_vsl_vehicle_ownership,base.group_system,1,1,1,1
access_vsl_driver_type_manager,vsl.driver.type.manager,model_vsl_driver_type,group_vsl_transport_manager,1,1,1,1
access_vsl_driver_type_user,vsl.driver.type.user,model_vsl_driver_type,group_vsl_transport_user,1,0,0,0
access_vsl_driver_type_garage,vsl.driver.type.garage,model_vsl_driver_type,group_vsl_garage_operator,1,0,0,0
access_vsl_driver_type_admin,vsl.driver.type.admin,model_vsl_driver_type,base.group_system,1,1,1,1
access_vsl_driver_profile_user,vsl.driver.profile.user,model_vsl_driver_profile,group_vsl_transport_user,1,1,1,0
access_vsl_driver_profile_manager,vsl.driver.profile.manager,model_vsl_driver_profile,group_vsl_transport_manager,1,1,1,1
access_vsl_driver_profile_garage,vsl.driver.profile.garage,model_vsl_driver_profile,group_vsl_garage_operator,1,1,1,0
access_vsl_driver_profile_admin,vsl.driver.profile.admin,model_vsl_driver_profile,base.group_system,1,1,1,1
access_vsl_driver_document_user,vsl.driver.document.user,model_vsl_driver_document,group_vsl_transport_user,1,0,0,0
access_vsl_driver_document_manager,vsl.driver.document.manager,model_vsl_driver_document,group_vsl_transport_manager,1,1,1,1
access_vsl_driver_document_garage,vsl.driver.document.garage,model_vsl_driver_document,group_vsl_garage_operator,1,1,1,1
access_vsl_driver_document_admin,vsl.driver.document.admin,model_vsl_driver_document,base.group_system,1,1,1,1
access_vsl_vehicle_document_user,vsl.vehicle.document.user,model_vsl_vehicle_document,group_vsl_transport_user,1,0,0,0
access_vsl_vehicle_document_manager,vsl.vehicle.document.manager,model_vsl_vehicle_document,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_document_garage,vsl.vehicle.document.garage,model_vsl_vehicle_document,group_vsl_garage_operator,1,1,1,1
access_vsl_vehicle_document_admin,vsl.vehicle.document.admin,model_vsl_vehicle_document,base.group_system,1,1,1,1
access_vsl_location_user,vsl.location.user,model_vsl_location,group_vsl_transport_user,1,1,1,0
access_vsl_location_manager,vsl.location.manager,model_vsl_location,group_vsl_transport_manager,1,1,1,1
access_vsl_location_garage,vsl.location.garage,model_vsl_location,group_vsl_garage_operator,1,0,0,0
access_vsl_location_admin,vsl.location.admin,model_vsl_location,base.group_system,1,1,1,1
access_vsl_dashboard_user,vsl.dashboard.user,model_vsl_dashboard,group_vsl_transport_user,1,0,0,0
access_vsl_dashboard_manager,vsl.dashboard.manager,model_vsl_dashboard,group_vsl_transport_manager,1,0,0,0
access_vsl_dashboard_garage,vsl.dashboard.garage,model_vsl_dashboard,group_vsl_garage_operator,1,0,0,0
access_vsl_dashboard_admin,vsl.dashboard.admin,model_vsl_dashboard,base.group_system,1,0,0,0
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/security/ir.model.access.csv
git commit -m "feat: add ACL entries for all new models"
```

---

## Task 12: Views — Vehicle Reference Data Views

**Files:**
- Create: `vsl_transport/views/vehicle_reference_views.xml`
- Modify: `vsl_transport/__manifest__.py`

- [ ] **Step 1: Create vehicle_reference_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_vehicle_type_list" model="ir.ui.view">
        <field name="name">vsl.vehicle.type.list</field>
        <field name="model">vsl.vehicle.type</field>
        <field name="arch" type="xml">
            <list string="Araç Tipleri" editable="bottom">
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_vsl_vehicle_type" model="ir.actions.act_window">
        <field name="name">Araç Tipleri</field>
        <field name="res_model">vsl.vehicle.type</field>
        <field name="view_mode">list</field>
    </record>

    <record id="view_vsl_vehicle_trailer_class_list" model="ir.ui.view">
        <field name="name">vsl.vehicle.trailer.class.list</field>
        <field name="model">vsl.vehicle.trailer.class</field>
        <field name="arch" type="xml">
            <list string="Dorse Sınıfları" editable="bottom">
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_vsl_vehicle_trailer_class" model="ir.actions.act_window">
        <field name="name">Dorse Sınıfları</field>
        <field name="res_model">vsl.vehicle.trailer.class</field>
        <field name="view_mode">list</field>
    </record>

    <record id="view_vsl_vehicle_case_type_list" model="ir.ui.view">
        <field name="name">vsl.vehicle.case.type.list</field>
        <field name="model">vsl.vehicle.case.type</field>
        <field name="arch" type="xml">
            <list string="Kasa Tipleri" editable="bottom">
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_vsl_vehicle_case_type" model="ir.actions.act_window">
        <field name="name">Kasa Tipleri</field>
        <field name="res_model">vsl.vehicle.case.type</field>
        <field name="view_mode">list</field>
    </record>

    <record id="view_vsl_vehicle_pass_system_list" model="ir.ui.view">
        <field name="name">vsl.vehicle.pass.system.list</field>
        <field name="model">vsl.vehicle.pass.system</field>
        <field name="arch" type="xml">
            <list string="Geçiş Sistemleri" editable="bottom">
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_vsl_vehicle_pass_system" model="ir.actions.act_window">
        <field name="name">Geçiş Sistemleri</field>
        <field name="res_model">vsl.vehicle.pass.system</field>
        <field name="view_mode">list</field>
    </record>

    <record id="view_vsl_vehicle_ownership_list" model="ir.ui.view">
        <field name="name">vsl.vehicle.ownership.list</field>
        <field name="model">vsl.vehicle.ownership</field>
        <field name="arch" type="xml">
            <list string="Sahiplik Durumları" editable="bottom">
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_vsl_vehicle_ownership" model="ir.actions.act_window">
        <field name="name">Sahiplik Durumları</field>
        <field name="res_model">vsl.vehicle.ownership</field>
        <field name="view_mode">list</field>
    </record>

</odoo>
```

- [ ] **Step 2: Update __manifest__.py**

Add `"views/vehicle_reference_views.xml",` to the data list, before `"views/transport_order_views.xml"`.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/views/vehicle_reference_views.xml vsl_transport/__manifest__.py
git commit -m "feat: add list views and actions for vehicle reference data"
```

---

## Task 13: Views — Driver Views

**Files:**
- Create: `vsl_transport/views/driver_views.xml`
- Modify: `vsl_transport/__manifest__.py`

- [ ] **Step 1: Create driver_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_driver_type_list" model="ir.ui.view">
        <field name="name">vsl.driver.type.list</field>
        <field name="model">vsl.driver.type</field>
        <field name="arch" type="xml">
            <list string="Sürücü Tipleri" editable="bottom">
                <field name="name"/>
            </list>
        </field>
    </record>

    <record id="action_vsl_driver_type" model="ir.actions.act_window">
        <field name="name">Sürücü Tipleri</field>
        <field name="res_model">vsl.driver.type</field>
        <field name="view_mode">list</field>
    </record>

    <record id="view_vsl_driver_profile_list" model="ir.ui.view">
        <field name="name">vsl.driver.profile.list</field>
        <field name="model">vsl.driver.profile</field>
        <field name="arch" type="xml">
            <list string="Sürücü Profilleri">
                <field name="partner_id"/>
                <field name="driver_type_id"/>
                <field name="license_number"/>
                <field name="license_class"/>
                <field name="status" widget="badge"/>
                <field name="phone"/>
            </list>
        </field>
    </record>

    <record id="view_vsl_driver_profile_form" model="ir.ui.view">
        <field name="name">vsl.driver.profile.form</field>
        <field name="model">vsl.driver.profile</field>
        <field name="arch" type="xml">
            <form string="Sürücü Profili">
                <sheet>
                    <group>
                        <field name="partner_id"/>
                        <field name="driver_type_id"/>
                        <field name="license_number"/>
                        <field name="license_class"/>
                        <field name="status"/>
                        <field name="phone"/>
                    </group>
                    <group string="Evraklar">
                        <field name="document_ids"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_vsl_driver_profile" model="ir.actions.act_window">
        <field name="name">Sürücü Profilleri</field>
        <field name="res_model">vsl.driver.profile</field>
        <field name="view_mode">list,form</field>
    </record>

    <record id="view_vsl_driver_document_list" model="ir.ui.view">
        <field name="name">vsl.driver.document.list</field>
        <field name="model">vsl.driver.document</field>
        <field name="arch" type="xml">
            <list string="Sürücü Evrakları" editable="bottom">
                <field name="driver_id"/>
                <field name="doc_type"/>
                <field name="issue_date"/>
                <field name="expiry_date"/>
                <field name="state" readonly="1"/>
            </list>
        </field>
    </record>

    <record id="view_vsl_driver_document_form" model="ir.ui.view">
        <field name="name">vsl.driver.document.form</field>
        <field name="model">vsl.driver.document</field>
        <field name="arch" type="xml">
            <form string="Sürücü Evrakı">
                <sheet>
                    <group>
                        <field name="driver_id"/>
                        <field name="doc_type"/>
                        <field name="attachment_id" widget="many2one_binary"/>
                        <field name="issue_date"/>
                        <field name="expiry_date"/>
                        <field name="state" readonly="1"/>
                    </group>
                    <group string="Notlar">
                        <field name="notes"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_vsl_driver_document" model="ir.actions.act_window">
        <field name="name">Sürücü Evrakları</field>
        <field name="res_model">vsl.driver.document</field>
        <field name="view_mode">list,form</field>
    </record>

</odoo>
```

- [ ] **Step 2: Update __manifest__.py**

Add `"views/driver_views.xml",` to the data list, before `"views/transport_order_views.xml"`.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/views/driver_views.xml vsl_transport/__manifest__.py
git commit -m "feat: add views and actions for driver profiles, documents and types"
```

---

## Task 14: Views — Vehicle Document & Fleet Extension Views

**Files:**
- Create: `vsl_transport/views/vehicle_document_views.xml`
- Create: `vsl_transport/views/fleet_vehicle_views.xml`
- Modify: `vsl_transport/__manifest__.py`

- [ ] **Step 1: Create vehicle_document_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_vehicle_document_list" model="ir.ui.view">
        <field name="name">vsl.vehicle.document.list</field>
        <field name="model">vsl.vehicle.document</field>
        <field name="arch" type="xml">
            <list string="Araç Evrakları" editable="bottom">
                <field name="vehicle_id"/>
                <field name="doc_type"/>
                <field name="issue_date"/>
                <field name="expiry_date"/>
                <field name="state" readonly="1"/>
            </list>
        </field>
    </record>

    <record id="view_vsl_vehicle_document_form" model="ir.ui.view">
        <field name="name">vsl.vehicle.document.form</field>
        <field name="model">vsl.vehicle.document</field>
        <field name="arch" type="xml">
            <form string="Araç Evrakı">
                <sheet>
                    <group>
                        <field name="vehicle_id"/>
                        <field name="doc_type"/>
                        <field name="attachment_id" widget="many2one_binary"/>
                        <field name="issue_date"/>
                        <field name="expiry_date"/>
                        <field name="state" readonly="1"/>
                    </group>
                    <group string="Notlar">
                        <field name="notes"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_vsl_vehicle_document" model="ir.actions.act_window">
        <field name="name">Araç Evrakları</field>
        <field name="res_model">vsl.vehicle.document</field>
        <field name="view_mode">list,form</field>
    </record>

</odoo>
```

- [ ] **Step 2: Create fleet_vehicle_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_fleet_vehicle_form_inherit_transport" model="ir.ui.view">
        <field name="name">fleet.vehicle.form.transport</field>
        <field name="model">fleet.vehicle</field>
        <field name="inherit_id" ref="fleet.fleet_vehicle_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@name='tabs']" position="inside">
                <page string="Taşımacılık" name="transport">
                    <group>
                        <field name="vsl_vehicle_type_id"/>
                        <field name="vsl_trailer_class_id"/>
                        <field name="vsl_case_type_id"/>
                        <field name="vsl_pass_system_id"/>
                        <field name="vsl_ownership_id"/>
                        <field name="vsl_capacity"/>
                        <field name="vsl_transport_status"/>
                    </group>
                    <group string="Araç Evrakları">
                        <field name="vsl_document_ids"/>
                    </group>
                </page>
            </xpath>
        </field>
    </record>

</odoo>
```

- [ ] **Step 3: Update __manifest__.py**

Add both new view files to the data list, before `"views/transport_order_views.xml"`:

```python
        "views/vehicle_document_views.xml",
        "views/fleet_vehicle_views.xml",
```

- [ ] **Step 4: Commit**

```bash
git add vsl_transport/views/vehicle_document_views.xml vsl_transport/views/fleet_vehicle_views.xml vsl_transport/__manifest__.py
git commit -m "feat: add vehicle document views and fleet.vehicle transport tab"
```

---

## Task 15: Views — Location & Dashboard Views

**Files:**
- Create: `vsl_transport/views/location_views.xml`
- Create: `vsl_transport/views/dashboard_views.xml`
- Modify: `vsl_transport/__manifest__.py`

- [ ] **Step 1: Create location_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_location_list" model="ir.ui.view">
        <field name="name">vsl.location.list</field>
        <field name="model">vsl.location</field>
        <field name="arch" type="xml">
            <list string="Lokasyonlar">
                <field name="name"/>
                <field name="type"/>
                <field name="city"/>
                <field name="contact_name"/>
                <field name="contact_phone"/>
            </list>
        </field>
    </record>

    <record id="view_vsl_location_form" model="ir.ui.view">
        <field name="name">vsl.location.form</field>
        <field name="model">vsl.location</field>
        <field name="arch" type="xml">
            <form string="Lokasyon">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="type"/>
                        <field name="partner_id"/>
                    </group>
                    <group string="Adres">
                        <field name="street"/>
                        <field name="city"/>
                        <field name="country_id"/>
                    </group>
                    <group string="Koordinatlar">
                        <field name="latitude"/>
                        <field name="longitude"/>
                    </group>
                    <group string="Yetkili">
                        <field name="contact_name"/>
                        <field name="contact_phone"/>
                    </group>
                    <group string="Özellikler">
                        <field name="features"/>
                    </group>
                    <group string="Notlar">
                        <field name="notes"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="view_vsl_location_search" model="ir.ui.view">
        <field name="name">vsl.location.search</field>
        <field name="model">vsl.location</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <filter name="filter_warehouse" string="Depo"
                        domain="[('type', '=', 'warehouse')]"/>
                <filter name="filter_port" string="Liman"
                        domain="[('type', '=', 'port')]"/>
                <filter name="filter_customs" string="Gümrük"
                        domain="[('type', '=', 'customs')]"/>
                <filter name="filter_factory" string="Fabrika"
                        domain="[('type', '=', 'factory')]"/>
            </search>
        </field>
    </record>

    <record id="action_vsl_location" model="ir.actions.act_window">
        <field name="name">Lokasyonlar</field>
        <field name="res_model">vsl.location</field>
        <field name="view_mode">list,form</field>
        <field name="search_view_id" ref="view_vsl_location_search"/>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">Henüz bir lokasyon yok.</p>
            <p>Depo, liman, gümrük, fabrika gibi yükleme/boşaltma noktalarını tanımlayın.</p>
        </field>
    </record>

</odoo>
```

- [ ] **Step 2: Create dashboard_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_dashboard" model="ir.ui.view">
        <field name="name">vsl.dashboard.view</field>
        <field name="model">vsl.dashboard</field>
        <field name="arch" type="xml">
            <form string="Taşımacılık Panosu">
                <sheet>
                    <div class="o_dashboard_container">
                        <group string="Operasyon">
                            <field name="total_orders" widget="statinfo"/>
                            <field name="open_orders" widget="statinfo"/>
                            <field name="loading_orders" widget="statinfo"/>
                            <field name="in_transit_orders" widget="statinfo"/>
                            <field name="delivered_month" widget="statinfo"/>
                            <field name="cancelled_month" widget="statinfo"/>
                        </group>
                        <group string="Filo">
                            <field name="total_vehicles" widget="statinfo"/>
                            <field name="available_vehicles" widget="statinfo"/>
                            <field name="on_route_vehicles" widget="statinfo"/>
                            <field name="maintenance_vehicles" widget="statinfo"/>
                            <field name="total_drivers" widget="statinfo"/>
                            <field name="active_drivers" widget="statinfo"/>
                            <field name="on_leave_drivers" widget="statinfo"/>
                        </group>
                        <group string="İş Ortakları">
                            <field name="total_carriers" widget="statinfo"/>
                            <field name="total_locations" widget="statinfo"/>
                        </group>
                    </div>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_vsl_dashboard" model="ir.actions.act_window">
        <field name="name">Dashboard</field>
        <field name="res_model">vsl.dashboard</field>
        <field name="view_mode">form</field>
        <field name="target">current</field>
    </record>

</odoo>
```

- [ ] **Step 3: Update __manifest__.py**

Add both new view files to the data list, before `"views/transport_order_views.xml"`:

```python
        "views/location_views.xml",
        "views/dashboard_views.xml",
```

- [ ] **Step 4: Commit**

```bash
git add vsl_transport/views/location_views.xml vsl_transport/views/dashboard_views.xml vsl_transport/__manifest__.py
git commit -m "feat: add location views with type filters and dashboard view"
```

---

## Task 16: Menu Structure Update

**Files:**
- Modify: `vsl_transport/views/menu_views.xml`

- [ ] **Step 1: Add new menu items to menu_views.xml**

Add the following menu items inside the `<odoo>` element, after the existing `menu_vsl_transport_config` (before `</odoo>`):

```xml
    <menuitem id="menu_vsl_drivers"
              name="Sürücüler"
              parent="menu_vsl_transport_root"
              sequence="15"/>

    <menuitem id="menu_vsl_driver_profile"
              name="Sürücü Profilleri"
              parent="menu_vsl_drivers"
              action="action_vsl_driver_profile"
              sequence="10"/>

    <menuitem id="menu_vsl_driver_document"
              name="Sürücü Evrakları"
              parent="menu_vsl_drivers"
              action="action_vsl_driver_document"
              sequence="20"/>

    <menuitem id="menu_vsl_driver_type"
              name="Sürücü Tipleri"
              parent="menu_vsl_drivers"
              action="action_vsl_driver_type"
              sequence="30"
              groups="vsl_transport.group_vsl_transport_manager"/>

    <menuitem id="menu_vsl_vehicle_mgmt"
              name="Araç Yönetimi"
              parent="menu_vsl_transport_root"
              sequence="25"/>

    <menuitem id="menu_vsl_vehicle_document"
              name="Araç Evrakları"
              parent="menu_vsl_vehicle_mgmt"
              action="action_vsl_vehicle_document"
              sequence="10"/>

    <menuitem id="menu_vsl_vehicle_type"
              name="Araç Tipleri"
              parent="menu_vsl_vehicle_mgmt"
              action="action_vsl_vehicle_type"
              sequence="20"
              groups="vsl_transport.group_vsl_transport_manager"/>

    <menuitem id="menu_vsl_vehicle_case_type"
              name="Kasa Tipleri"
              parent="menu_vsl_vehicle_mgmt"
              action="action_vsl_vehicle_case_type"
              sequence="30"
              groups="vsl_transport.group_vsl_transport_manager"/>

    <menuitem id="menu_vsl_vehicle_trailer_class"
              name="Dorse Sınıfları"
              parent="menu_vsl_vehicle_mgmt"
              action="action_vsl_vehicle_trailer_class"
              sequence="40"
              groups="vsl_transport.group_vsl_transport_manager"/>

    <menuitem id="menu_vsl_vehicle_pass_system"
              name="Geçiş Sistemleri"
              parent="menu_vsl_vehicle_mgmt"
              action="action_vsl_vehicle_pass_system"
              sequence="50"
              groups="vsl_transport.group_vsl_transport_manager"/>

    <menuitem id="menu_vsl_vehicle_ownership"
              name="Sahiplik Durumları"
              parent="menu_vsl_vehicle_mgmt"
              action="action_vsl_vehicle_ownership"
              sequence="60"
              groups="vsl_transport.group_vsl_transport_manager"/>

    <menuitem id="menu_vsl_location"
              name="Lokasyonlar"
              parent="menu_vsl_transport_root"
              action="action_vsl_location"
              sequence="35"/>

    <menuitem id="menu_vsl_dashboard"
              name="Dashboard"
              parent="menu_vsl_transport_root"
              action="action_vsl_dashboard"
              sequence="5"/>
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/views/menu_views.xml
git commit -m "feat: add new menus for drivers, vehicle mgmt, locations and dashboard"
```

---

## Task 17: Tests — Write TDD Tests for All Features

**Files:**
- Create: `vsl_transport/tests/test_driver.py`
- Create: `vsl_transport/tests/test_vehicle_extensions.py`
- Create: `vsl_transport/tests/test_location.py`
- Create: `vsl_transport/tests/test_dashboard.py`

- [ ] **Step 1: Run existing tests to ensure baseline**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml stop web && \
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  --test-enable -d odoo -u vsl_transport --stop-after-init && \
docker compose -f ~/dev/odoo/docker-compose.yml up -d web
```
Expected: 12/12 tests pass

- [ ] **Step 2: Create test_driver.py**

```python
import base64

from odoo.tests.common import TransactionCase


class TestDriverProfile(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Driver"})
        self.driver_type = self.env["vsl.driver.type"].create({"name": "Sozlesmeli"})

    def test_create_driver_profile(self):
        driver = self.env["vsl.driver.profile"].create({
            "partner_id": self.partner.id,
            "driver_type_id": self.driver_type.id,
            "license_number": "123456",
            "license_class": "CE",
            "status": "active",
        })
        self.assertEqual(driver.status, "active")
        self.assertEqual(driver.license_class, "CE")


class TestDriverDocument(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Driver Doc Test"})
        self.driver = self.env["vsl.driver.profile"].create({
            "partner_id": self.partner.id,
            "status": "active",
        })

    def test_create_document(self):
        attachment = self.env["ir.attachment"].create({
            "name": "license.pdf",
            "datas": base64.b64encode(b"dummy"),
        })
        doc = self.env["vsl.driver.document"].create({
            "driver_id": self.driver.id,
            "doc_type": "driving_license",
            "attachment_id": attachment.id,
            "expiry_date": "2028-01-01",
        })
        self.assertEqual(doc.state, "valid")

    def test_document_expired(self):
        attachment = self.env["ir.attachment"].create({
            "name": "old_license.pdf",
            "datas": base64.b64encode(b"dummy"),
        })
        doc = self.env["vsl.driver.document"].create({
            "driver_id": self.driver.id,
            "doc_type": "driving_license",
            "attachment_id": attachment.id,
            "expiry_date": "2020-01-01",
        })
        self.assertEqual(doc.state, "expired")
```

- [ ] **Step 3: Create test_vehicle_extensions.py**

```python
import base64

from odoo.tests.common import TransactionCase


class TestVehicleExtensions(TransactionCase):

    def setUp(self):
        super().setUp()
        self.vehicle_type = self.env["vsl.vehicle.type"].create({"name": "10 Teker"})
        self.ownership = self.env["vsl.vehicle.ownership"].create({"name": "Oz Mal"})
        self.vehicle = self.env["fleet.vehicle"].create({
            "name": "Test Arac",
            "license_plate": "34TEST123",
            "vsl_vehicle_type_id": self.vehicle_type.id,
            "vsl_ownership_id": self.ownership.id,
            "vsl_capacity": 20.0,
            "vsl_transport_status": "available",
        })

    def test_vehicle_transport_fields(self):
        self.assertEqual(self.vehicle.vsl_transport_status, "available")
        self.assertEqual(self.vehicle.vsl_capacity, 20.0)
        self.assertEqual(self.vehicle.vsl_vehicle_type_id.name, "10 Teker")

    def test_vehicle_document(self):
        attachment = self.env["ir.attachment"].create({
            "name": "insurance.pdf",
            "datas": base64.b64encode(b"dummy"),
        })
        doc = self.env["vsl.vehicle.document"].create({
            "vehicle_id": self.vehicle.id,
            "doc_type": "insurance",
            "attachment_id": attachment.id,
            "expiry_date": "2028-01-01",
        })
        self.assertEqual(doc.state, "valid")

    def test_vehicle_document_expired(self):
        attachment = self.env["ir.attachment"].create({
            "name": "old_insurance.pdf",
            "datas": base64.b64encode(b"dummy"),
        })
        doc = self.env["vsl.vehicle.document"].create({
            "vehicle_id": self.vehicle.id,
            "doc_type": "insurance",
            "attachment_id": attachment.id,
            "expiry_date": "2020-01-01",
        })
        self.assertEqual(doc.state, "expired")
```

- [ ] **Step 4: Create test_location.py**

```python
from odoo.tests.common import TransactionCase


class TestLocation(TransactionCase):

    def test_create_location(self):
        location = self.env["vsl.location"].create({
            "name": "Test Depo",
            "type": "warehouse",
            "city": "Istanbul",
            "latitude": 41.0,
            "longitude": 29.0,
            "features": "Forklift, Cold Storage",
        })
        self.assertEqual(location.type, "warehouse")
        self.assertEqual(location.city, "Istanbul")

    def test_location_with_country(self):
        country_tr = self.env.ref("base.tr", raise_if_not_found=False)
        if not country_tr:
            country_tr = self.env["res.country"].search([("code", "=", "TR")], limit=1)
        location = self.env["vsl.location"].create({
            "name": "Mersin Port",
            "type": "port",
            "city": "Mersin",
            "country_id": country_tr.id if country_tr else False,
        })
        self.assertEqual(location.type, "port")
```

- [ ] **Step 5: Create test_dashboard.py**

```python
from odoo.tests.common import TransactionCase


class TestDashboard(TransactionCase):

    def setUp(self):
        super().setUp()
        self.customer = self.env["res.partner"].create({"name": "Dash Customer"})
        self.carrier = self.env["res.partner"].create({
            "name": "Dash Carrier",
            "is_carrier": True,
        })
        self.load_address = self.env["res.partner"].create({
            "name": "Load Addr",
            "type": "delivery",
        })
        self.unload_address = self.env["res.partner"].create({
            "name": "Unload Addr",
            "type": "delivery",
        })

    def _create_order(self, state="draft"):
        return self.env["vsl.transport.order"].create({
            "customer_id": self.customer.id,
            "state": state,
            "stop_ids": [
                (0, 0, {
                    "stop_type": "loading",
                    "address_id": self.load_address.id,
                    "sequence": 10,
                    "state": "done" if state in ("in_transit", "delivered") else "pending",
                }),
                (0, 0, {
                    "stop_type": "unloading",
                    "address_id": self.unload_address.id,
                    "sequence": 20,
                    "state": "done" if state == "delivered" else "pending",
                }),
            ],
        })

    def test_dashboard_metrics(self):
        self._create_order("open")
        self._create_order("loading")
        self._create_order("in_transit")

        dashboard = self.env["vsl.dashboard"].new({})

        self.assertEqual(dashboard.total_orders, 3)
        self.assertEqual(dashboard.open_orders, 1)
        self.assertEqual(dashboard.loading_orders, 1)
        self.assertEqual(dashboard.in_transit_orders, 1)
```

- [ ] **Step 6: Commit all test files**

```bash
git add vsl_transport/tests/test_driver.py vsl_transport/tests/test_vehicle_extensions.py vsl_transport/tests/test_location.py vsl_transport/tests/test_dashboard.py
git commit -m "test: add tests for drivers, vehicle extensions, locations and dashboard"
```

- [ ] **Step 7: Run all tests**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml stop web && \
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  --test-enable -d odoo -u vsl_transport --stop-after-init && \
docker compose -f ~/dev/odoo/docker-compose.yml up -d web
```
Expected: All tests pass (12 existing + ~10 new)

---

## Task 18: Final Integration Verification

**Files:** None (verification only)

- [ ] **Step 1: Run full test suite with verbose output**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml stop web && \
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  --test-enable -d odoo -u vsl_transport --stop-after-init --log-level=test 2>&1 | tee /tmp/test_output.txt && \
docker compose -f ~/dev/odoo/docker-compose.yml up -d web
```

- [ ] **Step 2: Verify all models loaded correctly**

Check for any import errors or missing model warnings in the output.

- [ ] **Step 3: Verify data seed loaded**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml exec db psql -U odoo -d odoo -c "SELECT count(*) FROM vsl_vehicle_type;"
```
Expected: 10 records

- [ ] **Step 4: Final commit (if any manifest/data fixes needed)**

```bash
git status
git add -A
git commit -m "chore: final integration fixes and verification"
```

---

## Implementation Order Summary

```
Task 1  → Vehicle reference data models (5)
Task 2  → Driver type model
Task 3  → Driver document model (depends on Task 4 conceptually, but no code dep)
Task 4  → Driver profile model (depends on Task 3 doc_type ref)
Task 5  → Vehicle document model
Task 6  → fleet.vehicle inheritance (depends on Tasks 1, 5)
Task 7  → Location model
Task 8  → stop.location_id (depends on Task 7)
Task 9  → Dashboard model (depends on Tasks 4, 6, 7)
Task 10 → Reference data seed (depends on Tasks 1, 2)
Task 11 → Security ACLs (depends on all model tasks)
Task 12 → Vehicle reference views (depends on Tasks 1, 11)
Task 13 → Driver views (depends on Tasks 2, 3, 4, 11)
Task 14 → Vehicle doc + fleet views (depends on Tasks 5, 6, 11)
Task 15 → Location + dashboard views (depends on Tasks 7, 9, 11)
Task 16 → Menu update (depends on Tasks 12-15)
Task 17 → Tests (depends on all model tasks)
Task 18 → Final verification
```
