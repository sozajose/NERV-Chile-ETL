from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

# ==========================================
# 1. Configuración del Engine
# ==========================================
DATABASE_URL = "sqlite:///data/NERV.db"
engine = create_engine(DATABASE_URL, echo=False)

# ==========================================
# 2. Definición de la Base
# ==========================================
Base = declarative_base()

# ==========================================
# 3. Configuración de la Sesión
# ==========================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==========================================
# 4. Generación de Tablas
# ==========================================

#Tabla facilities
class Facility(Base):
    __tablename__ = 'facilities'
    
    facility_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    city = Column(String, nullable=False)
    type = Column(String, nullable=False)
    active = Column(Integer, nullable=False, default=1)

    def __repr__(self):
        return f"<Facility(facility_id={self.facility_id}, name='{self.name}', region='{self.region}', city='{self.city}', type='{self.type}', active='{self.active}')>"

#Tabla suppliers
class Supplier(Base):
    __tablename__ = 'suppliers'
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    facility_id = Column(Integer, ForeignKey("facilities.facility_id"), nullable=False)
    status = Column(String, nullable=False, default="available")

    def __repr__(self):
        return f"<Supplier(supplier_id={self.supplier_id}, name='{self.name}', vehicle_type='{self.vehicle_type}', facility_id='{self.facility_id}', status='{self.status}')>"

#Tabla transactions
class SupplyOrders(Base):
    __tablename__ = 'supply_orders'
    __table_args__ = (CheckConstraint('amount > 0'),)

    order_id = Column(Integer, primary_key=True, index=True)
    origin_id = Column(Integer, ForeignKey("facilities.facility_id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True)
    recipient_name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    delivery_date = Column(Date)
    status = Column(String, nullable=False, default="pending")
    amount = Column(Float, nullable=False)

    def __repr__(self):
        return  f"<SupplyOrders(order_id={self.order_id}, origin_id='{self.origin_id}', supplier_id='{self.supplier_id}', recipient_name='{self.recipient_name}', destination='{self.destination}', order_date='{self.order_date}', delivery_date='{self.delivery_date}', status='{self.status}', amount='{self.amount}')>"

# ==========================================
# 5. Inicialización de la Base de Datos
# ==========================================
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Felicidades Shinji, creaste la BD")

if __name__ == "__main__":
    init_db()
