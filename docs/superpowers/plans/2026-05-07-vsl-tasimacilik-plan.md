# vsl-Taşımacılık Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an end-to-end transport management Odoo 19 module with transport orders, multi-stop loading/unloading, vehicle/carrier assignment, document management, and dual invoicing.

**Architecture:** Custom core models (`vsl.transport.order`, `vsl.transport.stop`, etc.) with hooks into Odoo's `res.partner`, `fleet.vehicle`, `account.move`, and `ir.attachment`. Single module `vsl_tasimacilik` under `~/dev/vsl-tms-odoo/` symlinked to Odoo addons.

**Tech Stack:** Python 3 (Odoo 19 ORM), XML views, PostgreSQL 16

---

## Task 1: Module Skeleton and Manifest

**Files:**
- Create: `vsl_tasimacilik/__init__.py`
- Create: `vsl_tasimacilik/__manifest__.py`
- Create: `vsl_tasimacilik/models/__init__.py`
- Create empty placeholder: `vsl_tasimacilik/static/description/icon.png`
- Symlink: `~/dev/odoo/addons/vsl_tasimacilik` → `~/dev/vsl-tms-odoo/vsl_tasimacilik`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p ~/dev/vsl-tms-odoo/vsl_tasimacilik/{models,views,security,i18n,data,wizards,reports,static/description,tests}
```

- [ ] **Step 2: Create __init__.py (root)**

```python
from . import models
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/__init__.py`

- [ ] **Step 3: Create __manifest__.py**

```python
{
    "name": "vsl-Taşımacılık",
    "summary": "Uçtan uca sevkiyat yönetim modülü",
    "description": """
Türkiye'deki lojistik firmaları için uçtan uca sevkiyat yönetimi.
Özellikler: Sevkiyat emri, çoklu/parsiyel yükleme-boşaltma,
araç ve sürücü ataması (kendi filo + dış tedarikçi),
tedarikçi evrak yönetimi, geçmiş rota fiyat sorgulama,
çift yönlü fatura oluşturma.
    """,
    "version": "19.0.1.0.0",
    "category": "Transportation",
    "website": "https://www.vsl.com.tr",
    "author": "VSL",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "mail", "contacts", "fleet", "account"],
    "data": [
        "security/transport_security.xml",
        "security/ir.model.access.csv",
        "data/transport_data.xml",
        "views/transport_order_views.xml",
        "views/transport_stop_views.xml",
        "views/vehicle_assignment_views.xml",
        "views/carrier_document_views.xml",
        "views/res_partner_views.xml",
        "views/menu_views.xml",
        "wizards/transport_invoice_wizard.xml",
        "reports/transport_order_report.xml",
    ],
}
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/__manifest__.py`

- [ ] **Step 4: Create models/__init__.py (empty)**

```python
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/__init__.py`

- [ ] **Step 5: Create placeholder icon**

```bash
touch ~/dev/vsl-tms-odoo/vsl_tasimacilik/static/description/icon.png
```

- [ ] **Step 6: Symlink to Odoo addons**

```bash
rm -rf ~/dev/odoo/addons/vsl_tasimacilik
ln -s ~/dev/vsl-tms-odoo/vsl_tasimacilik ~/dev/odoo/addons/vsl_tasimacilik
```

- [ ] **Step 7: Commit**

```bash
git add vsl_tasimacilik/
git commit -m "feat: add module skeleton with manifest and directory structure"
```

---

## Task 2: Extend res.partner (Carrier fields)

**Files:**
- Create: `vsl_tasimacilik/models/res_partner.py`
- Modify: `vsl_tasimacilik/models/__init__.py`

- [ ] **Step 1: Write res_partner.py**

```python
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_carrier = fields.Boolean(
        string="Carrier / Supplier",
        help="This partner is a transport carrier/supplier.",
    )
    carrier_tax_office = fields.Char(string="Tax Office")
    carrier_tax_number = fields.Char(string="Tax Number")
    carrier_document_ids = fields.One2many(
        "vsl.carrier.document",
        "carrier_id",
        string="Documents",
    )
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/res_partner.py`

- [ ] **Step 2: Update models/__init__.py**

```python
from . import res_partner
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/__init__.py`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/models/res_partner.py vsl_tasimacilik/models/__init__.py
git commit -m "feat: extend res.partner with carrier fields"
```

---

## Task 3: Carrier Document Model

**Files:**
- Create: `vsl_tasimacilik/models/carrier_document.py`
- Modify: `vsl_tasimacilik/models/__init__.py`

- [ ] **Step 1: Write carrier_document.py**

```python
from odoo import api, fields, models


class VslCarrierDocument(models.Model):
    _name = "vsl.carrier.document"
    _description = "Carrier Document"
    _rec_name = "doc_type"
    _order = "expiry_date asc"

    carrier_id = fields.Many2one(
        "res.partner",
        string="Carrier",
        required=True,
        domain=[("is_carrier", "=", True)],
        ondelete="cascade",
    )
    doc_type = fields.Selection(
        [
            ("driving_license", "Driving License"),
            ("vehicle_registration", "Vehicle Registration"),
            ("insurance", "Insurance"),
            ("src_certificate", "SRC Certificate"),
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
        store=True,
    )

    @api.depends("expiry_date")
    def _compute_state(self):
        today = fields.Date.today()
        for doc in self:
            if doc.expiry_date and doc.expiry_date < today:
                doc.state = "expired"
            else:
                doc.state = "valid"
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/carrier_document.py`

- [ ] **Step 2: Update models/__init__.py**

