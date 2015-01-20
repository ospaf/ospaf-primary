import sys
import os

__all__=['DMDatabase', 'DMSharedUsers']

dirname=sys.path[0]
for item in __all__:
    sys.path.insert( 0, os.path.join(dirname, item)) 

