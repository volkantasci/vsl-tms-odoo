# Spec: Voslo Gap Analysis & Implementation — vsl_transport Modulu Genisletme

**Tarih:** 2026-05-08
**Durum:** Approved
**Kapsam:** vsl_transport'a voslo uygulamasındaki eksik ozelliklerin eklenmesi

---

## 1. Amac

Voslo lojistik uygulamasında var olup vsl_transport Odoo modulunde eksik olan ozellikleri,
Odoo 19 mimarisine uygun sekilde gelistirmek.

## 2. Tasarim Kararlari

| # | Konu | Karar |
|---|---|---|
| 1 | Surucu modeli | Ayri `vsl.driver.profile`, `res.partner` ile Many2one |
| 2 | Evrak modeli | 3 ayri model: `vsl.carrier.document`, `vsl.driver.document`, `vsl.vehicle.document` |
| 3 | Lokasyon modeli | Ayri `vsl.location`, `stop`a istege bagli `location_id` ek |
| 4 | Arac yonetimi | `fleet.vehicle` inheritance + 6 referans veri modeli |
| 5 | Dashboard | `vsl.dashboard` transient model + QWeb kanban view |

## 3. Yeni Modeller

### 3.1 Surucu Profili (`vsl.driver.profile`)

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `partner_id` | Many2one(res.partner) | Evet | Bagli kisi/firma, ondelete=cascade |
| `driver_type_id` | Many2one(vsl.driver.type) | Hayir | Calisma tipi |
| `license_number` | Char | Hayir | Ehliyet numarasi |
| `license_class` | Selection | Hayir | B, C, E, CE |
| `status` | Selection | Evet (default=active) | active, inactive, on_leave |
| `phone` | Char | Hayir | Telefon |
| `document_ids` | One2many(vsl.driver.document) | Hayir | Surucu evraklari |

**Order:** `partner_id.name`

### 3.2 Surucu Tipi Referansi (`vsl.driver.type`)

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `name` | Char | Evet | Tedarik, Sozlesmeli, Sozlesmesiz |

