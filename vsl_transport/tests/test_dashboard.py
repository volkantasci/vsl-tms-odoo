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

        self.assertGreaterEqual(dashboard.total_orders, 3)
        self.assertGreaterEqual(dashboard.open_orders, 1)
        self.assertGreaterEqual(dashboard.loading_orders, 1)
        self.assertGreaterEqual(dashboard.in_transit_orders, 1)
