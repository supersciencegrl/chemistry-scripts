import datetime
import os
from pathlib import Path
import random
import sys

def random_time(start, time_period):
    """
    Generate a random time offset from the current time.

    Args:
        time_period (int): The maximum time period in an integer of minutes. 

    Returns:
        datetime.datetime: A random datetime object.

    """

    time_period = int(time_period)
    offset = random.randint(1, time_period)
    result = start + datetime.timedelta(minutes = offset)

    return result

chime_bell = Path(Path.cwd(), 'chime-bell-29645.mp3')
default_time_period = 20 # minutes

if __name__ == '__main__':
    try:
        time_period = sys.argv[1]
    except IndexError:
        time_period = default_time_period
    except ValueError:
        print(f'{sys.argv[1]} cannot be converted to an integer value of minutes.')
        time_period = default_time_period
    
    print(f'Your alarm will ring within {time_period} minutes.')
    script_start = datetime.datetime.now()
    alarm_time = random_time(script_start, time_period)

    while datetime.datetime.now() < alarm_time:
        pass
    else:
        os.startfile(chime_bell)
