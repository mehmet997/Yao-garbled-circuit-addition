# Yao-garbled-circuit-addition

This repository is created for the Course Introduction to Cybersecurity at Alpen Adria Universität 

It uses the https://github.com/ojroques/garbled-circuit Repository as base


The overall task is to implement Yao’s Protocol for two parties who both hold an input set filled with numbers and want to compute the sum on both inputs without revealing their inputs to the other party.

The requirement is that the resulting implementation should be able to handle integers with 4 bits. Additionally, the implementation must allow decimal inputs with at least one digit before and after the decimal point.



Restriction: The input sets of the two parties (in the following, we will call them Alice and Bob) each must sum up to a maximum of 15.9. Therefore, the result of the multi-party-computation function on the two input sets has the maximum of 31.8.


# Dependencies: 
- ZeroMQ
- FernNet
- SymPy


# Running

The main script is to be called from ”course project/project source/” as follows:

    ./main.py -a [ALICE_INPUTS] -b [BOB_INPUTS]
    
For example:

    ./main.py -a 0.8,2.1,3.0,4.0,5.0 -b 1,2,3,4
    
Please note that the sums of the input sets have to be in the range of 0 and 15.9

# Communication
In this project, the communicating parties run in two seperate threads and send communication over the network. The communication is logged in txt-files:

- circuit_and_garbled_table_and_p_z.txt: Contains the circuit, the garbled table and
the signal bits 
- alice_keys_and_external_values.txt: contains Alice’s encrypted key and external val-
ues for the circuit. 
- alice_ot.txt: contains Alice’s values used for the oblivious transfer
-bob_ot.txt: contains Bobs values used for the oblivious transfer

The following diagram shows how the communication is working: 


<img width="534" alt="Screenshot 2022-06-22 at 09 29 11" src="https://user-images.githubusercontent.com/63359071/174971235-c8753494-d941-4989-9f06-c84eac60c0c7.png">

