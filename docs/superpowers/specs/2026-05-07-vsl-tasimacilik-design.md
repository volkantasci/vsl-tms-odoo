# vsl-Taşımacılık Modülü — Tasarım Dokümanı

> Tarih: 2026-05-07 | Durum: Tasarım | Odoo: 19.0

## 1. Amaç ve Kapsam

vsl-Taşımacılık, Türkiye'deki lojistik firmaları için uçtan uca sevkiyat yönetim modülüdür. Hem kendi filosuyla hem de dış tedarikçilerle (kamyoncu) taşıma yapan firmalara hitap eder.

### MVP Kapsamı (İlk aşama)

- Sevkiyat emri yönetimi (açma, planlama, takip)
- Çoklu/parsiyel yükleme ve boşaltma (aynı araçla birden çok müşterinin malı)
- Araç ve sürücü ataması (kendi filo + dış tedarikçi)
- Tedarikçi/kamyoncu evrak yönetimi (ehliyet, ruhsat, sigorta, SRC belgesi)
- Geçmiş rota fiyat sorgulama
- Çift yönlü fatura oluşturma (müşteri faturası + tedarikçi faturası) ve ek kalemler (sigorta, depolama, gümrük)

### Sonraki Aşama (MVP dışı)

- e-Fatura / e-İrsaliye entegrasyonu (l10n_tr_nilvera ile)

## 2. Mimari Yaklaşım

**Yaklaşım B: Özel çekirdek modeller + Odoo entegrasyonu.**

Taşımacılığa özel modeller (`vsl.transport.order`, `vsl.transport.stop`, vb.) sıfırdan yazılır. Müşteri/tedarikçi (`res.partner`), filo araçları (`fleet.vehicle`), faturalar (`account.move`) ve dosya saklama (`ir.attachment`) Odoo'nun mevcut altyapısıyla sağlanır.

## 3. Dizin Hiyerarşisi

```
vsl_tasimacilik/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── transport_order.py
│   ├── transport_stop.py
│   ├── vehicle_assignment.py
│   ├── carrier_document.py
│   └── res_partner.py
├── views/
│   ├── transport_order_views.xml
│   ├── transport_stop_views.xml
│   ├── vehicle_assignment_views.xml
│   ├── carrier_document_views.xml
│   ├── res_partner_views.xml
│   └── menu_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── transport_security.xml
├── i18n/
│   ├── tr.po
│   └── vsl_tasimacilik.pot
├── data/
│   └── transport_data.xml
├── wizards/
│   ├── __init__.py
│   └── transport_invoice_wizard.py
├── reports/
│   ├── __init__.py
│   ├── transport_order_report.py
│   └── transport_order_report.xml
├── static/
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    └── test_transport_order.py
```

### Bağımlılıklar (`__manifest__.py` `depends`)

`base`, `mail`, `contacts`, `fleet`, `account`

## 4. Veri Modelleri

### 4.1 `vsl.transport.order` — Sevkiyat Emri

| Alan | Tip | Gerekli | Açıklama |
|---|---|---|---|
| `name` | Char | ✓ | Belge numarası (sequence, otomatik) |
| `customer_id` | Many2one(res.partner) | ✓ | Müşteri |
| `state` | Selection | ✓ | Taslak → Açık → Atandı → Yüklemede → Yolda → Teslim Edildi → Faturalandı → İptal |
| `planned_date_start` | DateTime | | Planlanan başlangıç |
| `planned_date_end` | DateTime | | Planlanan bitiş |
| `actual_date_start` | DateTime | | Gerçekleşen başlangıç |
| `actual_date_end` | DateTime | | Gerçekleşen bitiş |
| `amount_total` | Monetary | | Toplam taşıma bedeli |
| `currency_id` | Many2one(res.currency) | | Para birimi (varsayılan: TRY) |
| `notes` | Text | | Açıklama |
| `stop_ids` | One2many(vsl.transport.stop, order_id) | | Duraklar |
| `assignment_id` | One2many | | Araç ataması (tarihçe için one2many) |
| `invoice_ids` | Many2many(account.move) | | İlişkili faturalar |
| `company_id` | Many2one(res.company) | ✓ | Şirket |

### 4.2 `vsl.transport.stop` — Durak (Yükleme/Boşaltma)

