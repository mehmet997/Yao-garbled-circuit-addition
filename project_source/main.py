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
    result = 0
    for input in inputs:
        result = result + input
    if result > 15.9 or result < 0:
        raise ValueError("sums of inputs of alice and bob each must be 0 <= sum <= 15.9")

    return result

def binary_string_to_integer_list(inputs):
    #result = "{0:b}".format(inputs)
    #result = format(result, '#06b')
    #result = result[2:]
    a_list = [char for char in inputs]
    map_object = map(int, a_list)
    list_of_integers = list(map_object)
    return list_of_integers

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

def verify_output(inputs_a,inputs_b, mpc_result):
    result = 0
    for input_a in inputs_a:
        result = result + input_a
    for input_b in inputs_b:
        result = result + input_b

    print("expected result: ", result)
    print("calculated result: ",mpc_result)
    return result == mpc_result


def preprocess_inputs(alice_inputs, bob_inputs):
    # 1. alice calculates her sum -> this must be 4 bits result
    inputs_a = calculate_sum(alice_inputs)
    # 2. bob calculates his sum -> this must be 4 bits result
    inputs_b = calculate_sum(bob_inputs)
    print("A: ", str(inputs_a))
    print("B: ", str(inputs_b))
    inputs_a = floating_point_conversion.float_normalization(inputs_a)
    inputs_b = floating_point_conversion.float_normalization(inputs_b)
    print("A: ", str(inputs_a))
    print("B: ", str(inputs_b))
    inputs_a = binary_string_to_integer_list(inputs_a)
    inputs_b = binary_string_to_integer_list(inputs_b)
    return inputs_a, inputs_b

def main(circuit_path,alice_inputs,bob_inputs):

    alice_inputs = alice_inputs.split(",")
    alice_inputs = map(float, alice_inputs)
    alice_inputs = list(alice_inputs)

    bob_inputs = bob_inputs.split(",")
    bob_inputs = map(float, bob_inputs)
    bob_inputs = list(bob_inputs)

    inputs_a, inputs_b = preprocess_inputs(alice_inputs, bob_inputs)

    # Your script should at least have the following functions to show the output

    # Assume that two parties involved are Alice and Bob

    # This function should print the necessary output from Alice that she wants to send to Bob.
    # This output from Alice should be printed in a file e.g. file_name
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
            alice_inputs=parser.parse_args().alice_input,
            bob_inputs=parser.parse_args().bob_input,)
    init()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
