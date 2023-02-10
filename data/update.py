"""
Add/Update User Fitness Data
"""

import uuid

from cassandra import DriverException
from cassandra import RequestExecutionException
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
from utils.logger import get_logger

logger = get_logger('default')

def add_activity_data(session, record):
    """Add activity data"""
    query = SimpleStatement(
        "INSERT into activity (id, date, totalsteps, calories, totaldistance, \
        sedentaryminutes, veryactiveminutes, fairlyactiveminutes, lightlyactiveminutes) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", consistency_level=ConsistencyLevel.QUORUM
    )
    try:
        session.execute(query, (uuid.UUID(record['id']), \
                                    record['date'], \
                                    record['totalsteps'], \
                                    record['calories'], \
                                    record['totaldistance'], \
                                    record['sedentaryminutes'], \
                                    record['veryactiveminutes'], \
                                    record['fairlyactiveminutes'], \
                                    record['lightlyactiveminutes']))
        return 1
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)
        return -1
    except KeyError as err:
        logger.error(err)
        return -1

def add_sleep_data(session, record):
    """Add sleep data"""
    query = SimpleStatement(
        "INSERT into sleep (id, date, sleeptime, sleepminutes, \
        bedminutes, sleeprecords) VALUES (%s, %s, %s, %s, %s, %s)", \
        consistency_level=ConsistencyLevel.QUORUM
    )
    try:
        session.execute(query, (uuid.UUID(record['id']), \
                                    record['date'], \
                                    record['sleeptime'], \
                                    record['sleepminutes'], \
                                    record['bedminutes'], \
                                    record['sleeprecords']))

        return 1
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)
        return -1
    except KeyError as err:
        logger.error(err)
        return -1

def add_weightloss_data(session, record):
    """Add weight data"""
    query = SimpleStatement(
        "INSERT into weightloss (id, date, weightkgs, fat, BMI) VALUES (%s, %s, %s, %s, %s)", \
        consistency_level=ConsistencyLevel.QUORUM
    )
    try:
        session.execute(query, (uuid.UUID(record['id']), \
                                    record['date'], \
                                    record['weightkgs'], \
                                    record['fat'], \
                                    record['BMI']))

        return 1
    except (DriverException, RequestExecutionException) as err:
        logger.error(err)
        return -1
    except KeyError as err:
        logger.error(err)
        return -1
    