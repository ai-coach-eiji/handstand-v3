from .production import *

try:
    from .local import *
    print("local mode")
except:
    print("production mode")
    pass
    