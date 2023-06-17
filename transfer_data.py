import time
import re
import os
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Session
from models import IranAdvertises, Files, create_engine
from db_config import connection_string


def transfer():
    with Session(engine) as session:
        old_files = session.query(IranAdvertises).filter(IranAdvertises.Phone != None).all()
    with Session(engine) as session:
        for file in old_files:
            if file.Phone.isdigit():
                new_file = Files(Phone= file.Phone, Media=[i[1:-1] for i in file.Media.strip("][").split(", ")] if file.Media is not None else [], Title=file.Title, City=file.NeighbourHood, Rooms=file.Rooms)
                session.add(new_file)
        session.commit()


def sync_last_update():
    with Session(engine) as session:
        not_syncs = session.query(Files).filter(Files.LastUpdate == None).all()
        for file in not_syncs:
            file.LastUpdate = session.query(IranAdvertises).filter(IranAdvertises.Id)

if __name__ == '__main__':
    engine = create_engine(connection_string)
    transfer()
    print('done!')
    sync_last_update()
    print('done!')
