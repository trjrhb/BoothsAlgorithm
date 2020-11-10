'''
This is a project for CompE 3108: Computer Organization and Design
'''

ZERO = '0'
ONE = '1'
iterations = 0
num_additions = 0

# Inverts each bit in the binary value
def ones_complement(binary):
    complement = []
    for index in range(len(binary)):
        if binary[index] == ZERO:
            complement.append(ONE)
        else:
            complement.append(ZERO)
    return complement

# Peforms 1's complement on a binary number then adds 1 to it
def twos_complement(binary):
    binary = ones_complement(binary)
    binary = binary[::-1]

    if binary[0] == ONE:
        binary[0] = ZERO
        for index in range(1, len(binary)):
            if binary[index] == '1':
                binary[index] = '0'
            else:
                binary[index] = '1'
                break
    else:
        binary[0] = '1'

    binary = binary[::-1]
    return binary

# Adds two binary values together and throws away the carryout bit
def add(bin1, bin2):
    global num_additions
    num_additions += 1
    carry_bit = False
    bin1 = bin1[::-1]
    bin2 = bin2[::-1]
    result = pad_zeros(len(bin1))
    for index in range(len(bin1)):
        if (bin1[index] != ONE and bin2[index] != ONE and carry_bit) or (
                bin1[index] != ONE and bin2[index] == ONE and not carry_bit) or (
                bin1[index] == ONE and bin2[index] != ONE and not carry_bit) or (
                bin1[index] == ONE and bin2[index] == ONE and carry_bit):
            result[index] = ONE
        else:
            result[index] = ZERO

        if (bin1[index] != ONE and bin2[index] == ONE and carry_bit) or (
                bin1[index] == ONE and bin2[index] != ONE and carry_bit) or (
                bin1[index] == ONE and bin2[index] == ONE and not carry_bit) or (
                bin1[index] == ONE and bin2[index] == ONE and carry_bit):
            carry_bit = True
        else:
            carry_bit = False

    result = result[::-1]
    return result

# Performs the circular rotate operation on two binary values
def circular_rotate_right(accum, binary):
    accum_temp = []
    bin_temp = []

    for cur_index in range(len(accum)):
        rotate_to = (cur_index - 1) % len(accum)
        accum_temp.append(accum[rotate_to])

    for cur_index in range(len(binary)):
        rotate_to = (cur_index - 1) % len(binary)
        bin_temp.append(binary[rotate_to])

    accum_temp[0], bin_temp[0] = bin_temp[0], accum_temp[0]
    return accum_temp, bin_temp


def to_list(word):
    newList = []
    for i in range(len(word)):
        newList.append(word[i])
    return newList


def pad_zeros(size, binary=None):
    if binary is None:
        binary = []
    binary = binary[::-1]
    for i in range(len(binary), size):
        binary.append('0')
    binary = binary[::-1]
    return binary


def should_pre_complement(binary):
    if binary[0] == ONE:
        return True
    return False


def booths_algorithm(multiplicand, multiplier):
    # Initialisation of the two 'registers'
    multiplicand_size = len(multiplicand)
    last_bit = multiplicand_size - 1
    accumulator = pad_zeros(multiplicand_size)
    last_bit_moved = '0'
    two_comp_multiplier = twos_complement(multiplier)

    # Rules:
    # Q0 = 0, Q-1 = 0  -> No Action, Circular Rotate Right
    # Q0 = 0, Q-1 = 1  -> Add (Accum + Multiplier), Circular Rotate Right
    # Q0 = 1, Q-1 = 0  -> Sub (Accum + Twos_Comp_Multiplier), Circular Rotate Right
    # Q0 = 1, Q-1 = 1  -> No Action, Circular Rotate Right
    global iterations
    for turn in range(multiplicand_size):
        iterations += 1
        curr_last_bit = multiplicand[last_bit]

        if curr_last_bit == ZERO and last_bit_moved == ONE:
            accumulator = add(accumulator, multiplier)

        elif curr_last_bit == ONE and last_bit_moved == ZERO:
            accumulator = add(accumulator, two_comp_multiplier)

        accumulator, multiplicand = circular_rotate_right(accumulator, multiplicand)
        last_bit_moved = curr_last_bit

    return accumulator + multiplicand


