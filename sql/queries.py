import sys
import os
import pandas as pd
from sqlalchemy import create_engine, text

# Agregar el directorio raíz al path para importar el engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.schema import DATABASE_URL

# Conectamos usando SQLAlchemy
engine = create_engine(DATABASE_URL)

# Diccionario con todas las consultas SQL requeridas
queries = {
    "Q1 — Resumen por Instalación": """
        -- Lista instalaciones activas, total despachados, entregados y monto promedio.
        SELECT 
            f.name AS instalacion,
            COUNT(o.order_id) AS total_pedidos_despachados,
            SUM(CASE WHEN o.status = 'delivered' THEN 1 ELSE 0 END) AS total_entregados,
            ROUND(AVG(CASE WHEN o.status = 'delivered' THEN o.amount ELSE NULL END), 2) AS monto_promedio_entregados
        FROM facilities f
        LEFT JOIN supply_orders o ON f.facility_id = o.origin_id
        WHERE f.active = 1 -- INSTALACIONES ACTIVAS
        GROUP BY f.facility_id, f.name
        ORDER BY total_pedidos_despachados DESC;
    """,
    
    "Q2 — Top Transportistas (Últimos 30 días)": """
        -- Top 5 transportistas con más pedidos entregados en los últimos 30 días
        -- Nota: Uso date('now', '-30 days') que es específico de SQLite para fechas
        SELECT +
            s.name AS transportista,
            s.vehicle_type AS tipo_vehiculo,
            f.name AS instalacion_origen,
            COUNT(o.order_id) AS conteo_entregas
        FROM suppliers s
        JOIN supply_orders o ON s.supplier_id = o.supplier_id
        JOIN facilities f ON o.origin_id = f.facility_id
        WHERE o.status = 'delivered' 
          AND o.delivery_date >= date('now', '-30 days')
        GROUP BY s.supplier_id, s.name, s.vehicle_type, f.name
        ORDER BY conteo_entregas DESC
        LIMIT 5;
    """,
    
    "Q3 — Tasa de Fallo por Región": """
        -- Tasa de fallo por región (sólo regiones con más de 10 pedidos)
        SELECT 
            destination AS region_destino,
            COUNT(order_id) AS total_pedidos,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS pedidos_fallidos,
            ROUND((CAST(SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(order_id)) * 100, 2) AS tasa_fallo_pct
        FROM supply_orders
        GROUP BY destination
        HAVING COUNT(order_id) > 10
        ORDER BY tasa_fallo_pct DESC;
    """,
    
    "Q4 — Pedidos Sin Transportista": """
        -- Pedidos pending/in_transit sin transportista y días transcurridos
        -- Nota: Uso julianday() de SQLite para calcular la diferencia de días
        SELECT 
            order_id,
            recipient_name AS destinatario,
            destination AS region,
            order_date AS fecha_pedido,
            CAST(julianday('now') - julianday(order_date) AS INTEGER) AS dias_transcurridos
        FROM supply_orders
        WHERE status IN ('pending', 'in_transit')
          AND supplier_id IS NULL;
    """,
    
    "Q5 — Tiempo Promedio de Entrega por Tipo de Vehículo": """
        -- Tiempo promedio, mínimo y máximo de entrega agrupado por tipo de vehículo
        -- Nota: julianday(delivery_date) - julianday(order_date) calcula la diferencia en días en SQLite
        SELECT 
            s.vehicle_type AS tipo_vehiculo,
            ROUND(AVG(julianday(o.delivery_date) - julianday(o.order_date)), 2) AS tiempo_promedio_dias,
            CAST(MIN(julianday(o.delivery_date) - julianday(o.order_date)) AS INTEGER) AS min_dias,
            CAST(MAX(julianday(o.delivery_date) - julianday(o.order_date)) AS INTEGER) AS max_dias
        FROM supply_orders o
        JOIN suppliers s ON o.supplier_id = s.supplier_id
        WHERE o.status = 'delivered'
        GROUP BY s.vehicle_type;
    """,
    
    "Q6 — Rendimiento Mensual (Últimos 3 meses)": """
        -- Métricas agregadas por mes cronológicamente
        -- Nota: strftime('%Y-%m') extrae el mes en SQLite
        SELECT 
            strftime('%Y-%m', order_date) AS mes,
            COUNT(order_id) AS total_creados,
            SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS total_entregados,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS total_fallidos,
            SUM(CASE WHEN status = 'delivered' THEN amount ELSE 0 END) AS monto_total_entregados
        FROM supply_orders
        WHERE order_date >= date('now', 'start of month', '-2 months')
        GROUP BY mes
        ORDER BY mes ASC;
    """
}

def ejecutar_queries():
    # Usamos pandas para imprimir los resultados en forma de tabla limpia
    with engine.connect() as conn:
        for titulo, query in queries.items():
            print(f"\n{'='*80}")
            print(f"> {titulo}")
            print(f"{'='*80}")
            
            # Ejecutar el query y cargar el resultado en un DataFrame de pandas
            df = pd.read_sql(text(query), conn)
            
            if df.empty:
                print("No hay resultados para esta consulta.\n")
            else:
                print(df.to_string(index=False))
            print("\n")

if __name__ == "__main__":
    ejecutar_queries()
    print("Felicidades Shinji, sabes preguntar")
