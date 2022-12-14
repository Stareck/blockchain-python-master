# miner


# coding:utf-8
from block import Block
import time
from data import Data
from account import get_account
from database import BlockChainDB, DataDB, UnDataDB
from lib.common import cprint
from Node import Node
from account import *
from CA_Sig.G_key import *


def coinbase():
    """
    First block generate.
    """
    rw = ''
    cb = Block(0, int(time.time()), '', "First block generate", 4)

    # Save block and datas to database.
    BlockChainDB().insert(cb.to_dict())
    DataDB().insert(rw)
    return cb


class supervisor(Node):
    def __int__(self, public_key: str = None, private_key: str = None, Etype: int = 1, address: str = None):
        self.public_key = public_key
        self.private_key = private_key
        self.address = address
        self.Etype = Etype

    # 1=supervisor 2=tenderUser 3=biddingUser
    def create_account(self, E: int):
        if E == 1:
            S_account()
        elif E == 2:
            T_account()
        elif E == 3:
            B_account()
        else:
            Exception("Error input")

    # 第一个s结点调用此函数
    def begin(self):
        G_K(self)

    def start(self, args):
        if get_account() == None:
            cprint('ERROR', 'Please create account before start miner.')
            exit()
        self.start_node(args[0])
        while True:
            cprint('Miner new block', self.to_dict())

    def get_all_undata(self):
        UnDataDB().all_hashes()

    def valid(self):
        pass

    def get_tx(self):
        pass

    def get_block(self):
        pass

    def get_blockchain(self):
        pass

    # 没写完，要选择4种类型其中一种
    def new_data(self):
        data = Data()
        return data

    def mine(self):
        """
        Main miner method.
        """
        # Found last block and unchecked datas.
        last_block = BlockChainDB().last()
        if len(last_block) == 0:
            last_block = coinbase().to_dict()
        untxdb = UnDataDB()
        # Miner reward
        untxs = untxdb.find_all()
        new_data = self.new_data()
        untxs.append(new_data.to_dict())
        # untxs_dict = [untx.to_dict() for untx in untxs]
        untx_hashes = untxdb.all_hashes()
        # Clear the undata database.
        untxdb.clear()
        cb = Block(last_block['index'] + 1, int(time.time()), untx_hashes, last_block['hash'])
        # Save block and data to database.
        BlockChainDB().insert(cb.to_dict())
        DataDB().insert(untxs)
        # Broadcast to other nodes
        Block.spread(cb.to_dict())
        Data.blocked_spread(untxs)
        return cb






