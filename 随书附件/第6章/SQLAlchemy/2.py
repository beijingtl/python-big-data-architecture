from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
class Company(Base):
    __tablename__ = 'company'
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(20))
    staff = relationship("Staff", backref="company")

class Staff(Base):
    __tablename__ = 'staff'
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(20))
    compandy_id = Column(Integer, ForeignKey('company.id'), nullable=False)


with DBSession() as session:
    c1 = Company(name="Go")
    c2 = Company(name="Az")
    c3 = Company(name="Fb")
    s1 = Staff(name="张三", company=c1)
    s2 = Staff(name="李四", company=c1)
    s3 = Staff(name="王五", company=c2)
    session.add_all([s1,s2,s3,c3])
    session.commit()
