# coding=utf-8
import threading
from uuid import uuid4
from time import time

from flask import Flask, jsonify, request

# ノードを作る
# Flaskについて詳しくはこちらを読んでほしい http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application
from blockchain import Blockchain

app = Flask(__name__)

# このノードのグローバルにユニークなアドレスを作る
node_identifire = str(uuid4()).replace('-', '')

# ブロックチェーンクラスをインスタンス化する
blockchain = Blockchain()


# メソッドはPOSTで/transactions/newエンドポイントを作る。メソッドはPOSTなのでデータを送信する
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # POSTされたデータに必要なデータがあるかを確認
    required = ['user', 'data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 新しいトランザクションを作る
    index = blockchain.new_transaction(values['user'], values['data'])

    response = {'message': f'トランザクションはブロック {index} に追加されました'}
    return jsonify(response), 201


# メソッドはGETで、フルのブロックチェーンをリターンする/chainエンドポイントを作る
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/users/<user>/transactions', methods=['GET'])
def users_transactions(user):
    transactions = [transaction
                    for block in blockchain.chain
                    for transaction in block['transactions']
                    if transaction['user'] == user]
    response = {
        'transactions': transactions,
        'length': len(transactions)
    }
    return jsonify(response), 200


@app.route('/search/transactions', methods=['GET'])
def search_transactions():
    return str(request.args), 200


class Thread:
    def __init__(self):
        self.timer = time()
        self.stop_event = threading.Event()

        self.thr = threading.Thread(target=self.mine)
        self.thr.start()

    # メソッドはGETで/mineエンドポイントを作る
    # @app.route('/mine', methods=['GET'])
    def mine(self):
        while not self.stop_event.is_set():
            # 次のプルーフを見つけるためプルーフ・オブ・ワークアルゴリズムを使用する
            last_block = blockchain.last_block
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)

            # プルーフを見つけたことに対する報酬を得る
            # 送信者は、採掘者が新しいコインを採掘したことを表すために"0"とする
            blockchain.new_transaction(
                user=node_identifire,
                data="@%s" % (len(blockchain.chain)),
            )

            # チェーンに新しいブロックを加えることで、新しいブロックを採掘する
            blockchain.new_block(proof)

    def stop(self):
        self.stop_event.set()
        self.thr.join()
        print()
        print(time() - self.timer)


# port5000でサーバーを起動する
if __name__ == '__main__':
    thread = Thread()
    app.run(host='0.0.0.0', port=5000, threaded=True)
    thread.stop()
