{
    "name": "vsl Transport",
    "summary": "Uçtan uca sevkiyat yönetim modülü",
    "description": """
Türkiye'deki lojistik firmaları için uçtan uca sevkiyat yönetimi.
Özellikler: Sevkiyat emri, çoklu/parsiyel yükleme-boşaltma,
araç ve sürücü ataması (kendi filo + dış tedarikçi),
tedarikçi evrak yönetimi, geçmiş rota fiyat sorgulama,
çift yönlü fatura oluşturma.
    """,
    "version": "19.0.1.0.0",
    "category": "Transportation",
    "website": "https://www.vsl.com.tr",
    "author": "VSL",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "mail", "contacts", "fleet", "account"],
    "data": [
        "security/transport_security.xml",
        "security/ir.model.access.csv",
        "data/transport_data.xml",
        "data/vsl_reference_data.xml",
        "wizards/transport_invoice_wizard.xml",
        "views/transport_order_views.xml",
        "views/transport_stop_views.xml",
        "views/vehicle_assignment_views.xml",
        "views/carrier_document_views.xml",
        "views/res_partner_views.xml",
        "views/menu_views.xml",
        "reports/transport_order_report.xml",
    ],
}
