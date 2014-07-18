from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
)
from flask.ext.script import Manager
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy

db_manager = Manager()
db = SQLAlchemy()


class Tender(db.Model):
    __tablename__ = 'tender'

    id = Column(Integer, primary_key=True)
    reference = Column(String(255), unique=True)
    title = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    published = Column(Date)
    deadline = Column(DateTime, nullable=True)
    description = Column(Text(5095), nullable=True)

    documents = relationship("TenderDocument", backref="tender")
    winner = relationship("Winner", backref="tender")

    def __unicode__(self):
        return 'Tender notice: %s' % self.title


class TenderDocument(db.Model):
    __tablename__ = 'tender_document'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    download_url = Column(String(255))

    tender_id = Column(ForeignKey('tender.id'), nullable=True)


class Winner(db.Model):
    __tablename__ = 'winner'

    id = Column(Integer, primary_key=True)
    vendor = Column(String(255), nullable=True)
    value = Column(Float, nullable=True)
    award_date = Column(DateTime)

    tender_id = Column(ForeignKey('tender.id'), nullable=True)

    def __unicode__(self):
        return '%s WON BY %s' % (self.title, self.vendor)


@db_manager.command
def init():
    db.create_all()