```python
from . import res_partner
from . import carrier_document
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/__init__.py`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/models/carrier_document.py vsl_tasimacilik/models/__init__.py
git commit -m "feat: add carrier document model with expiry tracking"
```

---

## Task 4: Transport Order Model

**Files:**
- Create: `vsl_tasimacilik/models/transport_order.py`
- Modify: `vsl_tasimacilik/models/__init__.py`

- [ ] **Step 1: Write transport_order.py**

```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VslTransportOrder(models.Model):
    _name = "vsl.transport.order"
    _description = "Transport Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "id desc"

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

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "vsl.transport.order"
            ) or _("New")
        return super().create(vals)

    def action_confirm(self):
        for order in self:
            if not order.customer_id:
                raise UserError(_("Please set a customer before confirming."))
            load_stops = order.stop_ids.filtered(lambda s: s.stop_type == "loading")
            unload_stops = order.stop_ids.filtered(lambda s: s.stop_type == "unloading")
            if not load_stops or not unload_stops:
                raise UserError(
                    _("At least one loading and one unloading stop is required.")
                )
            order.state = "open"

    def action_cancel(self):
        for order in self:
            if order.state == "invoiced":
                raise UserError(_("Invoiced orders cannot be cancelled."))
            order.state = "cancelled"

    def action_start_loading(self):
        for order in self:
            if not order.assignment_ids:
                raise UserError(
                    _("Please assign a vehicle and driver before starting loading.")
                )
            order.actual_date_start = fields.Datetime.now()
            order.state = "loading"

    def action_depart(self):
        for order in self:
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
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/transport_order.py`

- [ ] **Step 2: Update models/__init__.py**

```python
from . import res_partner
from . import carrier_document
from . import transport_order
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/__init__.py`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/models/transport_order.py vsl_tasimacilik/models/__init__.py
git commit -m "feat: add transport order model with state machine and actions"
```

---

## Task 5: Transport Stop and Stop Line Models

**Files:**
- Create: `vsl_tasimacilik/models/transport_stop.py`
- Modify: `vsl_tasimacilik/models/__init__.py`

- [ ] **Step 1: Write transport_stop.py (both models in one file)**

```python
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
    )
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
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/transport_stop.py`

- [ ] **Step 2: Update models/__init__.py**

