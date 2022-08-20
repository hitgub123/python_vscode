from django.test import TestCase
import os,sys
# sys.path.append('..')
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))
from m1 import t1
from m3 import t3


print('t2',os.path.abspath(os.path.join(os.getcwd())))
# Create your tests here.
