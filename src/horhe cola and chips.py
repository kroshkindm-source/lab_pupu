import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

conn = sqlite3.connect('kitov_A.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS zaselenie(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
flat INTEGER,
passport_num TEXT,
inst TEXT,
contacts TEXT,
obshaga_num INTEGER,
narush TEXT)''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS viselenie(
id INTEGER PRIMARY KEY AUTOINCREMENT,
id_vis INTEGER FOREIGNKEY REFERENCES zaselenie(id),
sost TEXT,
ready BOOLEAN)''')
conn.commit()
conn.close()
Base = declarative_base()


class Zaselenie(Base):
    __tablename__ = 'zaselenie'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    flat = Column(Integer)
    passport_num = Column(String)
    inst = Column(String)
    contacts = Column(String)
    obshaga_num = Column(Integer)
    narush = Column(String)

    viselenie = relationship("Viselenie", back_populates="zaselenie", uselist=False)

    def __repr__(self):
        return f"<Zaselenie(id={self.id}, name='{self.name}', flat={self.flat})>"


class Viselenie(Base):
    __tablename__ = 'viselenie'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_vis = Column(Integer, ForeignKey('zaselenie.id'))
    sost = Column(String)
    ready = Column(Boolean)

    zaselenie = relationship("Zaselenie", back_populates="viselenie")

    def __repr__(self):
        return f"<Viselenie(id={self.id}, id_vis={self.id_vis}, ready={self.ready})>"


def create_database():
    engine = create_engine('sqlite:///kitov_A.db')
    Base.metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    engine = create_database()

    Session = sessionmaker(bind=engine)
    session = Session()

    new_zaselenie = Zaselenie(
        name="Китов Артём Андреевич",
        flat=101,
        passport_num="6969 228228",
        inst="ИРИТ",
        contacts="+79991234567",
        obshaga_num=1,
        narush="Нет нарушений"
    )

    session.add(new_zaselenie)
    session.commit()

    new_viselenie = Viselenie(
        id_vis=new_zaselenie.id,
        sost="уд",
        ready=False
    )

    session.add(new_viselenie)
    session.commit()

    zaselenie_records = session.query(Zaselenie).all()
    print("Заселение:")
    for record in zaselenie_records:
        print(record)

    viselenie_records = session.query(Viselenie).all()
    print("\nВыселение:")
    for record in viselenie_records:
        print(record)

    session.close()

