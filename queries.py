# queries.py

# ---------- Список заказов с поиском и фильтром ----------
ORDERS_LIST = """
SELECT
    co.order_no,
    co.order_date,
    c.name                       AS customer,
    p.name                       AS product,
    oi.quantity,
    co.status,
    p.sale_price * oi.quantity   AS total
FROM customer_orders co
JOIN counterparties c  ON c.id        = co.customer_id
JOIN order_items   oi  ON oi.order_no = co.order_no
JOIN products      p   ON p.code      = oi.product_code
WHERE (%(order_no)s IS NULL OR co.order_no ILIKE '%%' || %(order_no)s || '%%')
  AND (%(customer)s IS NULL OR c.name     ILIKE '%%' || %(customer)s || '%%')
  AND (%(status)s   IS NULL OR co.status  = %(status)s)
ORDER BY co.order_date DESC, co.order_no
"""

ORDER_BY_NO = """
SELECT
    co.order_no, co.order_date, co.customer_id, c.name,
    co.status, oi.product_code, p.name, oi.quantity, p.sale_price,
    p.sale_price * oi.quantity AS total
FROM customer_orders co
JOIN counterparties c  ON c.id        = co.customer_id
JOIN order_items   oi  ON oi.order_no = co.order_no
JOIN products      p   ON p.code      = oi.product_code
WHERE co.order_no = %s
"""

CUSTOMERS = "SELECT id, name FROM counterparties WHERE type_id = 1 ORDER BY name"
PRODUCTS  = "SELECT code, name, sale_price FROM products ORDER BY name"
STATUSES  = ["Новый", "В производстве", "Готов", "Отгружен"]

INSERT_ORDER = """
INSERT INTO customer_orders (order_no, order_date, customer_id, status)
VALUES (%s, %s, %s, %s)
"""

INSERT_ORDER_ITEM = """
INSERT INTO order_items (order_no, product_code, quantity)
VALUES (%s, %s, %s)
"""

NEXT_ORDER_NO = """
SELECT 'ORD' || LPAD((COALESCE(MAX(SUBSTRING(order_no FROM 4)::INT), 0) + 1)::TEXT, 3, '0')
FROM customer_orders
WHERE order_no ~ '^ORD[0-9]+$'
"""

UPDATE_ORDER_STATUS = "UPDATE customer_orders SET status = %s WHERE order_no = %s"

UPDATE_ORDER_ITEM_QTY = """
UPDATE order_items SET quantity = %s
WHERE order_no = %s AND product_code = %s
"""

NEXT_PRODUCTION_NO = """
SELECT 'PO' || LPAD((COALESCE(MAX(SUBSTRING(production_no FROM 3)::INT), 0) + 1)::TEXT, 3, '0')
FROM production_orders
WHERE production_no ~ '^PO[0-9]+$'
"""

INSERT_PRODUCTION_ORDER = """
INSERT INTO production_orders
    (production_no, customer_order_no, start_date, quantity, status)
VALUES (%s, %s, %s, %s, %s)
"""

PRODUCTION_BY_ORDER = """
SELECT production_no, start_date, quantity, status
FROM production_orders
WHERE customer_order_no = %s
ORDER BY production_no
"""

ALL_CONTRACTORS = """
SELECT c.id, c.name, c.inn, c.address, c.phone, ct.type_name
FROM counterparties c
JOIN counterparty_types ct ON ct.type_id = c.type_id
ORDER BY ct.type_name, c.name
"""

ALL_PRODUCTS   = "SELECT code, name, unit, sale_price FROM products ORDER BY code"
ALL_OPERATIONS = "SELECT code, name, cost FROM operations ORDER BY code"

ALL_MATERIALS = """
SELECT m.code, m.name, m.unit, m.purchase_price, c.name AS supplier
FROM materials m
JOIN counterparties c ON c.id = m.supplier_id
ORDER BY m.code
"""

ALL_SPECS = """
SELECT s.product_code, p.name AS product,
       s.material_code, m.name AS material,
       s.material_qty
FROM specifications s
JOIN products  p ON p.code = s.product_code
JOIN materials m ON m.code = s.material_code
ORDER BY s.product_code, s.material_code
"""

ORDER_EXISTS = "SELECT 1 FROM customer_orders WHERE order_no = %s"