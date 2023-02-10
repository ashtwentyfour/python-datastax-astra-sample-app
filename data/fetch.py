"""
Retrieve Fitness Tracker Data
"""

import uuid

from cassandra.query import named_tuple_factory

def get_activity(session, uid, tracker):
    """Fetch fitness data by tracker category - last 21 days"""
    days = {'id': uid, 'days': []}
    session.row_factory = named_tuple_factory
    query = "SELECT * FROM {} where id=%s LIMIT 21".format(tracker)
    rows = session.execute(query, parameters=[uuid.UUID(uid)])
    if not rows:
        return days
    for row in rows:
        _row = row
        date_str = str(_row.date)
        _row = _row._replace(date = date_str)
        _row = _row._replace(id = uid)
        day = _row._asdict()
        del day['id']
        days['days'].append(day)
    return days
