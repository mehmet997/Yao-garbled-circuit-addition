# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import time

import threading
import os
import floating_point_conversion

from project_source.Alice import Alice
from project_source.Bob import Bob


def calculate_sum(inputs):
    """
    calculates the sum of the inputs
    :param inputs: list of floats
    :return: the sum of the floats
    """
    result = 0
    for single_input in inputs:
        result = result + single_input
    if result > 15.9 or result < 0:
        raise ValueError("sums of inputs of alice and bob each must be 0 <= sum <= 15.9")

    return result


def binary_string_to_integer_list(inputs):
    """
    Converts a binary representation string to list of integers
    :param inputs: string with binary representation. Must contain only integers 0 and 1
    :return: list of integers extracted from the input string
    """
    a_list = [char for char in inputs]
    map_object = map(int, a_list)
    list_of_integers = list(map_object)
    return list_of_integers


def print_alice_to_bob(circuit_path, inputs_a):
    """
    This function prints the necessary output from Alice that she wants to send to Bob. Also prints
    to file circuit_and_garbled_table.txt
    :param circuit_path: the path where the circuit json is saved
    :param inputs_a: Alices inputs, use here the result of alice_mpc_compute()
    :return: returns the alice object (for further usage) and the keys that she generates for each wire for bob
    """
    circuit_path = os.path.dirname(__file__) + "/" + circuit_path
    alice = Alice(inputs_a, circuit_path)
    # alice_thread = threading.Thread(target=alice.send_circuit_and_garbled_table)
    # alice_thread.start()
    alice.send_circuit_and_garbled_table()
    b_keys = alice.send_alice_values()[0]
    return alice, b_keys


def alice_bob_ot(alice, b_keys):
    """
    performs OT between Alice and Bob, Bob's thread should be still running, so only starting alice's ot part here
    this will result in a print of the following 3 files:
    - alice_keys_and_external_values
    - alice_ot
    - bob_ot
    :param alice: The alice object
    :param b_keys: the keys that alice chose for bobs wires
    :return: the result of the mpc between alice and bob (the result that alice gets from bob at the end of mpc)
    """
    result = alice.alice_ot(b_keys)
    return result


def verify_output(inputs_a, inputs_b, mpc_result):
    """
    Verifies the output. Checks the sum of both parties inputs without mpc and compares them to the mpc result
    :param inputs_a: alice's inputs
    :param inputs_b: bobs inputs
    :param mpc_result: the result of the mpc computation
    :return: True if the offline computation results in the same value as mpc_result, False if not.
    """
    result = 0
    for input_a in inputs_a:
        result = result + input_a
    for input_b in inputs_b:
        result = result + input_b

    print("expected result: ", result)
    print("calculated result: ", mpc_result)
    return result == mpc_result


def alice_mpc_compute(alice_inputs):
    """
    Calculates the sum of all alices inputs, this is done before giving her own sum to the mpc
    :param alice_inputs: alices inputs
    :return: sum of alices inputs
    """
    # 1. calculates the sum -> this must be 4 bits result
    inputs_a = calculate_sum(alice_inputs)
    inputs_a = floating_point_conversion.float_normalization(inputs_a)
    inputs_a = binary_string_to_integer_list(inputs_a)
    return inputs_a


def bob_mpc_compute(bob_inputs):
    """
        Calculates the sum of all bobs inputs, this is done before giving his own sum to the mpc
        :param bob_inputs: bobs inputs
        :return: sum of bobs inputs
        """
    return alice_mpc_compute(bob_inputs)


def main(circuit_path, alice_inputs, bob_inputs):
    """
    The Main function. Starts the whole MPC
    :param circuit_path: the part of the circuit (read from command line parameters)
    :param alice_inputs: the inputs of alice (read from command line parameters), sum must be 0 <= sum <= 15.9
    :param bob_inputs: the inputs of bob (read from command line parameters), sum must be 0 <= sum <= 15.9
    """
    # This function should print the output the function that Bob wants to compute on the combined data
    # For example this could be one of the three functions described in the project slide
    print("ALICES INPUTS (HIDDEN FROM BOB): ", alice_inputs)
    print("BOBS INPUTS (HIDDEN FROM ALICE): ", bob_inputs)

    alice_inputs = alice_inputs.split(",")
    alice_inputs = map(float, alice_inputs)
    alice_inputs = list(alice_inputs)

    bob_inputs = bob_inputs.split(",")
    bob_inputs = map(float, bob_inputs)
    bob_inputs = list(bob_inputs)


    inputs_a = alice_mpc_compute(alice_inputs)
    inputs_b = bob_mpc_compute(bob_inputs)
    print("ALICE'S SUM (HIDDEN FROM BOB): ", calculate_sum(alice_inputs))
    print("BOBS SUM (HIDDEN FROM ALICE): ", calculate_sum(bob_inputs))

    bob = Bob(inputs_b)
    bob_thread = threading.Thread(target=bob.listen)
    bob_thread.start()

    print("ALICE'S INPUT TO THE GATES (FLOATING POINT BIT REPRESENTATION OF HER SUM, HIDDEN FROM BOB): ", inputs_a)
    print("BOBS INPUT TO THE GATES (FLOATING POINT BIT REPRESENTATION OF HIS SUM, HIDDEN FROM ALICE): ", inputs_b)
    alice, b_keys = print_alice_to_bob(circuit_path, inputs_a)

    result = alice_bob_ot(alice, b_keys)[0]

    result = result.replace(" ", "")
    print("THE RESULT IN FLOATING POINT BIT REPRESENTATION: ",result)
    result = floating_point_conversion.reverse_float_normalization(result)

    verified = verify_output(alice_inputs, bob_inputs, result)
    if verified:
        print("Found the right solution.")
    else:
        print("Wrong solution.")
    print("---THE END---")


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
            help="the JSON circuit file for alice and local tests",
        )
        parser.add_argument("-a",
                            "--alice_input",
                            metavar="alice_input",
                            default="15",
                            help="The input of Alice (in form [input1, input2, input3, ...]) ")
        parser.add_argument("-b",
                            "--bob_input",
                            metavar="bob_input",
                            default="15.9",
                            help="The input of Bob (in form [input1, input2, input3, ...]) ")

        main(circuit_path=parser.parse_args().circuit,
             alice_inputs=parser.parse_args().alice_input,
             bob_inputs=parser.parse_args().bob_input, )


    init()

