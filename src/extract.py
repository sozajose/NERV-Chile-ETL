import argparse
import pandas as pd
from sqlalchemy import create_engine, text
import os

def extract_data(db_path, output_dir="outputs", output_file="orders_raw.csv"):
    # 1. Asegurar que el directorio de output exista
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Conexión a la base de datos
    engine = create_engine(db_path)
    
    # 3. Consulta SQL para últimos 60 días. Utilicé el "hoy" (26/04) como la fecha de ejecución, así que si se pregunta después, traerá otros resultados.
    query = """
        SELECT *
        FROM supply_orders
        WHERE order_date >= date('now', '-60 days')
    """
    
    try:
        with engine.connect() as conn:
            # 4. Extraer en DataFrame
            df = pd.read_sql(text(query), conn)
            
            if df.empty:
                print("Shinji, no hay datos XD")
                return df
            
            # 5. Exportar a CSV
            output_path = os.path.join(output_dir, output_file)
            df.to_csv(output_path, index=False)
            
            # 6. Identificar rango de fechas
            min_date = df['order_date'].min()
            max_date = df['order_date'].max()
            
            print("="*50)
            print("Shinji, los datos han sido extraídos. Detalle:")
            print("="*50)
            print(f"Origen de datos: {db_path}")
            print(f"Registros extraídos: {len(df)}")
            print(f"Rango de fechas: Desde {min_date} hasta {max_date}")
            print(f"Archivo exportado: {output_path}")
            print("="*50)
            
            return df
            
    except Exception as e:
        print(f"Shinji, todo salió mal, esta es la razón: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrae pedidos de los últimos 60 días.")
    # Parámetro configurable
    parser.add_argument(
        "--db-path", 
        type=str, 
        default="sqlite:///data/NERV.db",
        help="Ruta de conexión SQLAlchemy a la base de datos."
    )
    args = parser.parse_args()
    
    # Al estar en src/, nos aseguramos que outputs/ se cree en la raíz del proyecto
    # si ejecutamos desde la raíz: python src/extract.py
    extract_data(db_path=args.db_path)
