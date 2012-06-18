from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///newsdiffer.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Article(Base):
    __tablename__ = 'Articles'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    initial_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)


    def __init__(self, url, initial_date = None, last_update = None):
        self.url = url
        if initial_date == None:
            initial_date = datetime.now()
        self.initial_date = initial_date
        if last_update == None:
            last_update = datetime.min
        self.last_update = last_update

    def update(self):
        self.last_update = datetime.now()

    def minutes_since_update(self):
        delta = datetime.now() - self.last_update
        return delta.seconds // 60 + 24*60*delta.days

    def __repr__(self):
       return "<Article('%s')>" % (self.url)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