| Alan | Tip | Gerekli | Açıklama |
|---|---|---|---|
| `order_id` | Many2one(vsl.transport.order) | ✓ | Bağlı sevkiyat emri |
| `sequence` | Integer | ✓ | Sıralama |
| `stop_type` | Selection | ✓ | loading / unloading |
| `address_id` | Many2one(res.partner) | ✓ | Adres (yükleme/boşaltma noktası) |
| `planned_date` | DateTime | | Planlanan tarih |
| `actual_date` | DateTime | | Gerçekleşen tarih |
| `state` | Selection | ✓ | pending → done → cancelled |
| `line_ids` | One2many(vsl.transport.stop.line, stop_id) | | Durak kalemleri |
| `notes` | Text | | Notlar |

### 4.3 `vsl.transport.stop.line` — Durak Kalemi (Parsiyel yükleme)

| Alan | Tip | Gerekli | Açıklama |
|---|---|---|---|
| `stop_id` | Many2one(vsl.transport.stop) | ✓ | Bağlı durak |
| `customer_id` | Many2one(res.partner) | | Hangi müşterinin malı |
| `product_desc` | Char | | Mal açıklaması |
| `quantity` | Float | | Miktar |
| `weight` | Float | | Ağırlık (kg) |


### 4.4 `vsl.vehicle.assignment` — Araç ve Sürücü Ataması

| Alan | Tip | Gerekli | Açıklama |
|---|---|---|---|
| `order_id` | Many2one(vsl.transport.order) | ✓ | Sevkiyat emri |
| `vehicle_id` | Many2one(fleet.vehicle) | | Araç (kendi filodan) |
| `external_vehicle_plate` | Char | | Plaka (dış tedarikçi aracı için) |
| `driver_id` | Many2one(res.partner) | ✓ | Sürücü/tedarikçi (is_carrier=True) |
| `assignment_date` | DateTime | | Atama tarihi |
| `state` | Selection | | assigned → departed → completed → cancelled |

**Kural:** `vehicle_id` veya `external_vehicle_plate` alanlarından en az biri dolu olmalıdır.

### 4.5 `vsl.carrier.document` — Tedarikçi Evrakı

| Alan | Tip | Gerekli | Açıklama |
|---|---|---|---|
| `carrier_id` | Many2one(res.partner) | ✓ | Tedarikçi |
| `doc_type` | Selection | ✓ | driving_license / vehicle_registration / insurance / src_certificate / other |
| `attachment_id` | Many2one(ir.attachment) | ✓ | Dosya (PDF, görsel) |
| `issue_date` | Date | | Düzenleme tarihi |
| `expiry_date` | Date | | Geçerlilik bitiş tarihi |
| `state` | Selection | ✓ | valid → expired |

### 4.6 `res.partner` Genişletmesi

| Alan | Tip | Açıklama |
|---|---|---|
| `is_carrier` | Boolean | Tedarikçi/kamyoncu işareti |
| `carrier_tax_office` | Char | Vergi dairesi |
| `carrier_tax_number` | Char | Vergi numarası |
| `carrier_document_ids` | One2many(vsl.carrier.document, carrier_id) | Evrak kayıtları |

## 5. İş Akışı ve Durum Makinesi

### Sevkiyat Emri Durumları

```
        ┌──────┐    ┌──────┐    ┌─────────┐    ┌───────────┐    ┌──────┐    ┌──────────────┐    ┌──────────────┐
        │Taslak│───▶│ Açık │───▶│ Atandı  │───▶│ Yüklemede │───▶│Yolda │───▶│Teslim Edildi │───▶│ Faturalandı  │
        └──┬───┘    └──┬───┘    └────┬────┘    └─────┬─────┘    └──┬───┘    └──────┬───────┘    └──────────────┘
           │           │            │                │             │              │
           ▼           ▼            ▼                ▼             ▼              ▼
        ┌──────┐   ┌──────┐    ┌────────┐      ┌────────┐    ┌────────┐    ┌──────────┐
        │İptal │   │İptal │    │ İptal  │      │ İptal  │    │ İptal  │    │ İptal    │
        └──────┘   └──────┘    └────────┘      └────────┘    └────────┘    │(faturalı │
                                                                            │iptal edilmez)
                                                                            └──────────┘
```

