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
