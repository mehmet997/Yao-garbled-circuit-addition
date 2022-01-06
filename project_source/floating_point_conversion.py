# THE CONTENT OF THIS FILE IS FROM THE FOLLOWING SOURCE:
# https://www.geeksforgeeks.org/convert-decimal-fraction-binary-number/
# Python3 program to convert fractional
# decimal to binary number

# Function to convert decimal to binary
# upto k-precision after decimal point
def decimalToBinary(num, k_prec):
    binary = ""

    # Fetch the integral part of
    # decimal number
    Integral = int(num)

    # Fetch the fractional part
    # decimal number
    fractional = num - Integral

    # Conversion of integral part to
    # binary equivalent
    while (Integral):
        rem = Integral % 2

        # Append 0 in binary
        binary += str(rem);

        Integral //= 2

    # Reverse string to get original
    # binary equivalent
    binary = binary[:: -1]

    # Append point before conversion
    # of fractional part
    binary += '.'

    # Conversion of fractional part
    # to binary equivalent
    while (k_prec):

        # Find next bit in fraction
        fractional *= 2
        fract_bit = int(fractional)

        if (fract_bit == 1):

            fractional -= fract_bit
            binary += '1'

        else:
            binary += '0'

        k_prec -= 1

    return binary


# Python3 program to demonstrate above steps
# of binary fractional to decimal conversion

# Function to convert binary fractional
# to decimal
def binaryToDecimal(binary, length):
    # Fetch the radix point
    point = binary.find('.')

    # Update point if not found
    if (point == -1):
        point = length

    intDecimal = 0
    fracDecimal = 0
    twos = 1

    # Convert integral part of binary
    # to decimal equivalent
    for i in range(point - 1, -1, -1):
        # Subtract '0' to convert
        # character into integer
        intDecimal += ((ord(binary[i]) -
                        ord('0')) * twos)
        twos *= 2

    # Convert fractional part of binary
    # to decimal equivalent
    twos = 2

    for i in range(point + 1, length):
        fracDecimal += ((ord(binary[i]) -
                         ord('0')) / twos);
        twos *= 2.0

    # Add both integral and fractional part
    ans = intDecimal + fracDecimal

    return ans


# Driver code :
if __name__ == "__main__":
    n = "110.101"
    print(binaryToDecimal(n, len(n)))

    n = "101.1101"
    print(binaryToDecimal(n, len(n)))


# This code is contributed
# by aishwarya.27




# from here: own code

def float_normalization(n):
    """
    Normalizes the floating point number to 4bits.6bits and cuts the digits before the dot.
    only use this with numbers 0.0 <= 9.9 and only one digit before and after the dot.
    :param n: the number to normalize
    :return: the normalized number
    """
    float_nr = decimalToBinary(n, 6)
    # we want to consider only the digits after the point, so we have to shift the point by 4 digits
    # the largest exponent is 2^4
    # exponent is always 11
    # (2^n-1)-1 = (2^4-1)-1 = 7
    # 7+4 = 11 (dec) = 1011 (bin)
    # -> values have to be shifted by 4 digits
    index = float_nr.find(".")
    if index < 4:
        # fill with 0's
        float_nr = float_nr.zfill(11)
    # shift 4 bits to left and cut after the . is the same as just removing the dot
    result = float_nr.replace('.', '')
    return result

def reverse_float_normalization(n):
    # the result of the addition has one bit more than the inputs, so we have exponent 2^5 now
    # --> shift by 5 digits to convert back
    #print(n)
    n = n[:5] + '.' + n[5:]
    #print(n)
    n = binaryToDecimal(n, len(n))
    n = round(n,1)
    return n

# for testing the methods here
n = 9
print(str(n))
result = float_normalization(n)
print("as bit representation (without dot) : " + result)

result = result.zfill(11)

reversed_result = reverse_float_normalization(result)


print("adding the dot on the right place again: " + str(reversed_result))

