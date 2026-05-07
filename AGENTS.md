# AGENTS.md — vsl-Taşımacılık Geliştirici Referansı

## Ortam

| Bilgi | Değer |
|---|---|
| **Odoo sürümü** | 19.0 (Community) |
| **Veritabanı** | PostgreSQL 16, container `odoo-db-1` |
| **Üretim veritabanı** | `odoo` (kullanıcı: `odoo@me@volkantasci.com`, dil: `tr_TR`) |
| **Test veritabanı** | `postgres` |
| **Web port** | `8069` (host) → `8069` (container) |
| **Odoo container** | `odoo-web-1` |
| **DB container** | `odoo-db-1` |
| **Docker compose** | `~/dev/odoo/docker-compose.yml` |
| **Custom addons** | `~/dev/odoo/addons/` → `/mnt/extra-addons/` (container) |
| **Proje dizini** | `~/dev/vsl-tms-odoo/` (git repo) |
| **Modül dizini** | `~/dev/vsl-tms-odoo/vsl_tasimacilik/` |

## Hızlı Komutlar

```bash
# === GELİŞTİRME DÖNGÜSÜ ===

# Modülü deploy et (her kod değişikliğinde)
cd ~/dev/vsl-tms-odoo
rm -rf ~/dev/odoo/addons/vsl_tasimacilik
cp -r vsl_tasimacilik ~/dev/odoo/addons/vsl_tasimacilik

# Web'i durdur, modülü güncelle, web'i başlat
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  -d odoo -u vsl_tasimacilik --stop-after-init
docker compose -f ~/dev/odoo/docker-compose.yml up -d web

# Container'ları yeniden başlat
docker compose -f ~/dev/odoo/docker-compose.yml restart

# === TEST ===

# Testleri çalıştır
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  --test-enable -d odoo -u vsl_tasimacilik --stop-after-init
docker compose -f ~/dev/odoo/docker-compose.yml up -d web

# === VERİTABANI ===

# SQL sorgusu (odoo veritabanı)
docker compose -f ~/dev/odoo/docker-compose.yml exec db psql -U odoo -d odoo -c "..."

# Çeviri yükleme (sadece yeni .po eklenince)
docker compose -f ~/dev/odoo/docker-compose.yml exec web odoo i18n loadlang -d odoo -l tr
docker compose -f ~/dev/odoo/docker-compose.yml exec web odoo i18n import \
  -d odoo -l tr --overwrite /mnt/extra-addons/vsl_tasimacilik/i18n/tr.po

# === KONTEYNER İÇİ ===

# Container'a bağlan
docker compose -f ~/dev/odoo/docker-compose.yml exec web bash

# Odoo logları
docker compose -f ~/dev/odoo/docker-compose.yml logs -f web
```

## Odoo 19 Önemli Farklılıklar (Bilinen Tuzaklar)

### View'ler
- ❌ `<tree>` → ✅ `<list>` (tüm standalone tree view'lerde)
- ❌ `states="draft"` → ✅ kaldırıldı, butonlar her zaman görünür (17.0+)
- ❌ `attrs="{'invisible': ...}"` → ✅ kaldırıldı (17.0+)
- ❌ `<group expand="0">` → ✅ `<group>` (search view, Odoo 19)
- ❌ `<group string="...">` → ✅ string attribute yok, sadece `<group>` (search view)
- ❌ İç içe `<form>` inline view'ler → ✅ **çalışmıyor**, field validasyonu üst modele karşı yapılıyor
- ❌ `<field name="x" mode="tree,form">` → ✅ sadece `<field name="x"/>`, inline tree/form tanımlanamaz
- ✅ One2many inline list view için **standalone tree view** tanımlayıp Odoo'nun otomatik kullanmasına bırak

### Modeller
- ❌ `def create(self, vals):` → ✅ `@api.model_create_multi` ile `def create(self, vals_list):`
- ❌ `fields.Date.today()` → ✅ `fields.Date.context_today(self)` (timezone)
- ❌ `store=True` compute → ✅ otomatik yenilenmez, sadece depends alanı değişince hesaplanır (son kullanma tarihi gibi bugüne bağlı hesaplamalarda kullanma)

### Güvenlik
- ❌ `<field name="category_id" ref="base.module_category_hidden"/>` → ✅ `category_id` alanı yok (res.groups)
- ✅ Admin erişimi için `base.group_system` grubuna izin ver

### Veritabanı
- Çeviriler JSONB alanlarda: `field_description = {"en_US": "...", "tr_TR": "..."}`
- Menü adları JSONB: `name = {"en_US": "...", "tr_TR": "..."}`  
- `ir_translation` tablosu **yok** — çeviriler doğrudan ilgili alanın JSONB kolonunda
- `.po` dosyası `i18n import` ile yüklenebilir AMA her zaman çalışmaz, gerekirse SQL

### Deploy
- ❌ Symlink Docker volume'lar arası çalışmaz → ✅ `cp -r` ile kopyala
- Odoo config dosyası: `~/dev/odoo/config/odoo.conf` (DB bilgileri dahil edilmeli)

## Modül Mimarisi

```
Sevkiyat Emri (vsl.transport.order)
├── Duraklar (vsl.transport.stop) [1:N, yükleme/boşaltma noktaları]
│   └── Durak Kalemleri (vsl.transport.stop.line) [1:N, parsiyel yükler]
├── Araç Ataması (vsl.vehicle.assignment) [1:N, araç+sürücü]
└── Faturalar (account.move) [M:N]

Tedarikçi (res.partner, is_carrier=True)
└── Evraklar (vsl.carrier.document) [1:N, ehliyet/ruhsat/sigorta]
```

## İş Akışı

```
action_confirm()           action_start_loading()    action_depart()         action_deliver()          wizard
draft ──────────▶ open ──▶ assigned ──────────▶ loading ──────────▶ in_transit ──────────▶ delivered ──────────▶ invoiced
  │                  │         │                    │                   │                       │
  └─ action_cancel() ┘         └─ action_cancel() ──┘                   └── action_cancel() ────┘  (iptal edilemez)
```

## Test Durumu

- 9/12 test geçiyor (Odoo 19 uyumluluk sorunları)
- Kalan 3 hata: araç atama validasyonu, evrak oluşturma (TransactionCase savepoint sorunu)

## Deploy Edilecek Dosyalar

Her kod değişikliğinde **tüm modül dizini** kopyalanmalı:
```bash
rm -rf ~/dev/odoo/addons/vsl_tasimacilik && cp -r ~/dev/vsl-tms-odoo/vsl_tasimacilik ~/dev/odoo/addons/vsl_tasimacilik
```

## Odoo Konfigürasyonu

`~/dev/odoo/config/odoo.conf`:
```ini
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
db_host = db
db_user = odoo
db_password = random_sifre
```
