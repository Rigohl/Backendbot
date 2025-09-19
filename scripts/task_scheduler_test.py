from backendbot.core.task_scheduler import TaskScheduler
import time

s = TaskScheduler()

def hello():
    print('hello called')

try:
    tid = s.add_task_compat('test', hello, 'once')
    print('created task id:', tid)
    s.execute_task(tid)
    print('executed task')
except Exception as e:
    print('ERROR', e)
