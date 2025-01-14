import time
import random

def rname(): return time.strftime("%Y%m%d-%H%M%S") + "-" + str(random.randint(0, 99))