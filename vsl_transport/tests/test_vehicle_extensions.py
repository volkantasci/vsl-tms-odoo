import base64

from odoo.tests.common import TransactionCase


class TestVehicleExtensions(TransactionCase):

    def setUp(self):
        super().setUp()
        self.vehicle_type = self.env["vsl.vehicle.type"].create({"name": "10 Teker"})
        self.ownership = self.env["vsl.vehicle.ownership"].create({"name": "Oz Mal"})
        self.model = self.env["fleet.vehicle.model"].create({
            "name": "Test Model",
            "brand_id": self.env["fleet.vehicle.model.brand"].create({"name": "Test Brand"}).id,
        })
        self.vehicle = self.env["fleet.vehicle"].create({
            "name": "Test Arac",
            "license_plate": "34TEST123",
            "model_id": self.model.id,
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
