# A few methods to help initiate the database connection
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy import text

engine = create_engine('mysql+mysqlconnector://root:DB123pwd@localhost:3306/project',echo=True)


db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# import all modules so they will be registered properly on the metadata
# this comes right from the flask tutorial page https://flask.palletsprojects.com/en/3.0.x/patterns/sqlalchemy/ 
def init_db():
    import models
    Base.metadata.create_all(bind=engine)