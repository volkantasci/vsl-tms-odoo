# Sevkiyat Yükü — Fatura Ürünü Ayrımı Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sevkiyat yükü ürünlerini (cargo) fatura ürünlerinden ayırmak için `product.category` kullanarak iki ayrı menü altında listelemek ve sevkiyat stop line'da sadece cargo ürünlerinin seçilebilmesini sağlamak.

**Architecture:**
- Yeni `product.category` kaydı ("Sevkiyat Yükleri") oluşturulur
- `vsl.transport.stop.line.product_id` alanına domain eklenir (sadece cargo kategori ürünleri)
- Standart "Ürünler" menüsünün action'ı değiştirilir (cargo kategorisi HARİÇ)
- Yeni "Sevkiyat Yükleri" menüsü eklenir (sadece cargo kategorisi)

**Tech Stack:** Odoo 19, Python, XML

---

## Dosya Yapısı

```
vsl_transport/
├── __manifest__.py                    # data dosyalarına yeni XML eklenir
├── models/
│   └── transport_stop.py              # product_id domain eklenir
├── data/
│   └── product_category_cargo.xml     # YENİ: cargo category kaydı
├── views/
│   └── product_menu_views.xml         # YENİ: menu ve action override
└── tests/
    └── test_transport_order.py       # domain testi eklenir
```

---

## Task 1: product.category Data Dosyası

**Files:**
- Create: `vsl_transport/data/product_category_cargo.xml`

- [ ] **Step 1: Create data file**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="0">
        <record id="product_category_cargo" model="product.category">
            <field name="name">Sevkiyat Yükleri</field>
            <field name="parent_id" eval="False"/>
        </record>
    </data>
</odoo>
```

---

## Task 2: `vsl.transport.stop.line` Model Domain

**Files:**
- Modify: `vsl_transport/models/transport_stop.py:66-69`

- [ ] **Step 1: Add `api` import if not present**

```python
from odoo import api, fields, models
```

- [ ] **Step 2: Add `_get_cargo_product_domain` method to `VslTransportStopLine`**

```python
@api.model
def _get_cargo_product_domain(self):
    cargo_categ = self.env.ref(
        'vsl_transport.product_category_cargo', raise_if_not_found=False
    )
    if cargo_categ:
        return [('categ_id', 'child_of', cargo_categ.ids)]
    return []
```

- [ ] **Step 3: Update `product_id` field with domain**

```python
product_id = fields.Many2one(
    "product.product",
    string="Product",
    domain=lambda self: self._get_cargo_product_domain(),
)
```

- [ ] **Step 4: Commit**

```bash
git add vsl_transport/models/transport_stop.py
git commit -m "feat: add cargo product domain to stop line"
```

---

## Task 3: Menu ve Window Action XML

**Files:**
- Create: `vsl_transport/views/product_menu_views.xml`

- [ ] **Step 1: Create product_menu_views.xml with actions and menus**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Regular products action: excludes cargo category -->
    <record id="action_regular_products" model="ir.actions.act_window">
        <field name="name">Ürünler</field>
        <field name="res_model">product.template</field>
        <field name="view_mode">kanban,list,form</field>
        <field name="domain">[('categ_id', '!=', ref('vsl_transport.product_category_cargo'))]</field>
    </record>

    <!-- Cargo products action: only cargo category -->
    <record id="action_cargo_products" model="ir.actions.act_window">
        <field name="name">Sevkiyat Yükleri</field>
        <field name="res_model">product.template</field>
        <field name="view_mode">kanban,list,form</field>
        <field name="domain">[('categ_id', '=', ref('vsl_transport.product_category_cargo'))]</field>
    </record>

    <!-- Override standard Products menu action -->
    <record id="stock.menu_product_variant_config_stock" model="ir.ui.menu">
        <field name="action" ref="vsl_transport.action_regular_products"/>
    </record>

    <!-- Add cargo products menu as sibling under Products parent -->
    <menuitem id="menu_product_cargo"
              name="Sevkiyat Yükleri"
              parent="stock.menu_stock_inventory_control"
              action="vsl_transport.action_cargo_products"
              sequence="3"/>

</odoo>
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/views/product_menu_views.xml
git commit -m "feat: add cargo product menus and window actions"
```

