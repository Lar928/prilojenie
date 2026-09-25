SELECT
    ct.type_name       AS "Тип",
    c.id               AS "ID",
    c.name             AS "Наименование",
    c.inn              AS "ИНН",
    c.address          AS "Адрес",
    c.phone            AS "Телефон"
FROM counterparties c
JOIN counterparty_types ct ON ct.type_id = c.type_id
ORDER BY ct.type_name, c.name;


SELECT DISTINCT
    c.id      AS "ID покупателя",
    c.name    AS "Наименование",
    c.inn     AS "ИНН",
    c.phone   AS "Телефон"
FROM counterparties c
JOIN customer_orders co ON co.customer_id = c.id
WHERE c.type_id = 1
ORDER BY c.name;


SELECT
    c.id              AS "ID поставщика",
    c.name            AS "Поставщик",
    m.code            AS "Код материала",
    m.name            AS "Материал",
    m.unit            AS "Ед. изм.",
    m.purchase_price  AS "Цена закупки"
FROM materials m
JOIN counterparties c ON c.id = m.supplier_id
WHERE c.type_id = 2
ORDER BY c.name, m.name;


SELECT
    co.order_no    AS "Номер заказа",
    co.order_date  AS "Дата",
    c.name         AS "Покупатель",
    p.name         AS "Продукция",
    oi.quantity    AS "Количество",
    co.status      AS "Статус"
FROM customer_orders co
JOIN counterparties c  ON c.id   = co.customer_id
JOIN order_items   oi  ON oi.order_no = co.order_no
JOIN products      p   ON p.code = oi.product_code
ORDER BY co.order_date, co.order_no;


SELECT
    co.order_no                       AS "Номер заказа",
    co.order_date                     AS "Дата",
    c.name                            AS "Покупатель",
    p.name                            AS "Продукция",
    p.sale_price                      AS "Цена",
    oi.quantity                       AS "Количество",
    p.sale_price * oi.quantity        AS "Сумма заказа"
FROM customer_orders co
JOIN counterparties c  ON c.id        = co.customer_id
JOIN order_items   oi  ON oi.order_no = co.order_no
JOIN products      p   ON p.code      = oi.product_code
ORDER BY co.order_date, co.order_no;


SELECT
    p.code                                              AS "Код продукции",
    p.name                                              AS "Продукция",
    m.code                                              AS "Код материала",
    m.name                                              AS "Материал",
    m.unit                                              AS "Ед. изм.",
    s.material_qty                                      AS "Норма расхода",
    m.purchase_price                                    AS "Цена материала",
    ROUND(s.material_qty * m.purchase_price, 2)         AS "Стоимость на единицу"
FROM specifications s
JOIN products  p ON p.code = s.product_code
JOIN materials m ON m.code = s.material_code
WHERE p.code = 'PR001'
ORDER BY m.name;


SELECT
    p.code                                                  AS "Код продукции",
    p.name                                                  AS "Продукция",
    ROUND(
        COALESCE(SUM(s.material_qty * m.purchase_price), 0),
        2
    )                                                       AS "Материальная себестоимость"
FROM products p
LEFT JOIN specifications s ON s.product_code = p.code
LEFT JOIN materials     m ON m.code          = s.material_code
GROUP BY p.code, p.name
ORDER BY p.code;


SELECT
    p.code                                              AS "Код продукции",
    p.name                                              AS "Продукция",
    ROUND(
        COALESCE(SUM(po.operation_qty * o.cost), 0),
        2
    )                                                   AS "Стоимость операций"
FROM products p
LEFT JOIN product_operations po ON po.product_code   = p.code
LEFT JOIN operations         o  ON o.code            = po.operation_code
GROUP BY p.code, p.name
ORDER BY p.code;



WITH material_costs AS (
    SELECT
        p.code AS product_code,
        COALESCE(SUM(s.material_qty * m.purchase_price), 0) AS material_cost
    FROM products p
    LEFT JOIN specifications s ON s.product_code = p.code
    LEFT JOIN materials     m ON m.code          = s.material_code
    GROUP BY p.code
),
operation_costs AS (
    SELECT
        p.code AS product_code,
        COALESCE(SUM(po.operation_qty * o.cost), 0) AS operations_cost
    FROM products p
    LEFT JOIN product_operations po ON po.product_code = p.code
    LEFT JOIN operations         o  ON o.code          = po.operation_code
    GROUP BY p.code
)
SELECT
    p.code                                          AS "Код продукции",
    p.name                                          AS "Продукция",
    ROUND(mc.material_cost, 2)                      AS "Материалы",
    ROUND(oc.operations_cost, 2)                    AS "Операции",
    ROUND(mc.material_cost + oc.operations_cost, 2) AS "Себестоимость",
    p.sale_price                                    AS "Цена продажи",
    ROUND(p.sale_price - (mc.material_cost + oc.operations_cost), 2)
                                                    AS "Расчётная маржа"
FROM products p
JOIN material_costs  mc ON mc.product_code = p.code
JOIN operation_costs oc ON oc.product_code = p.code
ORDER BY p.code;


SELECT
    po.production_no      AS "Номер производства",
    po.customer_order_no  AS "Заказ покупателя",
    po.start_date         AS "Дата запуска",
    po.quantity           AS "Количество",
    po.status             AS "Статус",
    c.name                AS "Покупатель",
    p.name                AS "Продукция"
FROM production_orders po
JOIN customer_orders co ON co.order_no    = po.customer_order_no
JOIN counterparties  c  ON c.id           = co.customer_id
JOIN order_items     oi ON oi.order_no    = co.order_no
JOIN products        p  ON p.code         = oi.product_code
WHERE po.status IN ('В работе', 'Запланирован')
ORDER BY po.start_date, po.production_no;



SELECT
    c.id                              AS "ID покупателя",
    c.name                            AS "Покупатель",
    COUNT(co.order_no)                AS "Количество заказов",
    COALESCE(SUM(oi.quantity), 0)     AS "Всего единиц продукции"
FROM counterparties c
LEFT JOIN customer_orders co ON co.customer_id = c.id
LEFT JOIN order_items     oi ON oi.order_no    = co.order_no
WHERE c.type_id = 1
GROUP BY c.id, c.name
ORDER BY COUNT(co.order_no) DESC, c.name;



SELECT
    p.code                                   AS "Код продукции",
    p.name                                   AS "Продукция",
    SUM(oi.quantity)                         AS "Продано единиц",
    ROUND(SUM(oi.quantity * p.sale_price), 2) AS "Сумма продаж"
FROM order_items oi
JOIN products p ON p.code = oi.product_code
GROUP BY p.code, p.name
ORDER BY SUM(oi.quantity * p.sale_price) DESC
LIMIT 3;