```python
from . import res_partner
from . import carrier_document
from . import transport_order
from . import transport_stop
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/__init__.py`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/models/transport_stop.py vsl_tasimacilik/models/__init__.py
git commit -m "feat: add transport stop and stop line models"
```

---

## Task 6: Vehicle Assignment Model

**Files:**
- Create: `vsl_tasimacilik/models/vehicle_assignment.py`
- Modify: `vsl_tasimacilik/models/__init__.py`

- [ ] **Step 1: Write vehicle_assignment.py**

```python
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
            ("assigned", "Assigned"),
            ("departed", "Departed"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
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
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/vehicle_assignment.py`

- [ ] **Step 2: Update models/__init__.py**

```python
from . import res_partner
from . import carrier_document
from . import transport_order
from . import transport_stop
from . import vehicle_assignment
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/models/__init__.py`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/models/vehicle_assignment.py vsl_tasimacilik/models/__init__.py
git commit -m "feat: add vehicle assignment model"
```

---

## Task 7: Data Files (Sequence, Default Values)

**Files:**
- Create: `vsl_tasimacilik/data/transport_data.xml`

- [ ] **Step 1: Write transport_data.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <record id="seq_vsl_transport_order" model="ir.sequence">
            <field name="name">Transport Order</field>
            <field name="code">vsl.transport.order</field>
            <field name="prefix">TMS/%(year)s/</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>

        <record id="carrier_contact_type" model="res.partner.category">
            <field name="name">Carrier</field>
        </record>

    </data>
</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/data/transport_data.xml`

- [ ] **Step 2: Commit**

```bash
git add vsl_tasimacilik/data/transport_data.xml
git commit -m "feat: add data files with transport order sequence"
```

---

## Task 8: Security (Access Rights and Record Rules)

**Files:**
- Create: `vsl_tasimacilik/security/transport_security.xml`
- Create: `vsl_tasimacilik/security/ir.model.access.csv`

- [ ] **Step 1: Write transport_security.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <record id="group_vsl_transport_user" model="res.groups">
            <field name="name">Transport User</field>
            <field name="category_id" ref="base.module_category_hidden"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <record id="group_vsl_garage_operator" model="res.groups">
            <field name="name">Garage Operator</field>
            <field name="category_id" ref="base.module_category_hidden"/>
            <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
        </record>

        <record id="group_vsl_transport_manager" model="res.groups">
            <field name="name">Transport Manager</field>
            <field name="category_id" ref="base.module_category_hidden"/>
            <field name="implied_ids" eval="[
                (4, ref('vsl_tasimacilik.group_vsl_transport_user')),
                (4, ref('vsl_tasimacilik.group_vsl_garage_operator')),
            ]"/>
        </record>

        <!-- Transport User sees their own orders -->
        <record id="rule_transport_order_user" model="ir.rule">
            <field name="name">Transport User: own orders</field>
            <field name="model_id" ref="model_vsl_transport_order"/>
            <field name="groups" eval="[(4, ref('vsl_tasimacilik.group_vsl_transport_user'))]"/>
            <field name="domain_force">[('create_uid', '=', user.id)]</field>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Garage Operator sees open orders for assignment -->
        <record id="rule_transport_order_garage" model="ir.rule">
            <field name="name">Garage Operator: open orders</field>
            <field name="model_id" ref="model_vsl_transport_order"/>
            <field name="groups" eval="[(4, ref('vsl_tasimacilik.group_vsl_garage_operator'))]"/>
            <field name="domain_force">[('state', '=', 'open')]</field>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="False"/>
            <field name="perm_unlink" eval="False"/>
        </record>

        <!-- Manager sees all -->
        <record id="rule_transport_order_manager" model="ir.rule">
            <field name="name">Transport Manager: all orders</field>
            <field name="model_id" ref="model_vsl_transport_order"/>
            <field name="groups" eval="[(4, ref('vsl_tasimacilik.group_vsl_transport_manager'))]"/>
            <field name="domain_force">[(1, '=', 1)]</field>
        </record>

        <!-- Carrier documents: garage operator full access -->
        <record id="rule_carrier_document_garage" model="ir.rule">
            <field name="name">Garage Operator: carrier documents</field>
            <field name="model_id" ref="model_vsl_carrier_document"/>
            <field name="groups" eval="[(4, ref('vsl_tasimacilik.group_vsl_garage_operator'))]"/>
            <field name="domain_force">[(1, '=', 1)]</field>
        </record>

    </data>
</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/security/transport_security.xml`

- [ ] **Step 2: Write ir.model.access.csv**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_vsl_transport_order_user,vsl.transport.order.user,model_vsl_transport_order,group_vsl_transport_user,1,1,1,0
access_vsl_transport_order_manager,vsl.transport.order.manager,model_vsl_transport_order,group_vsl_transport_manager,1,1,1,1
access_vsl_transport_order_garage,vsl.transport.order.garage,model_vsl_transport_order,group_vsl_garage_operator,1,1,0,0
access_vsl_transport_stop_user,vsl.transport.stop.user,model_vsl_transport_stop,group_vsl_transport_user,1,1,1,0
access_vsl_transport_stop_manager,vsl.transport.stop.manager,model_vsl_transport_stop,group_vsl_transport_manager,1,1,1,1
access_vsl_transport_stop_garage,vsl.transport.stop.garage,model_vsl_transport_stop,group_vsl_garage_operator,1,0,0,0
access_vsl_transport_stop_line_user,vsl.transport.stop.line.user,model_vsl_transport_stop_line,group_vsl_transport_user,1,1,1,0
access_vsl_transport_stop_line_manager,vsl.transport.stop.line.manager,model_vsl_transport_stop_line,group_vsl_transport_manager,1,1,1,1
access_vsl_transport_stop_line_garage,vsl.transport.stop.line.garage,model_vsl_transport_stop_line,group_vsl_garage_operator,1,0,0,0
access_vsl_vehicle_assignment_user,vsl.vehicle.assignment.user,model_vsl_vehicle_assignment,group_vsl_transport_user,1,1,1,0
access_vsl_vehicle_assignment_manager,vsl.vehicle.assignment.manager,model_vsl_vehicle_assignment,group_vsl_transport_manager,1,1,1,1
access_vsl_vehicle_assignment_garage,vsl.vehicle.assignment.garage,model_vsl_vehicle_assignment,group_vsl_garage_operator,1,1,1,0
access_vsl_carrier_document_user,vsl.carrier.document.user,model_vsl_carrier_document,group_vsl_transport_user,1,0,0,0
access_vsl_carrier_document_manager,vsl.carrier.document.manager,model_vsl_carrier_document,group_vsl_transport_manager,1,1,1,1
access_vsl_carrier_document_garage,vsl.carrier.document.garage,model_vsl_carrier_document,group_vsl_garage_operator,1,1,1,1
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/security/ir.model.access.csv`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/security/
git commit -m "feat: add security groups, access rights and record rules"
```

---

## Task 9: Views — res.partner Extension and Carrier Document

**Files:**
- Create: `vsl_tasimacilik/views/res_partner_views.xml`
- Create: `vsl_tasimacilik/views/carrier_document_views.xml`

- [ ] **Step 1: Write res_partner_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_partner_form_inherit_transport" model="ir.ui.view">
        <field name="name">res.partner.form.transport</field>
        <field name="model">res.partner</field>
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@name='sales_purchases']" position="inside">
                <group string="Carrier Information" name="carrier_info">
                    <field name="is_carrier"/>
                    <field name="carrier_tax_office"
                           attrs="{'invisible': [('is_carrier', '=', False)]}"/>
                    <field name="carrier_tax_number"
                           attrs="{'invisible': [('is_carrier', '=', False)]}"/>
                </group>
            </xpath>
            <xpath expr="//page[@name='sales_purchases']" position="after">
                <page string="Documents" name="carrier_documents"
                      attrs="{'invisible': [('is_carrier', '=', False)]}">
                    <field name="carrier_document_ids" mode="tree,form">
                        <tree string="Documents" editable="bottom">
                            <field name="doc_type"/>
                            <field name="attachment_id"/>
                            <field name="issue_date"/>
                            <field name="expiry_date"/>
                            <field name="state" readonly="1"/>
                        </tree>
                        <form>
                            <group>
                                <field name="carrier_id" invisible="1"/>
                                <field name="doc_type"/>
                                <field name="attachment_id"/>
                                <field name="issue_date"/>
                                <field name="expiry_date"/>
                                <field name="state" readonly="1"/>
                            </group>
                        </form>
                    </field>
                </page>
            </xpath>
        </field>
    </record>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/views/res_partner_views.xml`

- [ ] **Step 2: Write carrier_document_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_carrier_document_tree" model="ir.ui.view">
        <field name="name">vsl.carrier.document.tree</field>
        <field name="model">vsl.carrier.document</field>
        <field name="arch" type="xml">
            <tree string="Documents" editable="bottom">
                <field name="carrier_id"/>
                <field name="doc_type"/>
                <field name="issue_date"/>
                <field name="expiry_date"/>
                <field name="state" readonly="1"/>
            </tree>
        </field>
    </record>

    <record id="view_vsl_carrier_document_form" model="ir.ui.view">
        <field name="name">vsl.carrier.document.form</field>
        <field name="model">vsl.carrier.document</field>
        <field name="arch" type="xml">
            <form string="Carrier Document">
                <sheet>
                    <group>
                        <field name="carrier_id"/>
                        <field name="doc_type"/>
                        <field name="attachment_id" widget="many2one_binary"/>
                        <field name="issue_date"/>
                        <field name="expiry_date"/>
                        <field name="state" readonly="1"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_vsl_carrier_document" model="ir.actions.act_window">
        <field name="name">Carrier Documents</field>
        <field name="res_model">vsl.carrier.document</field>
        <field name="view_mode">tree,form</field>
    </record>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/views/carrier_document_views.xml`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/views/res_partner_views.xml vsl_tasimacilik/views/carrier_document_views.xml