---

## Task 4: Manifest Güncellemesi

**Files:**
- Modify: `vsl_transport/__manifest__.py:19-38`

- [ ] **Step 1: Add new data files to manifest**

Add to `data` list:
```python
"data/product_category_cargo.xml",
"views/product_menu_views.xml",
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/__manifest__.py
git commit -m "feat: register cargo product data and menu files"
```

---

## Task 5: Test — Domain Doğrulaması

**Files:**
- Modify: `vsl_transport/tests/test_transport_order.py`

- [ ] **Step 1: Add test for cargo product domain**

Add at end of `TestTransportOrder` class:

```python
def test_cargo_product_domain(self):
    """Cargo category ürünleri stop line'da seçilebilir olmalı,
    cargo olmayan ürünler seçilememeli."""
    cargo_categ = self.env.ref('vsl_transport.product_category_cargo', raise_if_not_found=False)
    self.assertTrue(cargo_categ, "Cargo category should exist")

    # Cargo ürünü oluştur
    cargo_product = self.env['product.product'].create({
        'name': 'Test Cargo Product',
        'categ_id': cargo_categ.id,
        'type': 'product',
    })

    # Normal ürün oluştur (cargo category dışında)
    normal_product = self.env['product.product'].create({
        'name': 'Test Normal Product',
        'type': 'product',
    })

    # Stop line domain'i cargo ürününü içermeli
    stop_line = self.env['vsl.transport.stop.line']
    domain = stop_line._get_cargo_product_domain()
    self.assertIn('categ_id', str(domain))
    self.assertIn('child_of', str(domain))

    # Domain ile search yapıldığında sadece cargo ürünü gelmeli
    domain_search = [('categ_id', 'child_of', cargo_categ.ids)]
    cargo_products = self.env['product.product'].search(domain_search)
    self.assertIn(cargo_product.id, cargo_products.ids)
    self.assertNotIn(normal_product.id, cargo_products.ids)
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/tests/test_transport_order.py
git commit -m "test: add cargo product domain validation test"
```

---

## Task 6: Modülü Güncelle ve Test Et

- [ ] **Step 1: Stop web container, upgrade module, start web**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  -d odoo -u vsl_transport --stop-after-init
docker compose -f ~/dev/odoo/docker-compose.yml up -d web
```

- [ ] **Step 2: Run tests**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  --test-enable -d odoo -u vsl_transport --stop-after-init
docker compose -f ~/dev/odoo/docker-compose.yml up -d web
```

- [ ] **Step 3: Manual verification**

1. Ürünler menüsüne gir → cargo kategorisindeki ürünler görünmemeli
2. Sevkiyat Yükleri menüsüne gir → sadece cargo kategorisindeki ürünler görünmeli
3. Sevkiyat emri oluştur → stop line'da ürün seçerken sadece cargo kategorisindeki ürünler listelenmeli

---

## Özet — Değiştirilen/Oluşturulan Dosyalar

| Dosya | Durum | Açıklama |
|-------|-------|----------|
| `data/product_category_cargo.xml` | CREATE | Sevkiyat Yükleri category kaydı |
| `models/transport_stop.py` | MODIFY | product_id domain + helper method |
| `views/product_menu_views.xml` | CREATE | Window actions + menu override |
| `__manifest__.py` | MODIFY | Yeni data dosyaları |
| `tests/test_transport_order.py` | MODIFY | Domain testi |

---

## Sınırlama

- Domain operatörü `!=` ve `=` sadece direkt kategoriyi filtreler, alt kategorileri HARİÇ tutmaz (action domain için).
- Alt kategoriler için module update gerekir.
- Model field domain'inde `child_of` kullanıldığından stop line'da ürün seçerken alt kategoriler DOĞRU şekilde listelenir.
