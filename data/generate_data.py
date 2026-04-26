import sys
import os
import random
from datetime import timedelta
from faker import Faker

# Agregar el directorio raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sql.schema import SessionLocal, Facility, Supplier, SupplyOrders, init_db

def poblar_datos():
    # Instanciar faker con CHILE LO MÁS GRANDE QUE EXISTE
    fake = Faker('es_CL')
    
    init_db()
    
    with SessionLocal() as session:
        # Evitar duplicar si ya tiene datos
        if session.query(Facility).count() > 0:
            print("Shinji, ya hay datos, no es necesario hacer esto.")
            return

        # ==========================================
        # 1. Crear Facilities
        # ==========================================
        regiones = ['Norte', 'Centro', 'Sur', 'Metropolitana']
        facilities = []
        for i in range(5):
            f = Facility(
                name=f"NERV Branch - {fake.city()}",
                region=random.choice(regiones),
                city=fake.city(),
                type=random.choice(['base_principal', 'deposito', 'laboratorio']),
                # Al menos 1 fuera de servicio (indice 0)
                active=0 if i == 0 else 1
            )
            facilities.append(f)
        session.add_all(facilities)
        session.commit() # Commit para obtener IDs
        
        # ==========================================
        # 2. Crear Suppliers
        # ==========================================
        suppliers = []
        for i in range(15):
            if i < 2:
                status = "inactive"
            else:
                status = random.choice(["available", "on_route"])
                
            s = Supplier(
                name=fake.company(),
                vehicle_type=random.choice(['furgon', 'camion', 'moto']),
                facility_id=random.choice(facilities).facility_id,
                status=status
            )
            suppliers.append(s)
        session.add_all(suppliers)
        session.commit() # Commit para obtener IDs

        # ==========================================
        # 3. Crear SupplyOrders
        # ==========================================
        orders = []
        for i in range(300):
            # Fecha en los últimos 90 días
            order_date = fake.date_between(start_date="-90d", end_date="today")
            
            # Distribución de estado: 75% delivered, 10% in_transit, 8% failed, 7% pending
            rand = random.random()
            if rand < 0.75:
                status = "delivered"
            elif rand < 0.85:
                status = "in_transit"
            elif rand < 0.93:
                status = "failed"
            else:
                status = "pending"
                
            delivery_date = None
            if status == "delivered":
                # Delivery date entre 1 y 7 días después de order_date
                dias_demora = random.randint(1, 7)
                delivery_date = order_date + timedelta(days=dias_demora)
                
            # Montos entre $8.000 y $450.000 CLP
            # Para distribución realista, 70% de las veces son compras menores a 100k
            if random.random() < 0.7:
                amount = random.randint(8, 100) * 1000.0
            else:
                amount = random.randint(101, 450) * 1000.0

            # NUEVO: Dejar algunos pendientes SIN supplier asignado
            if status == 'pending' and random.random() < 0.5:
                supplier_id = None
            else:
                supplier_id = random.choice(suppliers).supplier_id

            order = SupplyOrders(
                origin_id=random.choice(facilities).facility_id,
                supplier_id=supplier_id,
                recipient_name=fake.name(),
                destination=random.choice(regiones),
                order_date=order_date,
                delivery_date=delivery_date,
                status=status,
                amount=amount
            )
            orders.append(order)
            
        session.add_all(orders)
        session.commit()

        # ==========================================
        # 4. Inyección de Inconsistencias (Para pruebas de validación)
        # ==========================================
        inconsistencias = [
            # 1. Delivered sin delivery_date
            SupplyOrders(
                origin_id=random.choice(facilities).facility_id,
                supplier_id=random.choice(suppliers).supplier_id,
                recipient_name="Error Test 1",
                destination="Metropolitana",
                order_date=fake.date_between(start_date="-10d", end_date="today"),
                delivery_date=None,  # Aquí está el error
                status="delivered",
                amount=25000.0
            ),
            # 2. Tiempos negativos (delivery_date antes que order_date)
            SupplyOrders(
                origin_id=random.choice(facilities).facility_id,
                supplier_id=random.choice(suppliers).supplier_id,
                recipient_name="Error Test 2",
                destination="Sur",
                order_date=fake.date_between(start_date="today", end_date="today"),
                delivery_date=fake.date_between(start_date="-30d", end_date="-20d"), # Fecha pasada
                status="delivered",
                amount=150000.0
            ),
            # 3. No entregado pero CON fecha de entrega
            SupplyOrders(
                origin_id=random.choice(facilities).facility_id,
                supplier_id=random.choice(suppliers).supplier_id,
                recipient_name="Error Test 3",
                destination="Norte",
                order_date=fake.date_between(start_date="today", end_date="today"),
                delivery_date=fake.date_between(start_date="today", end_date="today"), # No debería tener fecha si es pending
                status="pending",
                amount=90000.0
            )
        ]
        
        session.add_all(inconsistencias)
        session.commit()
        print("Inconsistencias inyectadas con éxito para el reporte de Shinji.")
        print("Felicidades Shinji, poblaste la BD")

if __name__ == "__main__":
    poblar_datos()
