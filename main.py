from flask import Flask, request
from dataclasses import dataclass
import json


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


app.run("0.0.0.0", 8000)
