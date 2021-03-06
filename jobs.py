class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'app_run:d_service',
            'args': '',
            'trigger': 'cron',
            'hour': '7',
            'timezone': 'Asia/Taipei'
        },
        {
            'id': 'job2',
            'func': 'app_run:chase_job',
            'args': '',
            'trigger': 'cron',
            'hour': '*/1',
            'timezone':'Asia/Taipei'
        }
    ]

    SCHEDULER_API_ENABLED = True
