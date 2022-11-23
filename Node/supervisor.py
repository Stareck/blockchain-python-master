# miner


# coding:utf-8
from block import Block
import time
from data import Vout, Data
from account import get_account
from database import BlockChainDB, DataDB, UnDataDB
from lib.common import unlock_sig, lock_sig

# MAX_COIN = 21000000


# REWARD = 20


# def reward():
#     reward = Vout(get_account()['address'], REWARD)
#     tx = Data([], reward)
#     return tx


# def coinbase():
#     """
#     First block generate.
#     """
#     rw = reward()
#     cb = Block(0, int(time.time()), [rw.hash], "")
#     nouce = cb.pow()
#     cb.make(nouce)
#     # Save block and datas to database.
#     BlockChainDB().insert(cb.to_dict())
#     DataDB().insert(rw.to_dict())
#     return cb


def get_all_undata():
    UnDataDB().all_hashes()


def mine():
    """
    Main miner method.
    """
    # Found last block and unchecked datas.
    last_block = BlockChainDB().last()
    if len(last_block) == 0:
        last_block = coinbase().to_dict()
    untxdb = UnDataDB()
    # Miner reward
    rw = reward()
    untxs = untxdb.find_all()
    untxs.append(rw.to_dict())
    # untxs_dict = [untx.to_dict() for untx in untxs]
    untx_hashes = untxdb.all_hashes()
    # Clear the undata database.
    untxdb.clear()

    # Miner reward is the first data.
    untx_hashes.insert(0, rw.hash)
    cb = Block(last_block['index'] + 1, int(time.time()), untx_hashes, last_block['hash'])
    nouce = cb.pow()
    cb.make(nouce)
    # Save block and data to database.
    BlockChainDB().insert(cb.to_dict())
    DataDB().insert(untxs)
    # Broadcast to other nodes
    Block.spread(cb.to_dict())
    Data.blocked_spread(untxs)
    return cb



class Data():
    def __init__(self, name :str, bid_name :str, Etype=4, msg="Nothing",signature :str = None):
        self.Etype = Etype
        self.timestamp = float(time.time())
        self.hash = self.gen_hash()
        self.msg = msg
        self.bid_name = bid_name
        self.name = name
        self.signature=signature

    def gen_hash(self):
        return hashlib.sha256((str(self.timestamp) + str(self.vin) + str(self.vout)).encode('utf-8')).hexdigest()

    @classmethod
    def transfer(cls, from_addr, to_addr, amount):
        if not isinstance(amount, int):
            amount = int(amount)
        unspents = Vout.get_unspent(from_addr)
        ready_utxo, change = select_outputs_greedy(unspents, amount)
        print('ready_utxo', ready_utxo[0].to_dict())
        vin = ready_utxo
        vout = []
        vout.append(Vout(to_addr, amount))
        vout.append(Vout(from_addr, change))
        tx = cls(vin, vout)
        tx_dict = tx.to_dict()
        UnDataDB().insert(tx_dict)
        return tx_dict

    @staticmethod
    def unblock_spread(undt):
        BroadCast().new_undata(undt)

    @staticmethod
    def blocked_spread(dts):
        BroadCast().blocked_datas(dts)

    def to_dict(self):
        dt = self.__dict__
        if not isinstance(self.vin, list):
            self.vin = [self.vin]
        if not isinstance(self.vout, list):
            self.vout = [self.vout]
        dt['vin'] = [i.__dict__ for i in self.vin]
        dt['vout'] = [i.__dict__ for i in self.vout]
        return dt


def select_outputs_greedy(unspent, min_value):
    if not unspent: return None
    # 分割成两个列表。
    lessers = [utxo for utxo in unspent if utxo.amount < min_value]
    greaters = [utxo for utxo in unspent if utxo.amount >= min_value]
    key_func = lambda utxo: utxo.amount
    greaters.sort(key=key_func)
    if greaters:
        # 非空。寻找最小的greater。
        min_greater = greaters[0]
        change = min_greater.amount - min_value
        return [min_greater], change
    # 没有找到greaters。重新尝试若干更小的。
    # 从大到小排序。我们需要尽可能地使用最小的输入量。
    lessers.sort(key=key_func, reverse=True)
    result = []
    accum = 0
    for utxo in lessers:
        result.append(utxo)
        accum += utxo.amount
        if accum >= min_value:
            change = accum - min_value
            return result, change
            # 没有找到。
    return None, 0
