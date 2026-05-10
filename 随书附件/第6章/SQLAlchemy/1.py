from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, String, Integer

Base = declarative_base()
engine = create_engine("postgresql+psycopg2://gres:pw@localhost:5432/postgres", echo=True, future=True)

class Users(Base):
    __tablename__ = 'users'
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(20))
    year = Column("year", Integer)

Base.metadata.create_all(engine)

from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker(engine)
with DBSession() as session:
    u1 = Users(name="张三", year=36)
    u2 = Users(name="李四", year=32)
    u3 = Users(name="王五", year=31)
    session.add_all([u1,u2,u3])
    session.commit()


from sqlalchemy import select, or_
with DBSession() as session:
    result_1 = session.execute(select(Users).
r_by(Users.year)).first()
    result_2 = session.execute(select(Users).where(Users.year > 31, Users.name != "张三")).all()
    result_3 = session.execute(select(Users).where(Users.year > 31).order_by(Users.year)).all()
    result_4 = session.execute(select(Users).
e(or_(Users.name.like("%三"), Users.name.in_(["李四"])))).all()
def handle_result(result, ident):
    [print(f"[{ident}] name:{i[0].name}, year:{i[0].year}") for i in result]
handle_result([result_1], 1)
handle_result(result_2, 2)
handle_result(result_3, 3)
handle_result(result_4, 4)
