# the code of this file is from https://github.com/ojroques/garbled-circuit
# we modified it to fit our needs for the project
import garbled_circuit_repo.src.util as util
import project_source.ot as ot
import logging
from YaoGarbler import YaoGarbler


class Alice(YaoGarbler):
    """Alice is the creator of the Yao circuit.

    Alice creates a Yao circuit and sends it to the evaluator along with her
    encrypted inputs. Alice will finally print the truth table of the circuit
    for all combination of Alice-Bob inputs.

    Alice does not know Bob's inputs but for the purpose
    of printing the truth table only, Alice assumes that Bob's inputs follow
    a specific order.

    Attributes:
        circuits: the JSON file containing circuits
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """

    def __init__(self, inputs, circuits, oblivious_transfer=True):
        super().__init__(circuits)
        self.bits_a = inputs
        self.socket = util.GarblerSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)

    def start(self):
        """Start Yao protocol."""
        for circuit in self.circuits:
            to_send = {
                "circuit": circuit["circuit"],
                "garbled_tables": circuit["garbled_tables"],
                "pbits_out": circuit["pbits_out"],
            }
            logging.debug(f"Sending {circuit['circuit']['id']}")

            """ OWN CHANGES: """
            with open('alice_to_bob.txt', 'a') as file:
                print(to_send, file=file)
            # reading it back in:
            # with open('alice_to_bob.txt', 'r') as f: content = f.read(); dic = eval(content);

            self.socket.send_wait(to_send)
            # print the to_send to a file

            self.print(circuit)
            self.socket.send("TERMINATE")
            return

    def print(self, entry):
        """Print circuit evaluation for all Bob and Alice inputs.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_keys = {  # map from Bob's wires to a pair (key, encr_bit)
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items() if w in b_wires
        }

        N = len(a_wires) + len(b_wires)

        print(f"======== {circuit['id']} ========")

        """OWN CHANGES: only one input from alice:"""

        # Generate all inputs for both Alice and Bob
        # for bits in [format(n, 'b').zfill(N) for n in range(2**N)]:
        #    bits_a = [int(b) for b in bits[:len(a_wires)]]  # Alice's inputs

        # Map Alice's wires to (key, encr_bit)
        for i in range(len(a_wires)):
            a_inputs[a_wires[i]] = (keys[a_wires[i]][self.bits_a[i]],
                                    pbits[a_wires[i]] ^ self.bits_a[i])

        # Send Alice's encrypted inputs and keys to Bob
        result = self.ot.get_result(a_inputs, b_keys)

        # Format output
        string_ints = [str(int) for int in self.bits_a]
        str_bits_a = "".join(string_ints)
        # str_bits_a = ' '.join(bits_a)
        # str_bits_b = ' '.join(bits[len(a_wires):])
        str_result = ' '.join([str(result[w]) for w in outputs])

        print(f"  Alice{a_wires} = {str_bits_a} "
              # f"Bob{b_wires} = {str_bits_b}  "
              f"Outputs{outputs} = {str_result}")

        return

    def _get_encr_bits(self, pbit, key0, key1):
        return ((key0, 0 ^ pbit), (key1, 1 ^ pbit))
