from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import sessionmaker

for line in open('/mit/ecprice/.my.cnf').read().split():
    if line.startswith('password='):
        pwd = line.split('=')[1]
engine = create_engine('mysql://ecprice:%s@sql.mit.edu/ecprice+newsdiffs'%pwd, echo=False)
#engine = create_engine('sqlite:///newsdiffer.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


ancient = datetime(1901, 1, 1)

class Article(Base):
    __tablename__ = 'Articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), unique=True)
    initial_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
    last_check = Column(DateTime, nullable=False)


    def __init__(self, url, initial_date = None):
        self.url = url
        if initial_date == None:
            initial_date = datetime.now()
        self.initial_date = initial_date
        self.last_update = datetime.now()
        self.last_check = ancient

    def minutes_since_update(self):
        delta = datetime.now() - self.last_update
        return delta.seconds // 60 + 24*60*delta.days

    def minutes_since_check(self):
        delta = datetime.now() - self.last_check
        return delta.seconds // 60 + 24*60*delta.days

    def __repr__(self):
       return "<Article('%s')>" % (self.url)

if __name__ == '__main__':
    import sys
    import subprocess

    if '-s' in sys.argv:
        Base.metadata.create_all(engine)

    if '--canonicalize' in sys.argv:
        def canonicalize_url(url):
            url = url.strip()+'?'
            return url[:url.find('?')]
        session = Session()
        for article_row in session.query(Article).all():
            newurl = canonicalize_url(article_row.url)
            if session.query(Article).filter_by(url=newurl).first() is None:
                article_row.url = newurl
            else:
                session.delete(article_row)
        session.commit()

    if '-r' in sys.argv:
        #reload from git
        session = Session()
        file_list = subprocess.check_output(['/usr/bin/git', 'ls-files'], cwd='articles')
        for fname in file_list.split():
            url = 'http://'+fname
            art = Article(url)
            session.add(art)
            if '--reformat' in sys.argv:
                txt = open('articles/'+fname).read()
                open('articles/'+fname, 'w').write(txt.strip()+'\n')
        session.commit()
