from flask import Flask, request
from dataclasses import dataclass
import json
import atexit


@dataclass
class Peer:
    address: str
    port: int

    def __hash__(self):
        return hash(tuple(f"{self.address}:{self.port}"))


class PeersEncoder(json.JSONEncoder):
    def default(self, obj: set | Peer):
        match obj:
            case set():
                return list(obj)
            case Peer():
                return {
                    "address": obj.address,
                    "port": obj.port
                }
        return json.JSONEncoder.default(self, obj)


app = Flask(__name__)
peers: set[Peer] = set()


def get_node_from_request() -> Peer:
    addr: str = request.args["addr"]
    port: int = int(request.args["port"])
    return Peer(addr, port)


@app.route("/hello")
def hello():
    peers.add(get_node_from_request())
    return "Hello"


@app.route("/bye")
def bye():
    peers.remove(get_node_from_request())
    return "Bye"


@app.route("/nodes")
def get_nodes():
    return json.dumps(peers, cls=PeersEncoder)


def save_nodes():
    with open("nodes.json", "w") as f:
        json.dump(peers, f, cls=PeersEncoder)
    print("nodes information saved successfully")


def load_nodes():
    try:
        with open("nodes.json", "r") as f:
            global peers
            peers = set(json.load(f))
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    atexit.register(save_nodes)
    load_nodes()
    app.run("0.0.0.0", 8000)
