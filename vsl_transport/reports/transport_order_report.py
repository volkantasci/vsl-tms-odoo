from odoo import api, models


class VslTransportOrderReport(models.AbstractModel):
    _name = "report.vsl_transport.report_transport_order"
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
