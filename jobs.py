class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'app_run:notice',
            'args': '',
            'trigger': 'cron',
            'start_date': '2013-02-13 00:00',
            'hour': '7'
        }
    ]

    SCHEDULER_API_ENABLED = True
