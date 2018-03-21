# coding=utf-8
import threading
from uuid import uuid4

from flask import Flask, jsonify, request

# ノードを作る
# Flaskについて詳しくはこちらを読んでほしい http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application
from blockchain import Blockchain

app = Flask(__name__)

# このノードのグローバルにユニークなアドレスを作る
node_identifire = str(uuid4()).replace('-', '')

# ブロックチェーンクラスをインスタンス化する
blockchain = Blockchain()


# メソッドはGETで/mineエンドポイントを作る
@app.route('/mine', methods=['GET'])
def mine():
    while True:
        # 次のプルーフを見つけるためプルーフ・オブ・ワークアルゴリズムを使用する
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        # プルーフを見つけたことに対する報酬を得る
        # 送信者は、採掘者が新しいコインを採掘したことを表すために"0"とする
        blockchain.new_transaction(
            user=node_identifire,
            data="",
        )

        # チェーンに新しいブロックを加えることで、新しいブロックを採掘する
        blockchain.new_block(proof)


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


@app.route('/users/<user>/transactions')
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


# port5000でサーバーを起動する
if __name__ == '__main__':
    thr = threading.Thread(target=mine)
    thr.start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
    thr.join()