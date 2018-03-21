# coding: UTF-8
import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse

import requests


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        # ジェネシスブロックを作る
        self.new_block(previous_hash=1, proof=100)

    def register_node(self, address):
        """
        ノードリストに新しいノードを加える
        :param address: <str> ノードのアドレス 例: 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        ブロックチェーンが正しいかを確認する
        :param chain: <list> ブロックチェーン
        :return: <bool> True であれば正しく、 False であればそうではない
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n--------------\n")

            # ブロックのハッシュが正しいかを確認
            if block['previous_hash'] != self.hash(last_block):
                return False

            # プルーフ・オブ・ワークが正しいかを確認
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        これがコンセンサスアルゴリズムだ。ネットワーク上の最も長いチェーンで自らのチェーンを
        置き換えることでコンフリクトを解消する。
        :return: <bool> 自らのチェーンが置き換えられると True 、そうでなれけば False
        """

        neighbours = self.nodes
        new_chain = None

        # 自らのチェーンより長いチェーンを探す必要がある
        max_length = len(self.chain)

        # 他のすべてのノードのチェーンを確認
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # そのチェーンがより長いか、有効かを確認
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # もし自らのチェーンより長く、かつ有効なチェーンを見つけた場合それで置き換える
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        # パクリ検出
        all_data = [transaction['data']
                    for block in self.chain
                    for transaction in block['transactions']]
        current_transactions = []

        for i in range(len(self.current_transactions)):
            if self.current_transactions[i]['data'] not in all_data:
                current_transactions.append(self.current_transactions[i])
        self.current_transactions = current_transactions

        # 新しいブロックを作る
        block = {
            'index': len(self.chain) + 1,
            'timestamp': int(datetime.now().timestamp()),
            'transactions': self.current_transactions,
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
        self.current_transactions.append({
            'user': user,
            'data': data,
            'timestamp': int(datetime.now().timestamp()),
        })
        return self.last_block['index'] + 1

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
