import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base,relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base





# 1. Fetch the string safely from system variables
raw_db_url = os.environ.get("TRIPPEN_POSTGRES_URL")

# 2. Modify the URL prefix so SQLAlchemy can map it to its internal driver
if raw_db_url and raw_db_url.startswith("postgresql://"):
    TRIPPEN_POSTGRES_URL = make_url(raw_db_url).set(drivername="postgresql+psycopg")
else:
    # Safe fallback wrapper for local SQLite practice/tests if variables are empty
    TRIPPEN_POSTGRES_URL = "sqlite:///./test.db"

# 3. Create the operational engine with connection pooling optimized for Serverless
engine = create_engine(
    TRIPPEN_POSTGRES_URL,
    pool_size=1,        # Keep connection footprints tiny for serverless environments
    max_overflow=0,
    pool_pre_ping=True,  # Test the safety of connections instantly before querying
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    client = Column(String, primary_key=True)
    distanceFromOffice = Column(Float)
    fullAddress = Column(Text)
    isDisabled = Column(Boolean, default=False)
    phoneNumber = Column(String)
    email = Column(String)
    contactPerson = Column(String)
    city = Column(String)
    trips = relationship('Trip', back_populates='client_rel', cascade="all, delete-orphan")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    regNumber = Column(String, primary_key=True)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    kmPerLiter = Column(Float)
    currentOdometer = Column(Float, default=0)
    ratePerKm = Column(Float, default=0)
    isDisabled = Column(Boolean, default=False)
    trips = relationship('Trip', back_populates='vehicle_rel', cascade="all, delete-orphan")

class PublicHoliday(Base):
    __tablename__ = 'public_holidays'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String)
    year = Column(Integer)
    date = Column(String)
    name = Column(String)

class Setting(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(Text)

class Trip(Base):
    __tablename__ = 'trips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String)
    client = Column(String, ForeignKey('clients.client'))
    city = Column(String)
    distanceKm = Column(Float)
    totalDistanceKm = Column(Float)
    tripType = Column(Integer)
    isPrivateTrip = Column(Boolean, default=False)
    vehicleRegNumber = Column(String, ForeignKey('vehicles.regNumber'))
    client_rel = relationship('Client', back_populates='trips')
    vehicle_rel = relationship('Vehicle', back_populates='trips')
