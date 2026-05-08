# vsl-Taşımacılık

Odoo 19 için geliştirilmiş, Türkiye lojistik sektörüne özel uçtan uca sevkiyat yönetim modülü.

## Özellikler

- **Sevkiyat Emri Yönetimi** — Taslak → Açık → Atandı → Yüklemede → Yolda → Teslim Edildi → Faturalandı durum akışı
- **Çoklu/Parsiyel Yükleme** — Aynı araca birden çok müşterinin malını yükleme, çok duraklı rota planlama
- **Araç ve Sürücü Ataması** — Kendi filo araçları (fleet.vehicle) veya harici nakliyeci plakası ile
- **Tedarikçi Evrak Yönetimi** — Ehliyet, ruhsat, sigorta, SRC belgesi takibi ve son kullanma kontrolü
- **Geçmiş Fiyat Sorgulama** — Aynı rotadaki geçmiş sevkiyatların fiyatlarına hızlı erişim
- **Çift Yönlü Fatura** — Müşteri faturası (out_invoice) ve tedarikçi faturası (in_invoice) oluşturma sihirbazı
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
| `vsl.vehicle.assignment` | Araç ve sürücü ataması |
| `vsl.carrier.document` | Tedarikçi evrakı |
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
│   ├── vehicle_assignment.py    # Araç ataması
│   ├── carrier_document.py      # Tedarikçi evrakı
│   └── res_partner.py           # res.partner genişletmesi
├── views/                       # XML görünüm tanımları
│   ├── transport_order_views.xml
│   ├── transport_stop_views.xml
│   ├── vehicle_assignment_views.xml
│   ├── carrier_document_views.xml
│   ├── res_partner_views.xml
│   └── menu_views.xml
├── security/                    # Erişim hakları
│   ├── ir.model.access.csv
│   └── transport_security.xml
├── data/                        # Sequence, varsayılan veriler
│   └── transport_data.xml
├── wizards/                     # Fatura sihirbazı
│   └── transport_invoice_wizard.py
├── reports/                     # PDF raporu
│   └── transport_order_report.py
├── i18n/                        # Çeviriler
│   ├── tr.po
│   └── vsl_transport.pot
└── tests/                       # Birim/entegrasyon testleri
    └── test_transport_order.py
```

## Lisans

LGPL-3
