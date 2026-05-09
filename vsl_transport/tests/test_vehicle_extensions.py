import base64

from odoo.tests.common import TransactionCase


class TestVehicleExtensions(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ownership = self.env["vsl.vehicle.ownership"].create({"name": "Öz Mal"})
        self.model = self.env["fleet.vehicle.model"].create({
            "name": "Test Model",
            "brand_id": self.env["fleet.vehicle.model.brand"].create({"name": "Test Brand"}).id,
        })
        self.vehicle = self.env["fleet.vehicle"].create({
            "name": "Test Araç",
            "license_plate": "34TEST123",
            "model_id": self.model.id,
            "vsl_ownership_id": self.ownership.id,
            "vsl_capacity": 20.0,
            "vsl_transport_status": "available",
        })

    def test_vehicle_transport_fields(self):
        self.assertEqual(self.vehicle.vsl_transport_status, "available")
        self.assertEqual(self.vehicle.vsl_capacity, 20.0)

    def test_vehicle_document(self):
        doc = self.env["vsl.vehicle.document"].create({
            "vehicle_id": self.vehicle.id,
            "doc_type": "insurance",
            "datas": base64.b64encode(b"dummy insurance content"),
            "expiry_date": "2028-01-01",
        })
        self.assertEqual(doc.state, "valid")

    def test_vehicle_document_expired(self):
        doc = self.env["vsl.vehicle.document"].create({
            "vehicle_id": self.vehicle.id,
            "doc_type": "insurance",
            "datas": base64.b64encode(b"dummy insurance content"),
            "expiry_date": "2020-01-01",
        })
        self.assertEqual(doc.state, "expired")
