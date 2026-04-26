import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def generate_report(input_file="outputs/orders_transformed.csv", output_dir="outputs"):
    if not os.path.exists(input_file):
        print(f"Error: No se encontró el archivo {input_file}.")
        return

    # Leer datos y asegurar tipo fecha
    df = pd.read_csv(input_file)
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    total_orders = len(df)
    if total_orders == 0:
        print("No hay datos para reportar.")
        return
        
    # Cálculos de KPIs
    delivered_orders = len(df[df['status'] == 'delivered'])
    failed_orders = len(df[df['status'] == 'failed'])
    
    success_rate = (delivered_orders / total_orders) * 100
    failure_rate = (failed_orders / total_orders) * 100
    
    # Tiempo promedio de entrega: usar solo valores válidos (mayores o iguales a 0)
    avg_delivery_time = df.loc[df['delivery_days'] >= 0, 'delivery_days'].mean()
    
    # Monto total
    total_amount = df['amount'].sum()
    
    print("="*60)
    print("REPORTE DE KPIs para Shinji")
    print("="*60)
    print(f"Total de pedidos:             {total_orders}")
    print(f"Tasa de entrega exitosa:      {success_rate:.2f}%")
    print(f"Tasa de fallo:                {failure_rate:.2f}%")
    print(f"Tiempo promedio de entrega:   {avg_delivery_time:.2f} días")
    print(f"Monto total despachado:       ${total_amount:,.2f} CLP")
    print("="*60)
    
    # Tabla resumen por región
    print("\n RESUMEN POR REGIÓN DE DESTINO")
    print("-" * 60)
    
    resumen_region = df.groupby('destination').agg(
        Total_Pedidos=('order_id', 'count'),
        Entregados=('status', lambda x: (x == 'delivered').sum()),
        Fallidos=('status', lambda x: (x == 'failed').sum()),
        Promedio_Dias_Entrega=('delivery_days', lambda x: x[x >= 0].mean())
    ).reset_index()
    
    print(resumen_region.to_string(index=False, float_format="%.2f"))
    print("-" * 60)
    
    # Gráfico 1: Cantidad de Pedidos por Status
    status_counts = df['status'].value_counts()
    plt.figure(figsize=(8, 5))
    status_counts.plot(kind='bar', color=['#4CAF50', '#FF9800', '#F44336', '#2196F3'])
    plt.title('Cantidad de Pedidos por Status', fontsize=14)
    plt.xlabel('Status', fontsize=12)
    plt.ylabel('Cantidad de Pedidos', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pedidos_por_status.png'), dpi=300)
    plt.close()
    
    # Gráfico 2: Evolución Semanal de Pedidos (Últimos 60 días)
    semanal = df.set_index('order_date').resample('W-MON').size()
    plt.figure(figsize=(10, 5))
    semanal.plot(kind='line', marker='o', color='#9C27B0', linewidth=2, markersize=8)
    plt.title('Evolución Semanal de Pedidos Creados (Últimos 60 Días)', fontsize=14)
    plt.xlabel('Semana', fontsize=12)
    plt.ylabel('Total Pedidos Creados', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'evolucion_semanal.png'), dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_report()
