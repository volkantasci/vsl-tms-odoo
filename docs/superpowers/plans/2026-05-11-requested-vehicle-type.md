# İstenen Araç Cinsi Alanı - Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sevkiyat emirlerine "İstenen Araç Cinsi" alanı eklemek ve atama validasyonu yapmak.

**Architecture:** Many2one alanı `vsl.vehicle.type` modelinden beslenir. Formda "Müşteri ve Tarihler" grubuna eklenir. Atama yapılırken araç cinsi uyumsuzluğunda warning gösterilir ama atama engellenmez.

**Tech Stack:** Odoo 19, Python, XML views

---

### Task 1: Model Alanı Ekle

**Files:**
- Modify: `vsl_transport/models/transport_order.py:80-95`

- [ ] **Step 1: `transport_order.py` dosyasına alan ekle**

Bulunacak yer (`stop_ids` tanımından sonra, `assignment_ids`'den önce):

```python
    stop_ids = fields.One2many(
        "vsl.transport.stop",
        "order_id",
        string="Stops",
        copy=True,
    )
    requested_vehicle_type_id = fields.Many2one(
        "vsl.vehicle.type",
        string="Requested Vehicle Type",
    )
    assignment_ids = fields.One2many(
        "vsl.vehicle.assignment",
        "order_id",
        string="Assignments",
    )
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/models/transport_order.py
git commit -m "feat(transport_order): add requested_vehicle_type_id field"
```

---

### Task 2: View'e Alan Ekle

**Files:**
- Modify: `vsl_transport/views/transport_order_views.xml`

- [ ] **Step 1: Form view'e alan ekle**

`customer_order_ref` alanından sonra, `planned_date_start`'den önce eklenecek:

```xml
<field name="customer_order_ref"/>
<field name="requested_vehicle_type_id"/>
<field name="planned_date_start"/>
```

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/views/transport_order_views.xml
git commit -m "feat(views): add requested_vehicle_type_id to transport order form"
```

---

### Task 3: Atama Validasyonu Ekle

**Files:**
- Modify: `vsl_transport/wizards/transport_assignment_wizard.py`
- Modify: `vsl_transport/models/vehicle_assignment.py` (doğrudan atama için)

- [ ] **Step 1: Wizard validasyonunu oku ve ekle**

`transport_assignment_wizard.py` dosyasını oku, `action_assign` veya benzeri methodu bul. Atamadan önce şu kontrolü ekle:

```python
# Check vehicle type compatibility
if wizard.requested_vehicle_type_id and vehicle.vsl_vehicle_type_id:
    if wizard.requested_vehicle_type_id != vehicle.vsl_vehicle_type_id:
        return {
            'type': 'ir.actions.act_window.message',
            'title': _('Uyarı'),
            'message': _(
                "Atanan aracın cinsi (%(assigned)s), istenen araç cinsinden (%(requested)s) farklıdır. "
                "Yine de devam etmek istiyor musunuz?"
            ) % {
                'assigned': vehicle.vsl_vehicle_type_id.name,
                'requested': wizard.requested_vehicle_type_id.name,
            },
            'buttons': [
                {
                    'name': _('Evet, Devam Et'),
                    'type': 'action',
                    'params': {
                        'action': 'continue_assignment',
                    },
                },
                {
                    'name': _('Hayır, İptal'),
                    'type': 'action',
                    'close': True,
                },
            ],
        }
```

**Not:** Bu Odoo 19'da çalışmayabilir. Basitçe `_show_warning` yardımcısı veya direkt `return` yerine mevcut pattern'e uygun bir yöntem tercih edilmeli. Daha basit yaklaşım:

```python
# Araç tipi uyarısı
if order_id.requested_vehicle_type_id and vehicle_id.vsl_vehicle_type_id:
    if order_id.requested_vehicle_type_id != vehicle_id.vsl_vehicle_type_id:
        # Warning göster ama devam ettir
        warning = _(
            "Atanan aracın cinsi (%s), istenen araç cinsinden (%s) farklıdır. Devam ediliyor..."
        ) % (vehicle_id.vsl_vehicle_type_id.name, order_id.requested_vehicle_type_id.name)
        # Warning'i context'e ekle veya logla
```

- [ ] **Step 2: vehicle_assignment.py'ye aynı kontrolü ekle**

Doğrudan atama için `vehicle_assignment.py` dosyasını oku ve `write`/`create` override et.

- [ ] **Step 3: Commit**

```bash
git add vsl_transport/wizards/transport_assignment_wizard.py vsl_transport/models/vehicle_assignment.py
git commit -m "feat(validation): add vehicle type mismatch warning on assignment"
```

---

### Task 4: Modülü Güncelle ve Test Et

**Files:**
- Modify: `vsl_transport/__manifest__.py` (version bump)

- [ ] **Step 1: Module upgrade**

```bash
docker compose -f ~/dev/odoo/docker-compose.yml stop web
docker compose -f ~/dev/odoo/docker-compose.yml run --rm web odoo \
  -d odoo -u vsl_transport --stop-after-init
docker compose -f ~/dev/odoo/docker-compose.yml up -d web
```

- [ ] **Step 2: Manuel test**
- Yeni sevkiyat oluştur → "İstenen Araç Cinsi" alanını gör
- Farklı tipli araç ataması yap → uyarı kontrol et

- [ ] **Step 3: Test manifest güncelle ve commit**

```bash
git add vsl_transport/__manifest__.py
git commit -m "bump: vsl_transport 1.1.0 - add requested_vehicle_type"
```

---

### Task 5: View'i List'e Ekle (Opsiyonel)

**Files:**
- Modify: `vsl_transport/views/transport_order_views.xml`

- [ ] **Step 1: Tree view'e kolon ekle**

List view'de diğer alanlarla birlikte `requested_vehicle_type_id` kolonunu ekle.

- [ ] **Step 2: Commit**

```bash
git add vsl_transport/views/transport_order_views.xml
git commit -m "feat(views): add requested_vehicle_type_id to tree view"
```