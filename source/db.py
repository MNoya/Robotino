from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from channel_ids import FRASES_EPICAS
from parse_phrases import parse_phrases

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    date = Column(Date)
    channel = Column(String)
    user = Column(String, nullable=True)

    def __str__(self):
        return "{} at {} on {}: {}".format(self.user, self.channel, self.date, self.text)


class DB(object):
    dbname = 'robotino.db'

    def __init__(self):
        self.engine = create_engine('sqlite:///{dbname}'.format(
            dbname=self.dbname
        ), echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print("Created SQL Session to {}".format(self.dbname))

    def setup(self):
        if not self.engine.dialect.has_table(self.engine, Message.__tablename__):
            try:
                Base.metadata.create_all(self.engine)
                print("Tables created succesfully")
            except Exception as e:
                print("Error occurred during Table creation!")
                print(e)
                return

            phrases_list = parse_phrases()
            for phrase_data in phrases_list:
                phrase_data['channel'] = FRASES_EPICAS
                self.save_message(**phrase_data)
            print("Populated Messages with {} phrases".format(len(phrases_list)))
        else:
            print("Database setup finished")

    def save_message(self, **kwargs):
        try:
            message = Message(**kwargs)
            self.session.add(message)
            print("Saved message: {}".format(message))
        except Exception as e:
            print("Error ocurred saving Message!")
            print(e)

    def get_messages(self, channel, text_filter=None):
        messages = self.session.query(Message).filter_by(channel=str(channel))
        if text_filter:
            messages = messages.filter(Message.text.contains(str(text_filter)))
        return messages.all()
