# coding: UTF-8
import hashlib
import json
from datetime import datetime


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.next_transaction_id = 0
        # ジェネシスブロックを作る
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        # パクリ検出
        all_data = [transaction['data']
                    for block in self.chain
                    for transaction in block['transactions']]
                    
        current_transactions = []
        for transaction in self.current_transactions:
            if transaction not in current_transactions:
                current_transactions.append(transaction)

        current_transactions = [transaction
                                for transaction in current_transactions
                                if transaction['data'] not in all_data]

        # 新しいブロックを作る
        block = {
            'index': len(self.chain) + 1,
            'timestamp': int(datetime.now().timestamp()),
            'transactions': current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # 現在のトランザクションリストをリセット
        self.current_transactions = []
        # チェーンに追加
        self.chain.append(block)
        return block

    def new_transaction(self, user, data):
        # 新しいトランザクションをリストに加えた後，
        # そのトランザクションが加えられるブロック(次に採掘されるブロック)のインデックスを返す．
        transaction = {
            'id': self.next_transaction_id,
            'user': user,
            'data': data,
            'timestamp': int(datetime.now().timestamp()),
        }
        self.current_transactions.append(transaction)
        self.next_transaction_id += 1
        return transaction

    @staticmethod
    def hash(block):
        # ブロックをハッシュ化する
        # 必ずディクショナリ（辞書型のオブジェクト）がソートされている必要がある。そうでないと、一貫性のないハッシュとなってしまう
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # チェーンの最後のブロックをリターンする
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        シンプルなプルーフ・オブ・ワークのアルゴリズム:
         - hash(pp') の最初の4つが0となるような p' を探す
         - p は1つ前のブロックのプルーフ、 p' は新しいブロックのプルーフ
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        プルーフが正しいかを確認する: hash(last_proof, proof)の最初の4つが0となっているか？
        :param last_proof: <int> 前のプルーフ
        :param proof: <int> 現在のプルーフ
        :return: <bool> 正しければ true 、そうでなれけば false
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        n = 5 #難易度調整

        return guess_hash[:n] == "0" * n
