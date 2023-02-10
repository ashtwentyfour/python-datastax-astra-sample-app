"""
Create Cassandra Tables
"""

from cassandra import AlreadyExists
from cassandra import DriverException
from cassandra import RequestExecutionException
from cassandra.query import SimpleStatement
from utils.logger import get_logger

logger = get_logger('default')

def create_tables(session):
    """Create activity, sleep and weightloss data tables"""
    query_table_1 = SimpleStatement(
                "CREATE TABLE activity ( \
                    id uuid, \
                    date date, \
                    totalsteps int, \
                    totaldistance double, \
                    calories int, \
                    sedentaryminutes int, \
                    veryactiveminutes int, \
                    fairlyactiveminutes int, \
                    lightlyactiveminutes int, \
                    PRIMARY KEY (id, date) \
                ) WITH COMMENT = 'A table with daily activity results' \
                  AND CLUSTERING ORDER BY (date DESC) \
                "
            )
    try:
        session.execute(query_table_1)
        logger.info('created table "activity"')
    except AlreadyExists as err:
        logger.debug(err)
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)

    query_table_2 = SimpleStatement(
                "CREATE TABLE sleep ( \
                    id uuid, \
                    date date, \
                    sleeptime timestamp, \
                    sleepminutes int, \
                    bedminutes int, \
                    sleeprecords int, \
                    PRIMARY KEY (id, date) \
                ) WITH COMMENT = 'A table with daily sleep results' \
                  AND CLUSTERING ORDER BY (date DESC) \
                "
            )
    try:
        session.execute(query_table_2)
        logger.info('created table "sleep"')
    except AlreadyExists as err:
        logger.debug(err)
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)

    query_table_3 = SimpleStatement(
                "CREATE TABLE weightloss ( \
                    id uuid, \
                    date date, \
                    weightkgs double, \
                    fat int, \
                    BMI double, \
                    PRIMARY KEY (id, date) \
                ) WITH COMMENT = 'A table with daily weight figures' \
                  AND CLUSTERING ORDER BY (date DESC) \
                "
            )
    try:
        session.execute(query_table_3)
        logger.info('created table "weightloss"')
    except AlreadyExists as err:
        logger.debug(err)
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)