### 3.3 Surucu Evraki (`vsl.driver.document`)

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `driver_id` | Many2one(vsl.driver.profile) | Evet | ondelete=cascade, indexed |
| `doc_type` | Selection | Evet | license, src_certificate, psychotechnic, other |
| `attachment_id` | Many2one(ir.attachment) | Evet | Dosya yukleme |
| `issue_date` | Date | Hayir | Duzenleme tarihi |
| `expiry_date` | Date | Hayir | Son kullanma tarihi |
| `state` | Selection (computed) | Hayir | valid / expired (expiry_date'e gore) |
| `notes` | Text | Hayir | Aciklama |

### 3.4 Arac Referans Verileri (5 model)

Tumunde sadece `name` (Char, required) alani vardir:

| Model | Ornek Degerler |
|---|---|
| `vsl.vehicle.type` | Kamyonet, 6 Teker, Atego, 10 Teker, 40 Ayak, Cekici, Dorse, Lowbed, Forklift, Vinc |
| `vsl.vehicle.trailer.class` | Tenteli, Tentesiz |
| `vsl.vehicle.case.type` | Acik, Kapali, Frigo |
| `vsl.vehicle.pass.system` | OGS, HGS, OGS + HGS |
| `vsl.vehicle.ownership` | Oz Mal, Tedarik |

### 3.5 Arac Evraki (`vsl.vehicle.document`)

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `vehicle_id` | Many2one(fleet.vehicle) | Evet | ondelete=cascade, indexed |
| `doc_type` | Selection | Evet | insurance, vehicle_registration, inspection, other |
| `attachment_id` | Many2one(ir.attachment) | Evet | Dosya yukleme |
| `issue_date` | Date | Hayir | |
| `expiry_date` | Date | Hayir | |
| `state` | Selection (computed) | Hayir | valid / expired |
| `notes` | Text | Hayir | |

### 3.6 fleet.vehicle Genisletme

`fleet.vehicle` modeline `_inherit` ile eklenen alanlar:

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `vsl_vehicle_type_id` | Many2one(vsl.vehicle.type) | Hayir | Arac tipi |
| `vsl_trailer_class_id` | Many2one(vsl.vehicle.trailer.class) | Hayir | Dorse sinifi |
| `vsl_case_type_id` | Many2one(vsl.vehicle.case.type) | Hayir | Kasa tipi |
| `vsl_pass_system_id` | Many2one(vsl.vehicle.pass.system) | Hayir | Gecis sistemi |
| `vsl_ownership_id` | Many2one(vsl.vehicle.ownership) | Hayir | Sahiplik |
| `vsl_capacity` | Float | Hayir | Kapasite (ton) |
| `vsl_transport_status` | Selection | Hayir (default=available) | available, on_route, maintenance |
| `vsl_document_ids` | One2many(vsl.vehicle.document) | Hayir | Arac evraklari |

### 3.7 Lokasyon (`vsl.location`)

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `name` | Char (indexed) | Evet | Lokasyon adi |
| `type` | Selection | Evet | warehouse, port, customs, factory, office, other |
| `partner_id` | Many2one(res.partner) | Hayir | Bagli adres (istege bagli) |
| `street` | Char | Hayir | Acik adres |
| `city` | Char | Hayir | Sehir |
| `country_id` | Many2one(res.country) | Hayir | Ulke |
| `latitude` | Float | Hayir | Enlem |
| `longitude` | Float | Hayir | Boylam |
| `contact_name` | Char | Hayir | Yetkili adi |
| `contact_phone` | Char | Hayir | Yetkili telefon |
| `features` | Text | Hayir | Ozellikler (Forklift, Cold Storage vs.) |
| `notes` | Text | Hayir | |

### 3.8 vsl.transport.stop Genisletme

`vsl.transport.stop` modeline `_inherit` ile eklenen:

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `location_id` | Many2one(vsl.location) | Hayir | Lokasyon referansi (address_id'ye ek olarak) |

### 3.9 Dashboard (`vsl.dashboard`) — TransientModel

Metrikleri hesaplamak icin `_compute` metotlu transient model. Kanban view ile kartlar halinde gosterim.

**Metrikler:**

| Kategori | Metrik | Sorgu |
|---|---|---|
| **Operasyon** | Toplam sevkiyat | `search_count([])` |
| | Acik sevkiyatlar | `search_count([('state', 'in', ['open','assigned'])])` |
| | Yuklemede | `search_count([('state', '=', 'loading')])` |
| | Yolda | `search_count([('state', '=', 'in_transit')])` |
| | Teslim edildi (aylik) | `search_count([('state', '=', 'delivered'), ('actual_date_end', '>=', ...)])` |
| | Iptal (aylik) | `search_count([('state', '=', 'cancelled'), ...])` |
| **Filo** | Toplam arac | `search_count([...], fleet.vehicle)` |
| | Musait araclar | `search_count([('vsl_transport_status', '=', 'available')])` |
| | Yoldaki araclar | `search_count([('vsl_transport_status', '=', 'on_route')])` |
| | Bakimdaki araclar | `search_count([('vsl_transport_status', '=', 'maintenance')])` |
| | Toplam surucu | `search_count([])` |
| | Aktif suruculer | `search_count([('status', '=', 'active')])` |
| **Partner** | Toplam tedarikci | `search_count([('is_carrier', '=', True)])` |
| | Toplam lokasyon | `search_count([])` |

## 4. View'ler

### 4.1 Surucu Profili
- **List view:** partner_id, driver_type_id, license_number, license_class, status, phone
- **Form view:** Tum alanlar + document_ids One2many inline
- **Search view:** partner_id, status filtreleri

### 4.2 Surucu Evraklari
- **List view:** driver_id, doc_type, issue_date, expiry_date, state (badge)
- **Form view:** Tum alanlar + attachment_id (binary widget)

### 4.3 Arac Evraklari
- **List view:** vehicle_id, doc_type, issue_date, expiry_date, state
- **Form view:** Tum alanlar + attachment_id

### 4.4 fleet.vehicle Genisletme
- Mevcut `fleet.vehicle.form` view'ine "Tasimacilik" sayfa sekmasi ekle
- Yeni alanlar bu sekmede: vsl_vehicle_type_id, vsl_trailer_class_id, vsl_case_type_id, vsl_pass_system_id, vsl_ownership_id, vsl_capacity, vsl_transport_status
- Arac evraklari alt sekme olarak One2many inline

### 4.5 Lokasyon
- **List view:** name, type, city, contact_name, contact_phone
- **Form view:** Tum alanlar, koordinatlar icin ayri group
- **Search view:** name, type filtresi

### 4.6 Dashboard
- Kanban view: 4 sutun (Operasyon, Filo, Partner)
- Her sutunda metrik kartlari
- Dekorasyon: pozitif/negatif renklendirme

## 5. Menu Yapisi

```
Sevkiyatlar/
├── Sevkiyat Emirleri         (mevcut)
├── Arac Atamalari            (mevcut)
├── Tedarikci Evraklari       (mevcut)
├── Suruculer                 (YENI)
│   ├── Surucu Profilleri     (action_vsl_driver_profile)
│   ├── Surucu Evraklari      (action_vsl_driver_document)
│   └── Surucu Tipleri        (action_vsl_driver_type)
├── Arac Yonetimi             (YENI)
│   ├── Arac Evraklari        (action_vsl_vehicle_document)
│   ├── Arac Tipleri          (action_vsl_vehicle_type)
│   ├── Kasa Tipleri          (action_vsl_vehicle_case_type)
│   ├── Dorse Siniflari       (action_vsl_vehicle_trailer_class)
│   ├── Gecis Sistemleri      (action_vsl_vehicle_pass_system)
│   └── Sahiplik Durumlari    (action_vsl_vehicle_ownership)
├── Lokasyonlar               (YENI, action_vsl_location)
├── Dashboard                 (YENI, action_vsl_dashboard)
└── Yapilandirma              (mevcut, manager only)
```

## 6. Guvenlik

- Suruculer: Transport User (R,W,C), Manager (all), Garage Operator (R,W,C)
- Surucu Evraklari: Garage Operator (R,W,C,U), Manager (all), User (R)
- Arac Referans verileri: Manager (all), User/Garage (R)
- Arac Evraklari: Garage Operator (R,W,C,U), Manager (all), User (R)
- Lokasyonlar: Transport User (R,W,C), Manager (all)
- Dashboard: Tum gruplar (R)

## 7. Veri Dosyalari (Seed/Default Data)

`data/vsl_reference_data.xml` dosyasi (noupdate=1) ile varsayilan degerler:
- Surucu tipleri: Tedarik, Sozlesmeli, Sozlesmesiz
- Arac tipleri: 10 adet (Kamyonet, 6 Teker, Atego, 10 Teker, 40 Ayak, Cekici, Dorse, Lowbed, Forklift, Vinc)
- Dorse siniflari: Tenteli, Tentesiz
- Kasa tipleri: Acik, Kapali, Frigo
- Gecis sistemleri: OGS, HGS
- Sahiplik: Oz Mal, Tedarik

## 8. Testler

Her yeni model icin:
- Olusturma testi
- Zorunlu alan validasyonu
- Computed alan testi (evraklarda son kullanma tarihi -> state)
- Surucu/arac evraklarinda expire state kontrolu

## 9. Bagimliliklar

- `fleet` — Mevcut bagimlilik, `fleet.vehicle` inheritance icin
- `base`, `mail`, `contacts`, `account` — Zaten mevcut

## 10. Yapilmayacaklar

- Envanter/stock.picking entegrasyonu
- Rota mesafe/sure hesaplama (Harita API entegrasyonu)
- Fatura tevkifat sistemi (Odoo'nun account.tax ile yapilabilir, ayrica gelistirme gereksiz)
- Email/bildirim sistemi
- Mobil/webhook/real-time
