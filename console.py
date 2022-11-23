# coding:utf-8
from Data_type import AData
from account import *
from rpc import get_clients, broadCast, start_server
from data import *
from database import *
from block import *
from PoA import *
import sys
import multiprocessing
import rpc
from node import *
from lib.common import cprint
import inspect

MODULES = ['account','tx','blockchain','miner','node']

def upper_first(string):
    return string[0].upper()+string[1:]



class node():

    def add(self, args,a):
        add_node(args[0],a)
        rpc.broadCast().add_node(args[0],a)
        cprint('Allnode', get_nodes())

    def run(self, args):
        start_node(args[0])

    def list(self, args):
        for t in NodeDB().find_all():
            cprint('Node', t)

class miner():
    def start(self, args):
        if get_account() == None:
            cprint('ERROR','Please create account before start miner.')
            exit()
        start_node(PoA())
        while True :
            cprint('Miner new block',mine().to_dict())

class Account():
    def create(self, nodetype = 2):

        if(nodetype == 0):
            ac = S_account()
        elif(nodetype == 1):
            ac = T_account()
        else:
            ac = B_account()
        cprint('Private Key',ac[0])
        cprint('Public Key',ac[1])
        cprint('Address',ac[2])

    def get(self, args):
        cprint('All Account',AccountDB().read())

    def current(self, args):
        cprint('Current Account', get_account())

class Blockchain():

    def list(self, args):
        for t in BlockChainDB().find_all():
            cprint('Blockchain',str(t))

class Tx():

    def list(self, args):
        for t in DataDB().find_all():
            cprint('Data',t)


    def publish(self,args):
        dt = AData.publish(args[0],args[1],args[2],args[3])
        print(AData.unblock_spread(dt))
        cprint('Data publish',dt)

def usage(class_name):
    module = globals()[upper_first(class_name)]
    print('  ' + class_name + '\r')
    print('    [action]\r')
    for k,v in module.__dict__.items():
        if callable(v):
            print('      %s' % (k,))
    print('\r')

def help():
    print("Usage: python console.py [module] [action]\r")
    print('[module]\n')
    for m in MODULES:
        usage(m)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        help()
        exit()
    module = sys.argv[1]
    if module == 'help':
        help()
        exit()
    if module not in MODULES:
        cprint('Error', 'First arg shoud in %s' % (str(MODULES,)))
        exit()
    mob = globals()[upper_first(module)]()
    method = sys.argv[2]
    # try:
    getattr(mob, method)(sys.argv[3:])
    # except Exception as e:
    #     cprint('ERROR','/(ㄒoㄒ)/~~, Maybe command params get wrong, please check and try again.')