| Geçiş | Tetikleyici | Kurallar |
|---|---|---|
| Taslak → Açık | `action_confirm()` butonu | En az 1 müşteri, en az 2 durak (en az 1 yükleme + 1 boşaltma) |
| Açık → Atandı | Araç ataması tamamlandı | Geçerli bir `vsl.vehicle.assignment` kaydı |
| Atandı → Yüklemede | `action_start_loading()` butonu | İlk yükleme durağı başlatıldı |
| Yüklemede → Yolda | `action_depart()` butonu | Tüm yükleme durakları 'done' |
| Yolda → Teslim Edildi | `action_deliver()` butonu | Tüm boşaltma durakları 'done' |
| Teslim Edildi → Faturalandı | Sihirbaz ile fatura oluşturma | En az 1 müşteri faturası oluşturuldu |
| Herhangi → İptal | `action_cancel()` butonu | `Faturalandı` durumunda iptal edilemez |

### Geçmiş Fiyat Sorgulama

Kullanıcı sevkiyat emri formunda bir butona basarak, aynı ilk yükleme ve son boşaltma adresine sahip geçmiş sevkiyatları ve `amount_total` değerlerini listeleyebilir. Hesaplanan alan değil, isteğe bağlı (`on-demand`) sorgudur.

### Fatura Oluşturma Sihirbazı

`Teslim Edildi` durumundaki sevkiyat emri için sihirbaz (`wizard`) açılır:

1. Müşteri faturası (`out_invoice`) — taşıma bedeli + ek kalemler
2. Tedarikçi faturası (`in_invoice`) — kamyoncuya ödenecek bedel
3. Ek kalemler (sigorta, depolama, gümrük) her iki faturaya satır olarak eklenebilir
4. Her iki fatura `vsl.transport.order` ile `invoice_ids` alanı üzerinden ilişkilendirilir

### Çoklu/Parsiyel Yükleme

- Bir sevkiyat emrine birden çok durak (`vsl.transport.stop`) eklenir
- Her durakta birden çok kalem (`vsl.transport.stop.line`) olabilir
- Kalemler farklı müşterilere ait olabilir (`customer_id`)
- Durak sıralaması `sequence` alanıyla belirlenir, kullanıcı arayüzünden sıralanabilir

## 6. Güvenlik

### Kullanıcı Grupları

| XML ID | Ad | Yetkiler |
|---|---|---|
| `group_vsl_transport_user` | Taşımacılık Kullanıcısı | Sevkiyat emirlerini görüntüleme, oluşturma, düzenleme |
| `group_vsl_transport_manager` | Taşımacılık Yöneticisi | Tüm yetkiler + silme, yapılandırma, fatura oluşturma |
| `group_vsl_garage_operator` | Garaj Operatörü | Araç ataması, tedarikçi evrakları yönetimi |

### Kayıt Kuralları

| Model | Grup | Kural |
|---|---|---|
| `vsl.transport.order` | `user` | Kendi oluşturduğu kayıtları görüntüleyebilir |
| `vsl.transport.order` | `garage_operator` | Yalnızca `Açık` durumundaki kayıtları görüntüleyebilir |
| `vsl.carrier.document` | `user` | Okuma erişimi var |
| `vsl.carrier.document` | `garage_operator` | Tam erişim |
| Tüm modeller | `manager` | Tam erişim |

### Model Erişim Matrisi

Model bazında `ir.model.access.csv` ile temel CRUD yetkileri verilir:
- `read`: Tüm gruplara açık
- `create/write/unlink`: Grup bazında kısıtlı (manager tam, user kısmi, garage_operator sınırlı)

## 7. Test Stratejisi

| Seviye | Kapsam |
|---|---|
| Birim testi | Model CRUD, alan kısıtlamaları (`@api.constrains`), durum geçişleri, `_compute` alanları |
| Entegrasyon testi | Uçtan uca iş akışı (Taslak → Faturalandı), fatura oluşturma, parsiyel yükleme |

Testler Odoo'nun yerleşik test framework'ü (`odoo.tests.common.TransactionCase`) ile yazılır.

## 8. Teknik Notlar

- **Dosya saklama:** Evraklar `ir.attachment` ile Odoo filestore'da saklanır. Docker volume (`odoo-web-data`) kalıcıdır.
- **Versiyon:** `19.0.1.0.0` ile başlar, semantik versiyonlama.
- **Adlandırma:** Model adları `vsl.transport.order` formatında (noktalı), view ID'leri `view_vsl_transport_order_form` formatında.
- **Hata yönetimi:** `UserError` ile Türkçe ve İngilizce hata mesajları, `@api.constrains` ile iş kuralları.
- **İptal mantığı:** `Faturalandı` durumundaki sevkiyat emri iptal edilemez. Diğer durumlarda iptal mümkündür.