def ext_booths_algorithm(multiplicand, multiplier):
    # Initialisation of the two 'registers'
    multiplicand_size = len(multiplicand)
    accumulator = pad_zeros(multiplicand_size)
    two_comp_multiplier = twos_complement(multiplier)
    multiplicand.append(ZERO)  # Appending a zero at the end
    action = [ZERO, ZERO, ZERO]
    bit1, bit2, bit3 = 0, 1, 2

    # Rules:
    # Q 000  -> No Action, Circular Rotate Right x 2
    # Q 001  -> Add (Accum + Multiplier), Circular Rotate Right x 2
    # Q 010  -> Add (Accum + Multiplier), Circular Rotate Right x 2
    # Q 011  -> Add x 2 (Accum + Multiplier), Circular Rotate Right x 2
    # Q 100  -> Sub x 2 (Accum + Twos_Comp_Multiplier), Circular Rotate Right x 2
    # Q 101  -> Sub (Accum + Twos_Comp_Multiplier), Circular Rotate Right x 2
    # Q 110  -> Sub (Accum + Twos_Comp_Multiplier), Circular Rotate Right x 2
    # Q 111  -> No Action, Circular Rotate Right x 2
    global iterations
    for turn in range((multiplicand_size + 1) // 2):
        iterations += 1

        action[-1] = multiplicand[-1]
        action[-2] = multiplicand[-2]
        action[-3] = multiplicand[-3]


        if action[0] == ZERO and ((action[1] == ZERO and action[2] == ONE) or (action[1] == ONE and action[2] == ZERO)):
            accumulator = add(accumulator, multiplier)

        elif action[0] == ZERO and action[1] == ONE and action[2] == ONE:
            accumulator = add(accumulator, multiplier)
            accumulator = add(accumulator, multiplier)

        elif action[0] == ONE and action[1] == ZERO and action[2] == ZERO:
            accumulator = add(accumulator, two_comp_multiplier)
            accumulator = add(accumulator, two_comp_multiplier)

        elif action[0] == ONE and (
                (action[1] == ZERO and action[2] == ONE) or (action[1] == ONE and action[2] == ZERO)):
            accumulator = add(accumulator, two_comp_multiplier)


        accumulator, multiplicand = circular_rotate_right(accumulator, multiplicand)
        accumulator, multiplicand = circular_rotate_right(accumulator, multiplicand)
        accumulator[0] = accumulator[2]
        accumulator[1] = accumulator[2]

    return accumulator + multiplicand[:multiplicand_size]


def main():
    correct_input = False
    print("Welcome to Booth's Calculator,")
    print("Please make sure all numbers are (4-12) in length")
    bin1 = ""
    bin2 = ""
    # Getting valid input for first binary number
    while not correct_input:
        print("Enter first binary number: ", end="")
        bin1 = input()
        if len(bin1) >= 4 and len(bin1) <= 12:
            correct_input = True
        else:
            print("Invalid range, binary value must be 4-12 in length")
    correct_input = False

    # Getting valid input for second binary number
    while not correct_input:
        print("Enter second binary number: ", end="")
        bin2 = input()
        if len(bin2) >= 4 and len(bin2) <= 12:
            correct_input = True
        else:
            print("Invalid range, binary value must be 4-12 in length")

    # Converting each input to a list since strings are immutable in python
    multiplicand = to_list(bin1)
    multiplier = to_list(bin2)

    # Makes the multiplicand and the multiplier the same length
    if len(multiplicand) > len(multiplier):
        multiplier = pad_zeros(len(multiplicand), multiplier)
    else:
        multiplicand = pad_zeros(len(multiplier), multiplicand)

    # Checks to see if pre/post complementation is necessary for the calculation
    pre_complement_multiplicand = should_pre_complement(multiplicand)
    pre_complement_multiplier = should_pre_complement(multiplier)
    post_complement_result = False

    # Complements the multiplicand and multiplier if necessary
    if pre_complement_multiplicand:
        multiplicand = twos_complement(multiplicand)
    if pre_complement_multiplier:
        multiplier = twos_complement(multiplier)
    if (not pre_complement_multiplicand and pre_complement_multiplier) or (
            pre_complement_multiplicand and not pre_complement_multiplier):
        post_complement_result = True


    global iterations
    global num_additions

    # Calculate using normal booth's algorithm the product of the multiplicand and the multiplier
    booth = booths_algorithm(multiplicand, multiplier)
    booth_iterations = iterations
    booth_num_add = num_additions

    # Resetting global counters
    iterations = 0
    num_additions = 0

    # Calculate using extended booth's algorithm the product of the multiplicand and the multiplier
    ext_booth = ext_booths_algorithm(multiplicand, multiplier)
    ext_booth_iterations = iterations
    ext_booth_num_add = num_additions

    # Determines if post complementation is necessary for the output
    if not post_complement_result:
        print("Regular Booth Results")
        print(booth)
        print("Num Iterations: " + str(booth_iterations))
        print("Num Additions: " + str(booth_num_add))
        print("-----------------------------")
        print("Extended Booth Results")
        print(ext_booth)
        print("Num Iterations: " + str(ext_booth_iterations))
        print("Num Additions: " + str(ext_booth_num_add))
        print("-----------------------------")
    else:
        print("Regular Booth Results")
        print(twos_complement(booth))
        print("Num Iterations: " + str(booth_iterations))
        print("Num Additions: " + str(booth_num_add))
        print("-----------------------------")
        print("Extended Booth Results")
        print(twos_complement(ext_booth))
        print("Num Iterations: " + str(ext_booth_iterations))
        print("Num Additions: " + str(ext_booth_num_add))
        print("-----------------------------")


# initiates main
main()
