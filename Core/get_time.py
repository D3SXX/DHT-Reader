from datetime import datetime
import time

def date():
     # Check what is the time right now
    now = datetime.now()
    # Format it for better readability
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    return date_time

def time_s():
     return time.time()