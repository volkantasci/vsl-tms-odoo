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
