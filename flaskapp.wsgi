import sys
import site
#import numpy as np
site.addsitedir('home/ubuntu/envs/DB/lib/python2.7/site-packages')
#np.seterr(all='ignore')


sys.path.insert(0, '/var/www/html/flaskapp')
sys.stdout = sys.stderr
#activate_this = "/home/ubuntu/miniconda2/bin/activate"
#execfile(activate_this, dict(__file__=activate_this))

from flaskapp import app as application

