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

    customer_invoice = fields.Boolean(string="Create Customer Invoice", default=True)
    customer_invoice_amount = fields.Monetary(
        string="Customer Invoice Amount",
        currency_field="currency_id",
    )
    customer_invoice_description = fields.Text(
        string="Customer Invoice Description",
    )

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

        customer = order.customer_id
        if not customer:
            raise UserError(_("No customer set on the transport order."))

        if self.customer_invoice:
            cus_inv_lines = [(0, 0, {
                "name": self.customer_invoice_description or _("Transport Service"),
                "quantity": 1,
                "price_unit": self.customer_invoice_amount or 0,
            })]
            for line in self.extra_line_ids:
                cus_inv_lines.append((0, 0, {
                    "name": line.description or _("Extra Charge"),
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                }))
            customer_invoice = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": customer.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": cus_inv_lines,
            })
            order.invoice_ids = [(4, customer_invoice.id)]

        if self.supplier_invoice and self.supplier_id:
            sup_inv_lines = [(0, 0, {
                "name": self.supplier_invoice_description or _("Transport Service"),
                "quantity": 1,
                "price_unit": self.supplier_invoice_amount or 0,
            })]
            for line in self.extra_line_ids:
                sup_inv_lines.append((0, 0, {
                    "name": line.description or _("Extra Charge"),
                    "quantity": line.quantity,
                    "price_unit": line.price_unit,
                }))
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
