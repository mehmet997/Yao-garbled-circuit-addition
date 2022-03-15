# the code of this file is from https://github.com/ojroques/garbled-circuit
# we modified it to fit our needs for the project



import sys
sys.path.append('../garbled_circuit_repo/src')

try:
    import garbled_circuit_repo.src.util as util
except:
    import util as util

try:
    import garbled_circuit_repo.src.yao as yao
except:
    import yao as yao

from abc import ABC, abstractmethod


class YaoGarbler(ABC):
    """An abstract class for Yao garblers (e.g. Alice)."""

    def __init__(self, circuits):
        circuits = util.parse_json(circuits)
        self.name = circuits["name"]
        self.circuits = []

        for circuit in circuits["circuits"]:
            garbled_circuit = yao.GarbledCircuit(circuit)
            pbits = garbled_circuit.get_pbits()
            entry = {
                "circuit": circuit,
                "garbled_circuit": garbled_circuit,
                "garbled_tables": garbled_circuit.get_garbled_tables(),
                "keys": garbled_circuit.get_keys(),
                "pbits": pbits,
                "pbits_out": {w: pbits[w]
                              for w in circuit["out"]},
            }
            self.circuits.append(entry)


