# the code of this file is from https://github.com/ojroques/garbled-circuit
# we modified it to fit our needs for the project
import garbled_circuit_repo.src.util as util
import project_source.ot as ot
import logging


class Bob:
    """Bob is the receiver and evaluator of the Yao circuit.

    Bob receives the Yao circuit from Alice, computes the results and sends
    them back.

    Args:
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """

    def __init__(self, inputs, oblivious_transfer=True):
        self.socket = util.EvaluatorSocket()
        self.bits_b = inputs
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)

    def listen(self):
        """Start listening for Alice messages."""
        logging.info("Start listening")
        while True:
            try:
                entry = self.socket.receive()
                if entry == "TERMINATE":
                    break
                self.socket.send(True)
                self.send_evaluation(entry)
            except KeyboardInterrupt:
                logging.info("Stop listening")
                break


    def send_evaluation(self, entry):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        a_wires = circuit.get("alice", [])  # list of Alice's wires
        b_wires = circuit.get("bob", [])  # list of Bob's wires

        print(f"Received {circuit['id']}")

        """ OWN CHANGES: """
        # Generate all possible inputs for both Alice and Bob
        # for bits in [format(n, 'b').zfill(N) for n in range(2**N)]:
        #    bits_b = [int(b) for b in bits[N - len(b_wires):]]  # Bob's inputs

        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {
            b_wires[i]: self.bits_b[i]
            for i in range(len(b_wires))
        }

        # Evaluate and send result to Alice
        self.ot.send_result(circuit, garbled_tables, pbits_out,
                            b_inputs_clear)
