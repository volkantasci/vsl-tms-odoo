# Tasarım: Sevkiyat Yükü — Fatura Ürünü Ayrımı

**Tarih:** 2026-05-11
**Modül:** `vsl_transport`
**Odoo Sürümü:** 19.0

## Amaç

Sevkiyat sırasında taşınan mallar (`vsl.transport.stop.line.product_id`) ile faturalamada kullanılan
hizmet/satış ürünleri aynı `product.product` modelini kullanmaktadır. Bu durum Ürünler listesinde
karışıklığa yol açmaktadır. Sevkiyata konu olan ürünlerin ana Ürünler listesinden ayrılması ve
ayrı bir menü altında yönetilmesi hedeflenir.

## Tasarım Kararı

**Yaklaşım:** `product.category` ile ayrıştırma. Odoo'nun yerleşik ürün kategorileme altyapısı kullanılır.

## Bileşenler

### 1. Veri Katmanı — `product.category` Kaydı

Modül yüklendiğinde oluşturulacak bir kategori:

```xml
<record id="product_category_cargo" model="product.category">
    <field name="name">Sevkiyat Yükleri</field>
    <field name="parent_id" ref="product.product_category_all"/>
</record>
```

- **XML ID:** `vsl_transport.product_category_cargo`
- Sevkiyata konu tüm ürünler bu kategoriye (veya alt kategorilerine) atanır
- Alt kategoriler (örn. Tehlikeli Madde, Gıda) ileride eklenebilir

### 2. Model Değişikliği — `vsl.transport.stop.line`

`product_id` alanına sevkiyat kategorisi ile filtreleme domain'i eklenir:

```python
@api.model
def _get_cargo_product_domain(self):
    cargo_categ = self.env.ref(
        'vsl_transport.product_category_cargo', raise_if_not_found=False
    )
    if cargo_categ:
        return [('categ_id', 'child_of', cargo_categ.ids)]
    return []

product_id = fields.Many2one(
    "product.product",
    string="Product",
    domain=lambda self: self._get_cargo_product_domain(),
)
```

`child_of` operatörü alt kategorileri de otomatik kapsar. Kategori XML kaydı bulunamazsa
domain boş döner (hata vermez).

Etkilenen dosya: `models/transport_stop.py`

### 3. Menü Yapısı

Ana Ürünler menüsü altında iki ayrı liste menüsü:

```
Ürünler (üst menü, standart Odoo)
├── Ürünler              → action_regular_products
├── Sevkiyat Yükleri      → action_cargo_products
├── Ürün Çeşitleri        → (korunur)
└── Ürün Kategorileri     → (korunur)
```

**Yeni eylemler:**

| XML ID | Model | Domain |
|--------|-------|--------|
| `action_regular_products` | `product.template` | Sevkiyat kategorisi ve alt kategorileri HARİÇ |
| `action_cargo_products` | `product.template` | Sadece sevkiyat kategorisi ve alt kategorileri |

**Menü değişiklikleri:**

1. Standart `product.product_template_menu` menüsünün `action` alanı `action_regular_products` ile değiştirilir
2. Aynı üst menü altına yeni bir `<menuitem>` ile `action_cargo_products` eklenir

Ürün formu her iki menüde de aynı standart `product.template` form görünümüdür, ek değişiklik gerekmez.

Etkilenen dosya: `views/product_menu.xml` (yeni)

### 4. Görünüm Değişikliği

Stop line form/tree görünümünde değişiklik gerekmez — `product_id` alanının yeni domain'i
otomatik olarak sadece sevkiyat kategorisindeki ürünlerin seçilmesini sağlar.

### 5. Test Stratejisi

- **Birim test:** `_get_cargo_product_domain()` metodunun doğru domain döndürdüğü kontrol edilir
- **Entegrasyon test:** Sevkiyat emri oluşturulup stop line'da ürün seçerken sadece sevkiyat
  kategorisindeki ürünlerin listelenmesi doğrulanır
- **Menü test:** Her iki menü eyleminin doğru domain ile çalıştığı kontrol edilir

## Veri Geçişi

Mevcut veriler için otomatik bir geçiş (migration) planlanmamaktadır. Halihazırda taşınan
yüklere atanmış ürünler varsa, bunların manuel olarak "Sevkiyat Yükleri" kategorisine taşınması
gerekir. Modül yönetici tarafından `product.category_id` alanı düzenlenerek bu işlem yapılabilir.

## Sınırlamalar

- Bir ürün yalnızca bir kategori ağacına ait olabilir. Bir ürün hem sevkiyat yükü hem de
  fatura ürünü olamaz.
- `child_of` domain operatörü alt kategorileri kapsar; `parent_of` değil.
- Standart Odoo Ürünler menüsü üzerine yazıldığı için, Odoo çekirdek modül güncellemelerinde
  menü tekrar eski haline dönebilir; modül yükseltmesi (`-u vsl_transport`) sonrası düzeltilir.
