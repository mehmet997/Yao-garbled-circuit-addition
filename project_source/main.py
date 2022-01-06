# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import time


import garbled_circuit_repo.src.util as util
import garbled_circuit_repo.src.ot as ot
from garbled_circuit_repo.src.main import YaoGarbler
import logging
import threading
import os
import floating_point_conversion


def calculate_sum(inputs):
    result = 0
    for input in inputs:
        result = result + input
    if result > 15.9 or result < 0:
        raise ValueError("sums of inputs of alice and bob each must be 0 <= sum <= 15.9")

    return result


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
        N = len(a_wires) + len(b_wires)

        print(f"Received {circuit['id']}")

        """ OWN CHANGES: """
        # Generate all possible inputs for both Alice and Bob
        #for bits in [format(n, 'b').zfill(N) for n in range(2**N)]:
        #    bits_b = [int(b) for b in bits[N - len(b_wires):]]  # Bob's inputs

        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {
            b_wires[i]: self.bits_b[i]
            for i in range(len(b_wires))
        }

        # Evaluate and send result to Alice
        self.ot.send_result(circuit, garbled_tables, pbits_out,
                            b_inputs_clear)

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
            #with open('alice_to_bob.txt', 'r') as f: content = f.read(); dic = eval(content);

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
        #for bits in [format(n, 'b').zfill(N) for n in range(2**N)]:
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
        #str_bits_a = ' '.join(bits_a)
        #str_bits_b = ' '.join(bits[len(a_wires):])
        str_result = ' '.join([str(result[w]) for w in outputs])

        print(f"  Alice{a_wires} = {str_bits_a} "
              #f"Bob{b_wires} = {str_bits_b}  "
              f"Outputs{outputs} = {str_result}")

        return
    def _get_encr_bits(self, pbit, key0, key1):
        return ((key0, 0 ^ pbit), (key1, 1 ^ pbit))


def print_alice_to_bob(circuit_path,inputs_a,inputs_b):
    #  idea from main.py of the used repo:
    bob = Bob(inputs_b)
    bob_thread = threading.Thread(target=bob.listen)
    bob_thread.start()


    time.sleep(1)
    circuit_path = os.path.dirname(__file__)+"/"+circuit_path
    alice = Alice(inputs_a, circuit_path)
    alice_thread = threading.Thread(target=alice.start)
    alice_thread.start()



def alice_bob_OT():
    pass


def bob_mpc_compute(bobs_data_input):
    pass


def alice_mpc_compute(alices_data_input):
    pass


def verfiy_output():
    pass


def main(circuit_path,inputs_a,inputs_b):

    inputs_a = inputs_a.split(",")
    inputs_a = map(float, inputs_a)
    inputs_a = list(inputs_a)
    inputs_b = inputs_b.split(",")
    inputs_b = map(float, inputs_b)
    inputs_b = list(inputs_b)

    result = 0
    for input in inputs_a:
        result = result + input
    for input in inputs_b:
        result = result + input

    #result = format(result, '#06b')
    #result = result[2:]
    #a_list = [char for char in result]
    #map_object = map(int, a_list)
    #list_of_integers = list(map_object)
    print("expected result:", result)
    """ If we need the sum of all inputs of both alice and bob: """
    # 1. alice calculates her sum -> this must be 4 bits result
    inputs_a = calculate_sum(inputs_a)
    # 2. bob calculates his sum -> this must be 4 bits result
    inputs_b = calculate_sum(inputs_b)

    print("A: ",str(inputs_a))
    print("B: ", str(inputs_b))
    inputs_a = floating_point_conversion.float_normalization(inputs_a)
    inputs_b = floating_point_conversion.float_normalization(inputs_b)
    print("A: ", str(inputs_a))
    print("B: ", str(inputs_b))

    inputs_a =  binary_string_to_integer_list(inputs_a)
    inputs_b = binary_string_to_integer_list(inputs_b)

    # Your scipt should at least have the following functions to show the output

    # Assume that two parties involved are Alice and Bob

    # This function should print the necessary output from Alice that she wants to send to Bob.
    # This ouput from Alice should be printed in a file e.g. file_name
    # The output format and how to read it should be described in the report document.
    # E.g. if you want to output in table format then describe how to read and interpret the tables. 
    print_alice_to_bob(circuit_path,inputs_a,inputs_b)
    print("result: ",floating_point_conversion.reverse_float_normalization("01111111001"))

    #
    # Alice and Bob OT
    # This function should print (in a file/console) the OT between Alice and Bob that takes place in Yao's protocol
    #alice_bob_OT()

    # This function should print the output the function that Bob wants to compute on the combined data
    # For example this could be one of the three functions decribed in the project slide
    #bob_mpc_compute(bobs_data_input)

    #alice_mpc_compute(alices_data_input)

    # This function should vefiry whether the output from bob_mpc_compute is same as the ouput
    # from a function which is computed non-multiparty way
    #verfiy_output()


def binary_string_to_integer_list(inputs):
    #result = "{0:b}".format(inputs)
    #result = format(result, '#06b')
    #result = result[2:]
    a_list = [char for char in inputs]
    map_object = map(int, a_list)
    list_of_integers = list(map_object)
    return list_of_integers


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import argparse
    def init():
        parser = argparse.ArgumentParser(description="Run Yao protocol.")
        parser.add_argument(
            "-c",
            "--circuit",
            metavar="circuit.json",
            default="10_bit_adder.json",
            help=("the JSON circuit file for alice and local tests"),
        )
        parser.add_argument("-a",
                            "--alice_input",
                            metavar="alice_input",
                            default="0",
                            help="The input of Alice (in form [input1, input2, input3, ...]) ")
        parser.add_argument("-b",
                            "--bob_input",
                            metavar="bob_input",
                            default="15.9",
                            help="The input of Bob (in form [input1, input2, input3, ...]) ")

        main(circuit_path=parser.parse_args().circuit,
            inputs_a=parser.parse_args().alice_input,
            inputs_b=parser.parse_args().bob_input,)
    init()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
