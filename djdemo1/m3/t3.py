import os,sys
# sys.path.append('..')
sys.path.append(os.path.abspath(os.path.join(os.getcwd())))
from m1 import t1
from m1.m2 import t2
print('t3',os.path.abspath(os.path.join(os.getcwd())))
# Create your tests here.
