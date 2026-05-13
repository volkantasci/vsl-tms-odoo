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
    customer_product_id = fields.Many2one(
        "product.product",
        string="Product / Service",
        domain="[('type', '=', 'service')]",
    )
    customer_tax_ids = fields.Many2many(
        "account.tax",
        "vsl_invoice_wizard_customer_tax_rel",
        "wizard_id",
        "tax_id",
        string="Tax",
    )
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
        domain="[('parent_id', '=', False)]",
    )
    supplier_product_id = fields.Many2one(
        "product.product",
        string="Product / Service",
        domain="[('type', '=', 'service')]",
    )
    supplier_tax_ids = fields.Many2many(
        "account.tax",
        "vsl_invoice_wizard_supplier_tax_rel",
        "wizard_id",
        "tax_id",
        string="Tax",
    )
    supplier_invoice_amount = fields.Monetary(
        string="Supplier Invoice Amount",
        currency_field="currency_id",
    )
    supplier_invoice_description = fields.Text(
        string="Supplier Invoice Description",
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

        if order.state not in ("delivered", "invoiced"):
            raise UserError(
                _("Invoices can only be created for delivered orders.")
            )

        if order.state == "invoiced" and order.invoice_ids:
            order.invoice_ids.unlink()
            order.state = "delivered"

        customer = order.customer_id
        if not customer:
            raise UserError(_("No customer set on the transport order."))

        if self.customer_invoice:
            customer_invoice_line_vals = {
                "name": self.customer_invoice_description or _("Transport Service"),
                "quantity": 1,
                "price_unit": self.customer_invoice_amount or 0,
            }
            if self.customer_product_id:
                customer_invoice_line_vals["product_id"] = self.customer_product_id.id
            if self.customer_tax_ids:
                customer_invoice_line_vals["tax_ids"] = [(6, 0, self.customer_tax_ids.ids)]
            customer_invoice = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": customer.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [(0, 0, customer_invoice_line_vals)],
            })
            order.invoice_ids = [(4, customer_invoice.id)]

        if self.supplier_invoice and self.supplier_id:
            supplier_invoice_line_vals = {
                "name": self.supplier_invoice_description or _("Transport Service"),
                "quantity": 1,
                "price_unit": self.supplier_invoice_amount or 0,
            }
            if self.supplier_product_id:
                supplier_invoice_line_vals["product_id"] = self.supplier_product_id.id
            if self.supplier_tax_ids:
                supplier_invoice_line_vals["tax_ids"] = [(6, 0, self.supplier_tax_ids.ids)]
            supplier_invoice = self.env["account.move"].create({
                "move_type": "in_invoice",
                "partner_id": self.supplier_id.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [(0, 0, supplier_invoice_line_vals)],
            })
            order.invoice_ids = [(4, supplier_invoice.id)]

        if self.customer_invoice or self.supplier_invoice:
            order.state = "invoiced"

        return {"type": "ir.actions.act_window_close"}
