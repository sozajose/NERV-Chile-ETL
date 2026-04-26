import pandas as pd
import numpy as np
import os

def transform_data(input_file="outputs/orders_raw.csv", output_file="outputs/orders_transformed.csv"):
    if not os.path.exists(input_file):
        print(f"Shinji, ERROR FATAL, no está el {input_file}. Asegúrate de ejecutar el extract.")
        return
    
    # 1. A leer (AUNQUE NO LO CREAN, SÉ LEER XD)
    df = pd.read_csv(input_file)
    
    # Asegurar que las fechas son de tipo datetime para poder hacer operaciones (no lo eran, así que tocaba convertirlas :v)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['delivery_date'] = pd.to_datetime(df['delivery_date'])
    
    # 2. Transformaciones
    
    # a. Días entre order_date y delivery_date (quedará en NaN si delivery_date es nulo)
    df['delivery_days'] = (df['delivery_date'] - df['order_date']).dt.days
    
    # b. True si fue entregado en más de 3 días (si es NaN devuelve False)
    df['is_late'] = df['delivery_days'] > 3
    
    # c. Categorización del monto
    condiciones = [
        df['amount'] < 50000,
        (df['amount'] >= 50000) & (df['amount'] <= 200000),
        df['amount'] > 200000
    ]
    valores = ['bajo', 'medio', 'alto']
    df['amount_range'] = np.select(condiciones, valores, default='desconocido')
    
    # 3. Reporte
    print("="*50)
    print("Shinji, aquí están los resultados de la transformación:")
    print("="*50)
    
    # i. Pedidos sin transportista
    pedidos_sin_transportista = df['supplier_id'].isna().sum()
    print(f"Registros procesados: {len(df)}")
    print(f"Pedidos SIN transportista asignado: {pedidos_sin_transportista}")
    print("-" * 50)
    print("Veamos si hay inconsistencias:")
    
    # ii. Inconsistencia: Delivered sin delivery_date
    delivered_sin_fecha = df[(df['status'] == 'delivered') & (df['delivery_date'].isna())]
    if len(delivered_sin_fecha) > 0:
        print(f"[!] ALERTA SHINJI: {len(delivered_sin_fecha)} pedidos 'delivered' NO tienen fecha de entrega. Se entregó o no?")
    else:
        print("[OK] Shinji, todos los pedidos 'delivered' tienen fecha de entrega válida.")
        
    # iii. Inconsistencia: Tiempos negativos (delivery_date antes que order_date)
    tiempos_negativos = df[df['delivery_days'] < 0]
    if len(tiempos_negativos) > 0:
        print(f"[!] ALERTA SHINJI: {len(tiempos_negativos)} pedidos tienen fecha de entrega ANTERIOR al pedido. Acaso somos una Caja de Compensación?")
    else:
        print("[OK] Shinji, no hay inconsistencias de fechas temporales negativas.")
        
    # iv. Inconsistencia: No entregados pero con fecha de entrega
    no_entregados_con_fecha = df[(df['status'].isin(['pending', 'in_transit'])) & (~df['delivery_date'].isna())]
    if len(no_entregados_con_fecha) > 0:
        print(f"[!] ALERTA SHINJI: {len(no_entregados_con_fecha)} pedidos pendientes/en tránsito TIENEN fecha de entrega. Acaso se teletransportan?")
    else:
        print("[OK] Shinji, los pedidos pendientes/en tránsito no tienen fechas de entrega registradas.")

    # 4. Exportar el DataFrame transformado
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    transform_data()
