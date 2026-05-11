import base64

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
            self.currency_try = self.env.ref("base.TRY", raise_if_not_found=False)
        if not self.currency_try:
            self.currency_try = self.env.company.currency_id

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

    def test_cargo_product_domain(self):
        """Cargo category ürünleri stop line'da seçilebilir olmalı,
        cargo olmayan ürünler seçilememeli."""
        cargo_categ = self.env.ref('vsl_transport.product_category_cargo', raise_if_not_found=False)
        self.assertTrue(cargo_categ, "Cargo category should exist")

        cargo_product = self.env['product.product'].create({
            'name': 'Test Cargo Product',
            'categ_id': cargo_categ.id,
            'type': 'product',
        })

        normal_product = self.env['product.product'].create({
            'name': 'Test Normal Product',
            'type': 'product',
        })

        stop_line = self.env['vsl.transport.stop.line']
        domain = stop_line._get_cargo_product_domain()
        self.assertIn('categ_id', str(domain))
        self.assertIn('child_of', str(domain))

        cargo_products = self.env['product.product'].search(domain)
        self.assertIn(cargo_product.id, cargo_products.ids)
        self.assertNotIn(normal_product.id, cargo_products.ids)


class TestCarrierDocument(TransactionCase):

    def setUp(self):
        super().setUp()
        self.carrier = self.env["res.partner"].create({
            "name": "Doc Carrier",
            "is_carrier": True,
        })

    def test_create_document(self):
        doc = self.env["vsl.carrier.document"].create({
            "carrier_id": self.carrier.id,
            "doc_type": "driving_license",
            "datas": base64.b64encode(b"dummy license content"),
            "issue_date": "2026-01-01",
            "expiry_date": "2028-01-01",
        })
        self.assertEqual(doc.state, "valid")

    def test_document_expiry(self):
        doc = self.env["vsl.carrier.document"].create({
            "carrier_id": self.carrier.id,
            "doc_type": "driving_license",
            "datas": base64.b64encode(b"dummy license content"),
            "expiry_date": "2020-01-01",
        })
        self.assertEqual(doc.state, "expired")
