from sqlalchemy import INT, String, DateTime, Boolean, ARRAY
from sqlalchemy import create_engine, Column
from sqlalchemy_utils import EmailType
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from datetime import datetime
import enum
from logzero import logger
from db_config import connection_string

Base = declarative_base()


class PageStatus(enum.IntEnum):
    ReadyToCrawl = 0
    NoInfo = 50
    NoImage = 90
    Finished = 100
    NotFound = 404
    ServerError = 500
    Problem = 666


class Files(Base):
    __tablename__ = 'Files'
    Id = Column(INT, primary_key=True)
    AgentName = Column(String, default=None)
    AgentPhone = Column(String, default=None)
    Phone = Column(String, default=None)
    Media = Column(ARRAY(String), default=None)
    Title = Column(String, default=None)
    Province = Column(String, default=None)
    City = Column(String, default=None)
    Village = Column(String, default=None)
    Address = Column(String, default=None)
    Floor = Column(INT, default=None)
    TotalFloors = Column(INT, default=None)
    HouseNumber = Column(INT, default=None)
    PostalCode = Column(INT, default=None)
    OwnershipType = Column(String, default=None)
    EnvironmentType = Column(String, default=None)
    AccessPath = Column(String, default=None)
    AccessDescription = Column(String, default=None)
    NeighbourhoodShip = Column(String, default=None)
    DistanceToPlaces = Column(String, default=None)
    Walls = Column(String, default=None)
    UnitArea = Column(INT, default=None)
    TotalArea = Column(INT, default=None)
    Capacity = Column(INT, default=None)
    MaxCapacity = Column(INT, default=None)
    Rooms = Column(INT, default=None)
    SleepServices = Column(String, default=None)
    SingleBed = Column(INT, default=None)
    DoubleBed = Column(INT, default=None)
    FoldingSofa = Column(INT, default=None)
    WCQuantity = Column(INT, default=None)
    SanitaryFacilities = Column(String, default=None)
    Pool = Column(Boolean, default=None)
    DrySauna = Column(Boolean, default=None)
    WetSauna = Column(Boolean, default=None)
    Parking = Column(Boolean, default=None)
    Balcony = Column(Boolean, default=None)
    EldersReception = Column(Boolean, default=None)
    DisabledReception = Column(Boolean, default=None)
    TV = Column(Boolean, default=None)
    DigitalReciever = Column(Boolean, default=None)
    Refrigerator = Column(Boolean, default=None)
    Oven = Column(Boolean, default=None)
    DiningService = Column(Boolean, default=None)
    Furniture = Column(Boolean, default=None)
    VacuumMachine = Column(Boolean, default=None)
    PersianToilet = Column(Boolean, default=None)
    Toilet = Column(Boolean, default=None)
    Bathroom = Column(Boolean, default=None)
    DiningFurniture = Column(Boolean, default=None)
    PrivateYard = Column(Boolean, default=None)
    Elevator = Column(Boolean, default=None)
    EvaporativeCooler = Column(Boolean, default=None)
    AirConditioner = Column(Boolean, default=None)
    Radiator = Column(Boolean, default=None)
    Fireplace = Column(Boolean, default=None)
    FreeWifi = Column(Boolean, default=None)
    Iron = Column(Boolean, default=None)
    WashingMachine = Column(Boolean, default=None)
    Jacuzzi = Column(Boolean, default=None)
    Microwave = Column(Boolean, default=None)
    Barbecue = Column(Boolean, default=None)
    Bathtub = Column(Boolean, default=None)
    TeaMaker = Column(Boolean, default=None)
    BoardGame = Column(Boolean, default=None)
    PingPong = Column(Boolean, default=None)
    SoundSystem = Column(Boolean, default=None)
    Billiards = Column(Boolean, default=None)
    TableFootball = Column(Boolean, default=None)
    GameConsole = Column(Boolean, default=None)
    CCTV = Column(Boolean, default=None)
    Bed = Column(Boolean, default=None)
    Porch = Column(Boolean, default=None)
    KidsPool = Column(Boolean, default=None)
    ColdWaterPool = Column(Boolean, default=None)
    AirHockey = Column(Boolean, default=None)
    JacuzziTub = Column(Boolean, default=None)
    Pets = Column(Boolean, default=None)
    Seremony = Column(Boolean, default=None)
    MCIAnten = Column(Boolean, default=None)
    IrancellAnten = Column(Boolean, default=None)
    MCINet = Column(Boolean, default=None)
    IrancellNet = Column(Boolean, default=None)
    HallFacilities = Column(String, default=None)
    HallHeater = Column(String, default=None)
    HallCooler = Column(String, default=None)
    RoomHeater = Column(String, default=None)
    RoomCooler = Column(String, default=None)
    Yard = Column(String, default=None)
    Garden = Column(String, default=None)
    GardenFacilities = Column(String, default=None)
    GardenDescription = Column(String, default=None)
    View = Column(String, default=None)
    ProsperityFacilities = Column(String, default=None)
    JoyFacilities = Column(String, default=None)
    CookingFacilities = Column(String, default=None)
    Dishes = Column(String, default=None)
    EntranceSteps = Column(INT, default=None)
    EnterHour = Column(String, default=None)
    ExitHour = Column(String, default=None)
    MinStay = Column(String, default=None)
    MaxStay = Column(String, default=None)
    LastCalenderAvailable = Column(DateTime, default=None)
    CancelRules = Column(String, default=None)
    RequiredDocuments = Column(String, default=None)
    PetsRules = Column(String, default=None)
    SeremonyConditions = Column(String, default=None)
    OtherRules = Column(String, default=None)
    HostCode = Column(String, default=None)
    HostName = Column(String, default=None)
    SuggestedPrice = Column(INT, default=None)
    OtherDescriptions = Column(String, default=None)
    LastUpdate = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"ID: {self.Id}, Ad_title: {self.Title}"

class IranAdvertises(Base):
    __tablename__ = 'IranAdvertises'
    Id = Column(INT, primary_key=True)
    Phone = Column(String, default=None)
    Title = Column(String, default=None)
    City = Column(String, default=None)
    NeighbourHood = Column(String, default=None)
    Rooms = Column(INT, default=None)
    Media = Column(String, default=None)
    AdvertiseUrl = Column(String, default=None)
    Descriptions = Column(String, default=None)
    Status = Column(INT, default=PageStatus.ReadyToCrawl)
    RetryCount = Column(INT, default=0)
    LastUpdate = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"ID: {self.Id}, Ad_title: {self.Title}"


def create_db():
    logger.info('Creating Database')
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_db()
