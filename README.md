# vsl-Taşımacılık

Odoo 19 için geliştirilmiş, Türkiye lojistik sektörüne özel uçtan uca sevkiyat yönetim modülü.

## Özellikler

- **Sevkiyat Emri Yönetimi** — Taslak → Açık → Atandı → Yüklemede → Yolda → Teslim Edildi → Faturalandı durum akışı
- **Çoklu/Parsiyel Yükleme** — Aynı araca birden çok müşterinin malını yükleme, çok duraklı rota planlama
- **Araç ve Sürücü Ataması** — Sihirbaz ile araç+sürücü atama, max 2 araç (Çekici+Dorse kombinasyonu), kendi filo veya harici nakliyeci
- **Sürücü Evrak Yönetimi** — Ehliyet, SRC belgesi, psikoteknik takibi ve son kullanma kontrolü
- **Araç Evrak Yönetimi** — Sigorta, ruhsat, muayene takibi ve son kullanma kontrolü
- **Tedarikçi Evrak Yönetimi** — Ehliyet, ruhsat, sigorta, SRC belgesi takibi ve son kullanma kontrolü
- **Geçmiş Fiyat Sorgulama** — Aynı rotadaki geçmiş sevkiyatların fiyatlarına hızlı erişim
- **Çift Yönlü Fatura** — Müşteri faturası (out_invoice) ve tedarikçi faturası (in_invoice) oluşturma sihirbazı
- **Pozisyon Bilgileri** — Yükleme ve boşaltma lokasyonları otomatik hesaplama
- **URL Routing** — Akılda kalıcı `/sevkiyatlar` endpoint
- **Tamamen Türkçe** — Tüm arayüz, hata mesajları ve durum değerleri Türkçe

## Gereksinimler

- Odoo 19.0
- PostgreSQL 16+
- Docker (geliştirme ortamı için)

## Bağımlı Modüller

| Modül | Kullanım Amacı |
|---|---|
| `base` | Temel Odoo altyapısı |
| `mail` | Mesajlaşma, aktivite takibi (mail.thread mixin) |
| `contacts` | Müşteri/tedarikçi yönetimi (res.partner) |
| `fleet` | Filo araç yönetimi (fleet.vehicle) |
| `account` | Fatura ve muhasebe (account.move) |

## Kurulum

```bash
# Modülü Odoo addons dizinine kopyala
cp -r vsl_transport /path/to/odoo/addons/

# Odoo'yu yeniden başlat
docker compose restart web

# Modülü kur
docker compose exec web odoo -d <veritabani> -i vsl_transport --stop-after-init
```

## Geliştirme Ortamı

```bash
# Projeyi klonla
git clone <repo-url> vsl-tms-odoo
cd vsl-tms-odoo

# Docker ile Odoo 19 başlat
cd ~/dev/odoo && docker compose up -d

# Modülü deploy et
cp -r vsl_transport ~/dev/odoo/addons/

# Modülü güncelle (her kod değişikliğinde)
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  -d odoo -u vsl_transport --stop-after-init
docker compose -f ~/dev/odoo/docker-compose.yml up -d web

# Testleri çalıştır
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  --test-enable -d odoo -u vsl_transport --stop-after-init
```

## Veri Modelleri

| Model | Açıklama |
|---|---|
| `vsl.transport.order` | Sevkiyat emri (ana model) |
| `vsl.transport.stop` | Yükleme/boşaltma durağı |
| `vsl.transport.stop.line` | Durak kalemi (parsiyel yükleme) |
| `vsl.vehicle.assignment` | Araç ve sürücü ataması (max 2) |
| `vsl.vehicle.type` | Araç tipi (Kamyonet, 6 Teker, Çekici, Dorse, vb.) |
| `vsl.driver.profile` | Sürücü profili |
| `vsl.driver.document` | Sürücü evrakı (ehliyet/src/psikoteknik) |
| `vsl.vehicle.document` | Araç evrakı (sigorta/ruhsat/muayene) |
| `vsl.carrier.document` | Tedarikçi evrakı |
| `fleet.vehicle` (genişletme) | vsl_vehicle_type_id, vsl_trailer_class_id, vsl_capacity, vsl_transport_status |
| `res.partner` (genişletme) | is_carrier, vergi dairesi, vergi no |

## Durum Makinesi

```
Taslak ──▶ Açık ──▶ Atandı ──▶ Yüklemede ──▶ Yolda ──▶ Teslim Edildi ──▶ Faturalandı
   │         │         │           │            │            │
   ▼         ▼         ▼           ▼            ▼            ▼
 İptal     İptal     İptal       İptal        İptal      (iptal edilemez)
```

## Kullanıcı Grupları

| Grup | Yetkiler |
|---|---|
| **Taşımacılık Kullanıcısı** | Sevkiyat emri oluşturma, düzenleme, görüntüleme |
| **Garaj Operatörü** | Araç/sürücü atama, evrak yönetimi |
| **Taşımacılık Yöneticisi** | Tüm yetkiler, silme, yapılandırma |

## Dizin Yapısı

```
vsl_transport/
├── __manifest__.py              # Modül metadata ve bağımlılıklar
├── __init__.py
├── models/                      # Python veri modelleri
│   ├── transport_order.py       # Sevkiyat emri
│   ├── transport_stop.py        # Durak ve durak kalemi
│   ├── vehicle_assignment.py    # Araç ataması (max 2)
│   ├── vehicle_reference.py     # vsl.vehicle.type, vsl.vehicle.trailer.class vb.
│   ├── driver_profile.py        # Sürücü profili
│   ├── driver_document.py        # Sürücü evrakı
│   ├── vehicle_document.py       # Araç evrakı
│   ├── carrier_document.py       # Tedarikçi evrakı
│   ├── fleet_vehicle.py          # fleet.vehicle genişletmesi
│   └── res_partner.py            # res.partner genişletmesi
├── views/                       # XML görünüm tanımları
│   ├── transport_order_views.xml
│   ├── transport_stop_views.xml
│   ├── vehicle_assignment_views.xml
│   ├── vehicle_reference_views.xml
│   ├── driver_views.xml
│   ├── vehicle_document_views.xml
│   ├── carrier_document_views.xml
│   ├── fleet_vehicle_views.xml
│   ├── res_partner_views.xml
│   └── menu_views.xml
├── controllers/                 # URL routing
│   └── main.py                  # /sevkiyatlar endpoint
├── security/                    # Erişim hakları
│   ├── ir.model.access.csv
│   └── transport_security.xml
├── data/                        # Sequence, varsayılan veriler
│   ├── transport_data.xml
│   ├── vsl_reference_data.xml
│   └── fleet_vehicle_model_data.xml  # Filo araç marka/model verileri
├── wizards/                     # Sihirbazlar
│   ├── transport_invoice_wizard.py
│   └── transport_assignment_wizard.py
├── reports/                     # Raporlar
│   └── transport_order_report.xml
├── i18n/                        # Çeviriler
│   ├── tr.po
│   └── vsl_transport.pot
└── tests/                       # Birim/entegrasyon testleri
    ├── test_transport_order.py
    ├── test_driver.py
    └── test_vehicle_extensions.py
```

## Lisans

LGPL-3
