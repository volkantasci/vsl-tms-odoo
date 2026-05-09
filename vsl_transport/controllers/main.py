from odoo import http
from odoo.http import request


class SevkiyatController(http.Controller):

    @http.route('/sevkiyatlar', auth='user', website=True)
    def sevkiyatlar(self):
        action = request.env.ref('vsl_transport.action_vsl_transport_order')
        return request.redirect(f'/web#action={action.id}')

    @http.route('/sevkiyat', auth='user', website=True)
    def sevkiyat(self):
        action = request.env.ref('vsl_transport.action_vsl_transport_order')
        return request.redirect(f'/web#action={action.id}')