git commit -m "feat: add views for carrier fields on res.partner and carrier documents"
```

---

## Task 10: Views — Transport Order, Stops, and Vehicle Assignment

**Files:**
- Create: `vsl_tasimacilik/views/transport_order_views.xml`
- Create: `vsl_tasimacilik/views/transport_stop_views.xml`
- Create: `vsl_tasimacilik/views/vehicle_assignment_views.xml`

- [ ] **Step 1: Write transport_order_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Tree View -->
    <record id="view_vsl_transport_order_tree" model="ir.ui.view">
        <field name="name">vsl.transport.order.tree</field>
        <field name="model">vsl.transport.order</field>
        <field name="arch" type="xml">
            <tree string="Transport Orders" decoration-danger="state == 'cancelled'"
                  decoration-success="state == 'invoiced'">
                <field name="name"/>
                <field name="customer_id"/>
                <field name="state" widget="badge"/>
                <field name="planned_date_start"/>
                <field name="planned_date_end"/>
                <field name="amount_total" sum="Total"/>
                <field name="currency_id" invisible="1"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_vsl_transport_order_form" model="ir.ui.view">
        <field name="name">vsl.transport.order.form</field>
        <field name="model">vsl.transport.order</field>
        <field name="arch" type="xml">
            <form string="Transport Order">
                <header>
                    <button name="action_confirm" type="object"
                            string="Confirm" class="btn-primary"
                            states="draft"/>
                    <button name="action_start_loading" type="object"
                            string="Start Loading" class="btn-primary"
                            states="assigned"/>
                    <button name="action_depart" type="object"
                            string="Depart" class="btn-primary"
                            states="loading"/>
                    <button name="action_deliver" type="object"
                            string="Deliver" class="btn-primary"
                            states="in_transit"/>
                    <button name="action_view_history" type="object"
                            string="View History" class="btn-secondary"
                            states="draft,open,assigned"/>
                    <button name="%(action_vsl_transport_invoice_wizard)d" type="action"
                            string="Create Invoices" class="btn-primary"
                            states="delivered"/>
                    <button name="action_cancel" type="object"
                            string="Cancel" states="draft,open,assigned,loading,in_transit,delivered"/>
                    <field name="state" widget="statusbar"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name"/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="customer_id"/>
                            <field name="planned_date_start"/>
                            <field name="planned_date_end"/>
                        </group>
                        <group>
                            <field name="amount_total" widget="monetary"/>
                            <field name="currency_id" invisible="1"/>
                            <field name="company_id" invisible="1"/>
                            <field name="actual_date_start" readonly="1"/>
                            <field name="actual_date_end" readonly="1"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Stops">
                            <field name="stop_ids" mode="tree,form">
                                <tree string="Stops" editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="stop_type"/>
                                    <field name="address_id"/>
                                    <field name="planned_date"/>
                                    <field name="actual_date"/>
                                    <field name="state"/>
                                </tree>
                                <form string="Stop">
                                    <group>
                                        <field name="order_id" invisible="1"/>
                                        <field name="stop_type"/>
                                        <field name="sequence"/>
                                        <field name="address_id"/>
                                        <field name="planned_date"/>
                                        <field name="actual_date"/>
                                        <field name="state"/>
                                    </group>
                                    <group string="Stop Lines">
                                        <field name="line_ids" mode="tree,form">
                                            <tree string="Stop Lines" editable="bottom">
                                                <field name="customer_id"/>
                                                <field name="product_desc"/>
                                                <field name="quantity"/>
                                                <field name="weight"/>
                                            </tree>
                                            <form>
                                                <group>
                                                    <field name="customer_id"/>
                                                    <field name="product_desc"/>
                                                    <field name="quantity"/>
                                                    <field name="weight"/>
                                                </group>
                                            </form>
                                        </field>
                                    </group>
                                    <group string="Notes">
                                        <field name="notes"/>
                                    </group>
                                </form>
                            </field>
                        </page>
                        <page string="Vehicle &amp; Driver">
                            <field name="assignment_ids" mode="tree,form">
                                <tree string="Assignments" editable="bottom">
                                    <field name="vehicle_id"/>
                                    <field name="external_vehicle_plate"/>
                                    <field name="driver_id"/>
                                    <field name="assignment_date"/>
                                    <field name="state"/>
                                </tree>
                                <form>
                                    <group>
                                        <field name="order_id" invisible="1"/>
                                        <field name="vehicle_id"
                                               attrs="{'required': [('external_vehicle_plate', '=', False)]}"/>
                                        <field name="external_vehicle_plate"
                                               attrs="{'required': [('vehicle_id', '=', False)]}"/>
                                        <field name="driver_id"/>
                                        <field name="assignment_date"/>
                                    </group>
                                </form>
                            </field>
                        </page>
                        <page string="Invoices">
                            <field name="invoice_ids"
                                   context="{'default_move_type': 'out_invoice'}"/>
                        </page>
                        <page string="Notes">
                            <field name="notes"/>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_vsl_transport_order_search" model="ir.ui.view">
        <field name="name">vsl.transport.order.search</field>
        <field name="model">vsl.transport.order</field>
        <field name="arch" type="xml">
            <search string="Search Transport Orders">
                <field name="name"/>
                <field name="customer_id"/>
                <filter name="draft" string="Draft" domain="[('state', '=', 'draft')]"/>
                <filter name="open" string="Open" domain="[('state', '=', 'open')]"/>
                <filter name="assigned" string="Assigned" domain="[('state', '=', 'assigned')]"/>
                <filter name="loading" string="Loading" domain="[('state', '=', 'loading')]"/>
                <filter name="in_transit" string="In Transit" domain="[('state', '=', 'in_transit')]"/>
                <filter name="delivered" string="Delivered" domain="[('state', '=', 'delivered')]"/>
                <filter name="invoiced" string="Invoiced" domain="[('state', '=', 'invoiced')]"/>
                <separator/>
                <filter name="active" string="Active"
                        domain="[('state', 'not in', ['cancelled', 'invoiced'])]"/>
                <group expand="0" string="Group By">
                    <filter name="group_state" string="Status"
                            context="{'group_by': 'state'}"/>
                    <filter name="group_customer" string="Customer"
                            context="{'group_by': 'customer_id'}"/>
                </group>
            </search>
        </field>
    </record>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/views/transport_order_views.xml`

