from sqlalchemy import Table
association_table = Table('post_tag', Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')))

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    tags = relationship("Tag", secondary=association_table, backref="posts")

class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))


with DBSession() as session:
    t1 = Tag(name="Python")
    t2 = Tag(name="SQLAlchemy")
    t3 = Tag(name="PyMySQL")
    p1 = Post(title="使用Python连接MySQL")
    p1.tags = [t1, t3]
    p2 = Post(title="Python Orm")
    p2.tags = [t1, t2]
    session.add_all([p1, p2])
    session.commit()


with DBSession() as session:
    post = session.execute(select(Post).where(Post.title=="Python Orm")).first()
    post_tags = post[0].tags
    [print(i.name) for i in post_tags]
