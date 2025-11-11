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


def get_residents_by_flat(session, flat_number):
    results = session.query(Zaselenie, Viselenie). \
        join(Viselenie, Zaselenie.id == Viselenie.id_vis). \
        filter(Zaselenie.flat == flat_number). \
        all()

    flat_residents = []
    for zaselenie, viselenie in results:
        flat_residents.append({
            'id': zaselenie.id,
            'name': zaselenie.name,
            'passport_num': zaselenie.passport_num,
            'institute': zaselenie.inst,
            'contacts': zaselenie.contacts,
            'obshaga_num': zaselenie.obshaga_num,
            'violations': zaselenie.narush,
            'eviction_status': viselenie.sost,
            'ready_to_evict': viselenie.ready
        })

    return flat_residents


def print_residents(residents, flat_number):
    if not residents:
        print(f"\nВ комнате {flat_number} никто не проживает.")
        return

    print(f"\n{'=' * 60}")
    print(f"ЖИТЕЛИ КОМНАТЫ {flat_number}")
    print(f"{'=' * 60}")

    for i, resident in enumerate(residents, 1):
        print(f"Житель #{i}:")
        print(f"  ФИО: {resident['name']}")
        print(f"  Паспорт: {resident['passport_num']}")
        print(f"  Институт: {resident['institute']}")
        print(f"  Контакты: {resident['contacts']}")
        print(f"  Общежитие: №{resident['obshaga_num']}")
        print(f"  Нарушения: {resident['violations']}")
        print(f"  Состояние комнаты2: {resident['eviction_status']}")
        print(f"  Готов к выселению: {'Да' if resident['ready_to_evict'] else 'Нет'}")
        print(f"{'-' * 40}")


def add_new_resident(session):
    print("\n" + "=" * 50)
    print("ДОБАВЛЕНИЕ НОВОГО ЖИТЕЛЯ")
    print("=" * 50)

    try:
        name = input("ФИО: ")
        flat = int(input("Номер комнаты: "))
        passport_num = input("Номер паспорта: ")
        inst = input("Институт: ")
        contacts = input("Контакты: ")
        obshaga_num = int(input("Номер общежития: "))
        narush = input("Нарушения: ")

        new_zaselenie = Zaselenie(
            name=name,
            flat=flat,
            passport_num=passport_num,
            inst=inst,
            contacts=contacts,
            obshaga_num=obshaga_num,
            narush=narush
        )

        session.add(new_zaselenie)
        session.commit()

        sost = input("Состояние комнаты"
                     " (уд/неуд): ")
        ready = input("Готов к выселению (да/нет): ").lower() == 'да'

        new_viselenie = Viselenie(
            id_vis=new_zaselenie.id,
            sost=sost,
            ready=ready
        )

        session.add(new_viselenie)
        session.commit()

        print(f"\nЖитель {name} успешно добавлен в комнату {flat}!")

    except ValueError:
        print("Ошибка: некорректный ввод числовых данных")
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")
        session.rollback()


def search_residents_by_flat(session):
    while True:
        print("\n" + "=" * 50)
        print("ПОИСК ЖИТЕЛЕЙ ПО НОМЕРУ КОМНАТЫ")
        print("=" * 50)
        print("1 - Найти жителей комнаты")
        print("2 - Показать все существующие комнаты")
        print("3 - Назад")

        choice = input("\nВыберите действие (1-3): ").strip()

        if choice == '1':
            try:
                flat_number = int(input("Введите номер комнаты для поиска: "))
                residents = get_residents_by_flat(session, flat_number)
                print_residents(residents, flat_number)

                if residents:
                    input("\nНажмите Enter для продолжения...")
                else:
                    all_flats = session.query(Zaselenie.flat).distinct().all()
                    if all_flats:
                        flats_list = [flat[0] for flat in all_flats]
                        print(f"\nСуществующие комнаты: {sorted(flats_list)}")
                    input("\nНажмите Enter для продолжения...")

            except ValueError:
                print("Ошибка: введите корректный номер комнаты")
                input("Нажмите Enter для продолжения...")

        elif choice == '2':
            all_flats = session.query(Zaselenie.flat).distinct().all()
            if all_flats:
                flats_list = [flat[0] for flat in all_flats]
                print(f"\nВсе существующие комнаты: {sorted(flats_list)}")
            else:
                print("\nВ базе данных нет записей о комнатах.")
            input("\nНажмите Enter для продолжения...")

        elif choice == '3':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            input("Нажмите Enter для продолжения...")


def main_menu(session):
    while True:
        print("\n" + "=" * 50)
        print("СИСТЕМА УПРАВЛЕНИЯ ОБЩЕЖИТИЕМ")
        print("=" * 50)
        print("1 - Добавить нового жителя")
        print("2 - Найти жителей по номеру комнаты")
        print("3 - Выйти")

        choice = input("\nВыберите действие (1-3): ").strip()

        if choice == '1':
            add_new_resident(session)
            input("\nНажмите Enter для продолжения...")

        elif choice == '2':
            search_residents_by_flat(session)

        elif choice == '3':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")
            input("Нажмите Enter для продолжения...")


if __name__ == "__main__":
    engine = create_database()
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(Zaselenie).count() == 0:
        test_residents = [
            Zaselenie(
                name="Хивинова Ирина Александровна",
                flat=228,
                passport_num="1234 567891",
                inst="ИРИТ",
                contacts="+79991234567",
                obshaga_num=1,
                narush="Нет нарушений"
            ),
            Zaselenie(
                name="Петров Алексей Владимирович",
                flat=315,
                passport_num="1234 567892",
                inst="ИНЭЛ",
                contacts="+79991234568",
                obshaga_num=2,
                narush="Курение в комнате"
            ),
            Zaselenie(
                name="Сидорова Мария Игоревна",
                flat=228,
                passport_num="1234 567893",
                inst="ИРИТ",
                contacts="+79991234569",
                obshaga_num=1,
                narush="Шум в ночное время"
            ),
            Zaselenie(
                name="Иванов Дмитрий Сергеевич",
                flat=315,
                passport_num="1234 567894",
                inst="ИНЭЛ",
                contacts="+79991234570",
                obshaga_num=2,
                narush="Нет нарушений"
            )
        ]

        for resident in test_residents:
            session.add(resident)
        session.commit()

        test_evictions = [
            Viselenie(id_vis=1, sost="уд", ready=False),
            Viselenie(id_vis=2, sost="неуд", ready=True),
            Viselenie(id_vis=3, sost="уд", ready=False),
            Viselenie(id_vis=4, sost="уд", ready=False)
        ]

        for eviction in test_evictions:
            session.add(eviction)
        session.commit()

    main_menu(session)
    session.close()