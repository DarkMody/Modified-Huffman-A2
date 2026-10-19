import operator # for sorting nodes



# ================= classes ====================
class Node:
    def __init__(self, char=None,):
        self.char = char
        self.probability = 0
        self.left = None
        self.right = None


#================= global variables ===================
encoding_table = {} # I know its a bad practice to make global variables
decoding_table = {}
others_encoding_table = {}
others_decoding_table = {}

#================= functions ==========================

def create_node_list(text, limit):

    dict = {}
    lettersCount = len(text)
    othersNode = Node("others")
    shortCode = "000000"

    # traverse text and put characters in a dict
    for char in text:
        if char in dict:
            dict[char] += 1
        else:
            dict[char] = 1

    # then move everything in the dict to a list
    list = []
    for char, count in dict.items():
        nodeProbability = count/lettersCount

        if nodeProbability > limit:
            node = Node(char)
            node.probability = nodeProbability
            list.append(node)

        else:
            others_encoding_table[char] = shortCode
            shortCode = format(int(shortCode, 2) + 1, "06b") # increment the short code
            othersNode.probability += nodeProbability


    # add the othersNode to the final list
    list.append(othersNode)
    # sort based on probability
    list.sort(key=lambda x: x.probability)

    return list

def create_huffman_tree(nodes):

    while (len(nodes) > 1):
        newNodeProbability = nodes[0].probability + nodes[1].probability
        newNode = Node(None)
        newNode.probability = newNodeProbability

        newNode.left = nodes[0]
        newNode.right = nodes[1]

        nodes.pop(0)
        nodes.pop(0)
        nodes.insert(0, newNode)

        # re-sort
        nodes.sort(key=lambda x: x.probability)


    return nodes[0] # returns only the root



def create_codes(node, current_code):

    if node.char == None:
        create_codes(node.left, current_code + "0")
        create_codes(node.right, current_code + "1")

    else:
        encoding_table[node.char] = current_code
        decoding_table[current_code] = node.char



def encode(text):
    encoded_text = ""

    for char in text:
        if char in others_encoding_table:
            encoded_text += encoding_table["others"] + str(others_encoding_table[char])
        else:
            encoded_text += encoding_table[char]


    return encoded_text

def decode(text, decoding_table, others_decoding_table):
    current_string = ""
    decoded_string = ""


    # fill others_decoding_table with entries
    for char, shortcode in others_encoding_table.items():
        others_decoding_table[shortcode] = char


    i = 0
    while i < len(text):

        current_bit = text[i]
        current_string += text[i]
        i += 1
        print(f"current bit: {current_bit} current string: {current_string} index {i}")

        if current_string not in decoding_table:
            continue

        # if the current code is "others" code
        if decoding_table[current_string] == "others":
            decoded_string += others_decoding_table[text[i:i+6]] # the next 6 bits will be decoded
            i += 6 # skip the next 6 bits
            current_string = ""

        else:
            decoded_string += decoding_table[current_string]
            current_string = ""



    return decoded_string


def create_decoding_file(fileName):
    decodingFile = open(f"./{fileName}_dict.txt", "w")
    for code, char in decoding_table.items():
        decodingFile.write(f"{code} {char}\n")


def main():

    while True:

        choice = int(input("1. Compress\n2. Decompress\n"))
        fileName = input("Enter file name including extenstion: ")
        limit = float(input("Enter min limit of probability: "))
        file = open(f"./{fileName}", "r").read()



        if choice == 1:

            create_codes(create_huffman_tree(create_node_list(file, limit)), "")

            with open(f"./{fileName[:-4]}_compressed.txt", "w") as compressedFile:
                compressedFile.write(encode(file))
            print(encode(file))

            create_decoding_file(fileName[:-4])



        elif choice == 2:


            decompressedFile = open(f"./{fileName[:-4]}_decompressed.txt", "w")
            decodingFileChoice = input(f'Enter decoding table to use for decompression (press enter for default "{fileName[:-4]}_dict.txt"')

            if decodingFileChoice == '':
                    decodingFile = open(f"./{fileName[:-4]}_dict.txt", "w")
                    decompressedFile.write(decode(file, decodingFile.read(), others_decoding_table))



        # reset tables
        decoding_table = {}
        encoding_table = {}
        others_decoding_table = {}
        others_encoding_table = {}



main()