- [ ] **Step 2: Write transport_stop_views.xml (standalone views for stop and line)**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_transport_stop_tree" model="ir.ui.view">
        <field name="name">vsl.transport.stop.tree</field>
        <field name="model">vsl.transport.stop</field>
        <field name="arch" type="xml">
            <tree string="Stops">
                <field name="order_id"/>
                <field name="sequence" widget="handle"/>
                <field name="stop_type"/>
                <field name="address_id"/>
                <field name="planned_date"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/views/transport_stop_views.xml`

- [ ] **Step 3: Write vehicle_assignment_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_vehicle_assignment_tree" model="ir.ui.view">
        <field name="name">vsl.vehicle.assignment.tree</field>
        <field name="model">vsl.vehicle.assignment</field>
        <field name="arch" type="xml">
            <tree string="Vehicle Assignments">
                <field name="order_id"/>
                <field name="vehicle_id"/>
                <field name="external_vehicle_plate"/>
                <field name="driver_id"/>
                <field name="assignment_date"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/views/vehicle_assignment_views.xml`

- [ ] **Step 4: Commit**

```bash
git add vsl_tasimacilik/views/transport_order_views.xml vsl_tasimacilik/views/transport_stop_views.xml vsl_tasimacilik/views/vehicle_assignment_views.xml
git commit -m "feat: add views for transport order, stops, and vehicle assignment"
```

---

## Task 11: Menu Structure

**Files:**
- Create: `vsl_tasimacilik/views/menu_views.xml`

- [ ] **Step 1: Write menu_views.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Root menu -->
    <menuitem id="menu_vsl_transport_root"
              name="Transport"
              sequence="90"
              web_icon="vsl_tasimacilik,static/description/icon.png"/>

    <!-- Transport Orders -->
    <menuitem id="menu_vsl_transport_order"
              name="Transport Orders"
              parent="menu_vsl_transport_root"
              action="action_vsl_transport_order"
              sequence="10"/>

    <record id="action_vsl_transport_order" model="ir.actions.act_window">
        <field name="name">Transport Orders</field>
        <field name="res_model">vsl.transport.order</field>
        <field name="view_mode">tree,form</field>
        <field name="search_view_id" ref="view_vsl_transport_order_search"/>
    </record>

    <!-- Carrier Documents (under Transport menu) -->
    <menuitem id="menu_vsl_carrier_document"
              name="Carrier Documents"
              parent="menu_vsl_transport_root"
              action="action_vsl_carrier_document"
              sequence="20"/>

    <!-- Vehicle Assignments (under Transport menu) -->
    <record id="action_vsl_vehicle_assignment" model="ir.actions.act_window">
        <field name="name">Vehicle Assignments</field>
        <field name="res_model">vsl.vehicle.assignment</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_vsl_vehicle_assignment"
              name="Vehicle Assignments"
              parent="menu_vsl_transport_root"
              action="action_vsl_vehicle_assignment"
              sequence="30"/>

    <!-- Configuration menu -->
    <menuitem id="menu_vsl_transport_config"
              name="Configuration"
              parent="menu_vsl_transport_root"
              sequence="90"
              groups="vsl_tasimacilik.group_vsl_transport_manager"/>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/views/menu_views.xml`

- [ ] **Step 2: Commit**

```bash
git add vsl_tasimacilik/views/menu_views.xml
git commit -m "feat: add menu structure for transport module"
```

---

## Task 12: Invoice Creation Wizard

**Files:**
- Create: `vsl_tasimacilik/wizards/__init__.py`
- Create: `vsl_tasimacilik/wizards/transport_invoice_wizard.py`
- Create: `vsl_tasimacilik/wizards/transport_invoice_wizard.xml`
- Modify: `vsl_tasimacilik/__init__.py`

- [ ] **Step 1: Create wizards/__init__.py**

```python
from . import transport_invoice_wizard
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/wizards/__init__.py`

- [ ] **Step 2: Write transport_invoice_wizard.py**

```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VslTransportInvoiceWizard(models.TransientModel):
    _name = "vsl.transport.invoice.wizard"
    _description = "Transport Invoice Wizard"

    order_id = fields.Many2one(
        "vsl.transport.order",
        string="Transport Order",
        required=True,
        readonly=True,
    )

    # Customer invoice fields
    customer_invoice = fields.Boolean(string="Create Customer Invoice", default=True)
    customer_invoice_amount = fields.Monetary(
        string="Customer Invoice Amount",
        currency_field="currency_id",
    )
    customer_invoice_description = fields.Text(
        string="Customer Invoice Description",
    )

    # Supplier invoice fields
    supplier_invoice = fields.Boolean(string="Create Supplier Invoice", default=True)
    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier / Carrier",
        domain="[('is_carrier', '=', True)]",
    )
    supplier_invoice_amount = fields.Monetary(
        string="Supplier Invoice Amount",
        currency_field="currency_id",
    )
    supplier_invoice_description = fields.Text(
        string="Supplier Invoice Description",
    )

    # Extra line items
    extra_line_ids = fields.One2many(
        "vsl.transport.invoice.wizard.line",
        "wizard_id",
        string="Extra Items",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get("active_id"):
            order = self.env["vsl.transport.order"].browse(
                self.env.context["active_id"]
            )
            defaults["order_id"] = order.id
            defaults["customer_invoice_amount"] = order.amount_total
            if order.assignment_ids:
                defaults["supplier_id"] = order.assignment_ids[0].driver_id.id
        return defaults

    def action_create_invoices(self):
        self.ensure_one()
        order = self.order_id

        if order.state != "delivered":
            raise UserError(
                _("Invoices can only be created for delivered orders.")
            )

        Partner = self.env["res.partner"]
        customer = order.customer_id

        if not customer:
            raise UserError(_("No customer set on the transport order."))

        # Prepare extra lines
        extra_lines = []
        for line in self.extra_line_ids:
            extra_lines.append((0, 0, {
                "name": line.description or _("Extra Charge"),
                "quantity": line.quantity,
                "price_unit": line.price_unit,
            }))

        # Create customer invoice
        if self.customer_invoice:
            cus_inv_lines = [(0, 0, {
                "name": self.customer_invoice_description or _("Transport Service"),
                "quantity": 1,
                "price_unit": self.customer_invoice_amount or 0,
            })] + extra_lines
            customer_invoice = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": customer.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": cus_inv_lines,
            })
            order.invoice_ids = [(4, customer_invoice.id)]

        # Create supplier invoice
        if self.supplier_invoice and self.supplier_id:
            sup_inv_lines = [(0, 0, {
                "name": self.supplier_invoice_description or _("Transport Service"),
                "quantity": 1,
                "price_unit": self.supplier_invoice_amount or 0,
            })] + (
                [(0, 0, {
                    "name": l.description or _("Extra Charge"),
                    "quantity": l.quantity,
                    "price_unit": l.price_unit,
                }) for l in self.extra_line_ids]
            )
            supplier_invoice = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": self.supplier_id.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": sup_inv_lines,
            })
            order.invoice_ids = [(4, supplier_invoice.id)]

        if self.customer_invoice or self.supplier_invoice:
            order.state = "invoiced"

        return {"type": "ir.actions.act_window_close"}


class VslTransportInvoiceWizardLine(models.TransientModel):
    _name = "vsl.transport.invoice.wizard.line"
    _description = "Transport Invoice Wizard Line"

    wizard_id = fields.Many2one(
        "vsl.transport.invoice.wizard",
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    description = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Monetary(string="Unit Price", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        related="wizard_id.currency_id",
    )
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/wizards/transport_invoice_wizard.py`

- [ ] **Step 3: Write transport_invoice_wizard.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="view_vsl_transport_invoice_wizard" model="ir.ui.view">
        <field name="name">vsl.transport.invoice.wizard.form</field>
        <field name="model">vsl.transport.invoice.wizard</field>
        <field name="arch" type="xml">
            <form string="Create Invoices">
                <group string="Customer Invoice">
                    <field name="customer_invoice"/>
                    <field name="customer_invoice_amount"
                           widget="monetary"
                           attrs="{'required': [('customer_invoice', '=', True)], 'invisible': [('customer_invoice', '=', False)]}"/>
                    <field name="customer_invoice_description"
                           attrs="{'invisible': [('customer_invoice', '=', False)]}"/>
                </group>
                <group string="Supplier Invoice">
                    <field name="supplier_invoice"/>
                    <field name="supplier_id"
                           attrs="{'required': [('supplier_invoice', '=', True)], 'invisible': [('supplier_invoice', '=', False)]}"/>
                    <field name="supplier_invoice_amount"
                           widget="monetary"
                           attrs="{'required': [('supplier_invoice', '=', True)], 'invisible': [('supplier_invoice', '=', False)]}"/>
                    <field name="supplier_invoice_description"
                           attrs="{'invisible': [('supplier_invoice', '=', False)]}"/>
                </group>
                <group string="Extra Line Items (Insurance, Customs, Storage, etc.)">
                    <field name="extra_line_ids" mode="tree">
                        <tree string="Extra Items" editable="bottom">
                            <field name="description"/>
                            <field name="quantity"/>
                            <field name="price_unit" widget="monetary"/>
                        </tree>
                    </field>
                </group>
                <footer>
                    <button name="action_create_invoices" type="object"
                            string="Create Invoices" class="btn-primary"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_vsl_transport_invoice_wizard" model="ir.actions.act_window">
        <field name="name">Create Invoices</field>
        <field name="res_model">vsl.transport.invoice.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
        <field name="binding_model_id" ref="model_vsl_transport_order"/>
        <field name="binding_view_types">form</field>
    </record>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/wizards/transport_invoice_wizard.xml`

- [ ] **Step 4: Update root __init__.py to import wizards**

```python
from . import models
from . import wizards
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/__init__.py`

- [ ] **Step 5: Ensure transport_invoice_wizard.xml is in manifest data**

The `__manifest__.py` already lists `wizards/transport_invoice_wizard.xml` in the `data` array from Task 1.

- [ ] **Step 6: Commit**

```bash
git add vsl_tasimacilik/wizards/ vsl_tasimacilik/__init__.py
git commit -m "feat: add invoice creation wizard for dual invoicing"
```

---

## Task 13: Transport Order Report

**Files:**
- Create: `vsl_tasimacilik/reports/__init__.py`
- Create: `vsl_tasimacilik/reports/transport_order_report.py`
- Create: `vsl_tasimacilik/reports/transport_order_report.xml`
- Modify: `vsl_tasimacilik/__init__.py`

- [ ] **Step 1: Create reports/__init__.py**

```python
from . import transport_order_report
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/reports/__init__.py`

- [ ] **Step 2: Write transport_order_report.py**

```python
from odoo import api, fields, models


class VslTransportOrderReport(models.AbstractModel):
    _name = "report.vsl_tasimacilik.report_transport_order"
    _description = "Transport Order Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["vsl.transport.order"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "vsl.transport.order",
            "docs": docs,
            "data": data,
        }
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/reports/transport_order_report.py`

- [ ] **Step 3: Write transport_order_report.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="action_report_transport_order" model="ir.actions.report">
        <field name="name">Transport Order</field>
        <field name="model">vsl.transport.order</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">vsl_tasimacilik.report_transport_order</field>
        <field name="report_file">vsl_tasimacilik.report_transport_order</field>
        <field name="binding_model_id" ref="model_vsl_transport_order"/>
        <field name="binding_view_types">form</field>
    </record>

    <template id="report_transport_order_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="web.external_layout">
                    <div class="page">
                        <h2>Transport Order: <span t-field="doc.name"/></h2>

                        <table class="table table-bordered">
                            <tr>
                                <th>Customer</th>
                                <td t-field="doc.customer_id.name"/>
                            </tr>
                            <tr>
                                <th>Status</th>
                                <td t-field="doc.state"/>
                            </tr>
                            <tr>
                                <th>Planned Dates</th>
                                <td>
                                    <t t-field="doc.planned_date_start"/> - <t t-field="doc.planned_date_end"/>
                                </td>
                            </tr>
                            <tr>
                                <th>Total Amount</th>
                                <td t-field="doc.amount_total"/>
                            </tr>
                        </table>

                        <h3>Stops</h3>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Seq</th>
                                    <th>Type</th>
                                    <th>Address</th>
                                    <th>Planned</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr t-foreach="doc.stop_ids" t-as="stop">
                                    <td t-field="stop.sequence"/>
                                    <td t-field="stop.stop_type"/>
                                    <td t-field="stop.address_id.name"/>
                                    <td t-field="stop.planned_date"/>
                                    <td t-field="stop.state"/>
                                </tr>
                            </tbody>
                        </table>

                        <h3>Notes</h3>
                        <p t-field="doc.notes"/>
                    </div>
                </t>
            </t>
        </t>
    </template>

</odoo>
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/reports/transport_order_report.xml`

- [ ] **Step 4: Update root __init__.py to import reports**

```python
from . import models
from . import wizards
from . import reports
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/__init__.py`

- [ ] **Step 5: Commit**

```bash
git add vsl_tasimacilik/reports/ vsl_tasimacilik/__init__.py
git commit -m "feat: add transport order PDF report"
```

---

## Task 14: i18n (Translations)

**Files:**
- Create: `vsl_tasimacilik/i18n/vsl_tasimacilik.pot`
- Create: `vsl_tasimacilik/i18n/tr.po`

- [ ] **Step 1: Write vsl_tasimacilik.pot**

```po
# Translation of Odoo Module.
# Copyright (C) 2026 VSL
# This file is distributed under the same license as the Odoo module.
msgid ""
msgstr ""
"Project-Id-Version: Odoo 19.0\n"
"POT-Creation-Date: 2026-05-07\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_order
msgid "Transport Order"
msgstr ""

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_stop
msgid "Transport Stop"
msgstr ""

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_stop_line
msgid "Transport Stop Line"
msgstr ""

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_vehicle_assignment
msgid "Vehicle Assignment"
msgstr ""

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_carrier_document
msgid "Carrier Document"
msgstr ""

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_invoice_wizard
msgid "Transport Invoice Wizard"
msgstr ""
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/i18n/vsl_tasimacilik.pot`

- [ ] **Step 2: Write tr.po**

```po
# Translation of Odoo Module.
# Copyright (C) 2026 VSL
msgid ""
msgstr ""
"Project-Id-Version: Odoo 19.0\n"
"POT-Creation-Date: 2026-05-07\n"
"PO-Revision-Date: 2026-05-07\n"
"Language-Team: Turkish\n"
"Language: tr\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_order
msgid "Transport Order"
msgstr "Sevkiyat Emri"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_stop
msgid "Transport Stop"
msgstr "Sevkiyat Durağı"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_stop_line
msgid "Transport Stop Line"
msgstr "Durak Kalemi"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_vehicle_assignment
msgid "Vehicle Assignment"
msgstr "Araç Ataması"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_carrier_document
msgid "Carrier Document"
msgstr "Tedarikçi Evrakı"

#. module: vsl_tasimacilik
#: model:ir.model,name:vsl_tasimacilik.model_vsl_transport_invoice_wizard
msgid "Transport Invoice Wizard"
msgstr "Sevkiyat Fatura Sihirbazı"
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/i18n/tr.po`

- [ ] **Step 3: Commit**

```bash
git add vsl_tasimacilik/i18n/
git commit -m "feat: add i18n files with Turkish translations"
```

---

## Task 15: Tests

**Files:**
- Create: `vsl_tasimacilik/tests/__init__.py`
- Create: `vsl_tasimacilik/tests/test_transport_order.py`

- [ ] **Step 1: Create tests/__init__.py**

```python
from . import test_transport_order
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/tests/__init__.py`

- [ ] **Step 2: Write test_transport_order.py**

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError


class TestTransportOrder(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Currency = self.env["res.currency"]
        self.currency_try = self.Currency.search(
            [("name", "=", "TRY")], limit=1
        )
        if not self.currency_try:
            self.currency_try = self.Currency.create({
                "name": "TRY",
                "symbol": "₺",
            })

        self.customer = self.env["res.partner"].create({
            "name": "Test Customer",
        })
        self.carrier = self.env["res.partner"].create({
            "name": "Test Carrier",
            "is_carrier": True,
        })
        self.load_address = self.env["res.partner"].create({
            "name": "Loading Address",
            "type": "delivery",
        })
        self.unload_address = self.env["res.partner"].create({
            "name": "Unloading Address",
            "type": "delivery",
        })

    def _create_order(self, state="draft"):
        vals = {
            "customer_id": self.customer.id,
            "amount_total": 5000.0,
            "currency_id": self.currency_try.id,
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
        }
        return self.env["vsl.transport.order"].create(vals)

    def test_create_order(self):
        order = self._create_order()
        self.assertTrue(order.name)
        self.assertNotEqual(order.name, "New")
        self.assertEqual(order.state, "draft")

    def test_confirm_order(self):
        order = self._create_order()
        order.action_confirm()
        self.assertEqual(order.state, "open")

    def test_confirm_fails_without_stops(self):
        order = self.env["vsl.transport.order"].create({
            "customer_id": self.customer.id,
        })
        with self.assertRaises(UserError):
            order.action_confirm()

    def test_assign_vehicle(self):
        order = self._create_order("open")
        assignment = self.env["vsl.vehicle.assignment"].create({
            "order_id": order.id,
            "external_vehicle_plate": "34ABC123",
            "driver_id": self.carrier.id,
        })
        order.state = "assigned"
        self.assertEqual(order.state, "assigned")
        self.assertEqual(assignment.state, "assigned")

    def test_assignment_requires_vehicle_or_plate(self):
        order = self._create_order("open")
        with self.assertRaises(ValidationError):
            self.env["vsl.vehicle.assignment"].create({
                "order_id": order.id,
                "driver_id": self.carrier.id,
            })

    def test_start_loading_requires_assignment(self):
        order = self._create_order("open")
        with self.assertRaises(UserError):
            order.action_start_loading()

    def test_full_workflow(self):
        order = self._create_order()
        self.assertEqual(order.state, "draft")

        order.action_confirm()
        self.assertEqual(order.state, "open")

        self.env["vsl.vehicle.assignment"].create({
            "order_id": order.id,
            "external_vehicle_plate": "34XYZ789",
            "driver_id": self.carrier.id,
        })
        order.state = "assigned"
        self.assertEqual(order.state, "assigned")

        order.action_start_loading()
        self.assertEqual(order.state, "loading")

        for stop in order.stop_ids.filtered(lambda s: s.stop_type == "loading"):
            stop.state = "done"
        order.action_depart()
        self.assertEqual(order.state, "in_transit")

        for stop in order.stop_ids.filtered(lambda s: s.stop_type == "unloading"):
            stop.state = "done"
        order.action_deliver()
        self.assertEqual(order.state, "delivered")

    def test_cancel_order(self):
        order = self._create_order("open")
        order.action_cancel()
        self.assertEqual(order.state, "cancelled")

    def test_cannot_cancel_invoiced(self):
        order = self._create_order("delivered")
        order.state = "invoiced"
        with self.assertRaises(UserError):
            order.action_cancel()

    def test_parsiyel_stop_lines(self):
        order = self._create_order()
        stop = order.stop_ids[0]
        customer2 = self.env["res.partner"].create({"name": "Second Customer"})
        self.env["vsl.transport.stop.line"].create({
            "stop_id": stop.id,
            "customer_id": self.customer.id,
            "product_desc": "Nuts",
            "quantity": 10,
            "weight": 500.0,
        })
        self.env["vsl.transport.stop.line"].create({
            "stop_id": stop.id,
            "customer_id": customer2.id,
            "product_desc": "Pistachios",
            "quantity": 5,
            "weight": 250.0,
        })
        self.assertEqual(len(stop.line_ids), 2)


class TestCarrierDocument(TransactionCase):

    def setUp(self):
        super().setUp()
        self.carrier = self.env["res.partner"].create({
            "name": "Doc Carrier",
            "is_carrier": True,
        })

    def test_create_document(self):
        attachment = self.env["ir.attachment"].create({
            "name": "test_license.pdf",
            "datas": b"dummy",
        })
        doc = self.env["vsl.carrier.document"].create({
            "carrier_id": self.carrier.id,
            "doc_type": "driving_license",
            "attachment_id": attachment.id,
            "issue_date": "2026-01-01",
            "expiry_date": "2028-01-01",
        })
        self.assertEqual(doc.state, "valid")

    def test_document_expiry(self):
        from odoo import fields
        attachment = self.env["ir.attachment"].create({
            "name": "expired_license.pdf",
            "datas": b"dummy",
        })
        doc = self.env["vsl.carrier.document"].create({
            "carrier_id": self.carrier.id,
            "doc_type": "driving_license",
            "attachment_id": attachment.id,
            "expiry_date": "2020-01-01",
        })
        self.assertEqual(doc.state, "expired")
```

Write to `~/dev/vsl-tms-odoo/vsl_tasimacilik/tests/test_transport_order.py`

- [ ] **Step 3: Run tests to verify they pass**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml exec web odoo --test-enable --stop-after-init -d postgres -i vsl_tasimacilik --log-level=test
```

Expected: Tests pass with OK status.

- [ ] **Step 4: Commit**

```bash
git add vsl_tasimacilik/tests/
git commit -m "test: add unit tests for transport order and carrier document"
```

---

## Task 16: Module Installation and Verification

**Files:** None created — this is a verification task.

- [ ] **Step 1: Restart Odoo container and install module**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml restart web
```

Wait for Odoo to restart (~30 seconds), then:

```bash
docker compose -f ~/dev/odoo/docker-compose.yml exec web odoo -d postgres -i vsl_tasimacilik --stop-after-init
```

Expected: Module installs without errors.

- [ ] **Step 2: Verify module appears in Apps menu**

Open `http://localhost:8069/web`, login, navigate to Apps, search for "Tasimacilik". Confirm module appears and shows as installed.

- [ ] **Step 3: Verify Transport menu appears**

Navigate to the top menu bar. Confirm "Transport" menu is visible with sub-items: Transport Orders, Carrier Documents, Vehicle Assignments.

---

## Task 17: Final Integration Check

**Files:** None — verification only.

- [ ] **Step 1: Create a test carrier**

Navigate to Contacts, create a new contact named "Test Kamyoncu", check "Carrier / Supplier" checkbox, fill Tax Office and Tax Number, save. Add a carrier document (Driving License) with a test attachment.

- [ ] **Step 2: Create a full transport order**

Navigate to Transport Orders, create new. Select customer, add a loading stop and an unloading stop. Add stop lines with product descriptions. Save. Click "Confirm" to move to Open state.

- [ ] **Step 3: Assign vehicle and driver**

On the "Vehicle & Driver" tab, create an assignment with external plate and driver (the carrier created above). Move order to Assigned state.

- [ ] **Step 4: Complete the workflow**

Click "Start Loading" → set loading stops to "Done" → "Depart" → set unloading stops to "Done" → "Deliver" → "Create Invoices" wizard → create customer and supplier invoices. Verify invoices appear on the Invoices tab.

- [ ] **Step 5: Run full test suite again**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml exec web odoo --test-enable --stop-after-init -d postgres -i vsl_tasimacilik --log-level=test
```

Expected: All tests pass.

- [ ] **Step 6: Commit any final fixes**

```bash
git status
git add -A
git commit -m "fix: final integration fixes and verification"
```

