import math
# ================= classes ====================


class Node:

    def __init__(self, char=None,):
        self.char = char
        self.ratio = 0
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.ratio < other.ratio


# ================= global variables ===================
encoding_table = {}  # I know its a bad practice to make global variables
decoding_table = {}
others_encoding_table = {}
others_decoding_table = {}

# ================= functions ==========================


def create_node_list(file, limit):
    text = file.read()
    dict_counts = {}
    lettersCount = len(text)
    othersNode = Node("others")
    shortCode = "000000"

    # traverse text and put characters in a dict
    for char in text:
        if char in dict_counts:
            dict_counts[char] += 1
        else:
            dict_counts[char] = 1

    # then move everything in the dict to a list
    node_list = []
    for char, count in dict_counts.items():
        nodeRatio = count / lettersCount

        if nodeRatio > limit:
            node = Node(char)
            node.ratio = nodeRatio
            node_list.append(node)

        else:
            others_encoding_table[char] = ""
            #shortCode = format(int(shortCode, 2) + 1, "06b")  # increment the short code
            othersNode.ratio += nodeRatio

    create_original_codes()

    # add the othersNode to the final list
    if others_encoding_table:
        node_list.append(othersNode)

    node_list.sort()

    return node_list


def create_original_codes():
    originalCodeSize = math.ceil(math.log2(len(others_encoding_table)))
    originalCode = format(0, f"0{originalCodeSize}b")

    for char, code in others_encoding_table.items():
        others_encoding_table[char] = originalCode
        originalCode = format(int(originalCode, 2) + 1, f"0{originalCodeSize}b")  # increment the original code

def create_huffman_tree(nodes):
    while len(nodes) > 1:
        newNodeRatio = nodes[0].ratio + nodes[1].ratio
        newNode = Node(None)
        newNode.ratio = newNodeRatio

        newNode.left = nodes[0]
        newNode.right = nodes[1]

        nodes.pop(0)
        nodes.pop(0)
        nodes.insert(0, newNode)

        # re-sort
        nodes.sort()

    return nodes[0]  # returns only the root


def create_coding_table(node, current_code):
    if node.char is None:
        create_coding_table(node.left, current_code + "0")
        create_coding_table(node.right, current_code + "1")

    else:
        encoding_table[node.char] = current_code
        decoding_table[current_code] = node.char


def create_others_decoding_table():
    for char, code in others_encoding_table.items():
        others_decoding_table[code] = char



def encode(file):
    text = file.read()
    encoded_text = ""

    for char in text:
        if char in others_encoding_table:
            encoded_text += encoding_table["others"] + others_encoding_table[char]
        else:
            encoded_text += encoding_table[char]

    return encoded_text


def decode(file, decoding_table, others_decoding_table):
    current_string = ""
    decoded_string = ""
    originalCodeSize = math.ceil(math.log2(len(others_decoding_table)))
    text = file.read()

    i = 0
    while i < len(text):
        current_bit = text[i]
        current_string += text[i]
        i += 1

        if current_string not in decoding_table:
            continue

        # if the current code is "others" code
        if decoding_table[current_string] == "others":
            six_bits = text[i : i + originalCodeSize]
            decoded_string += others_decoding_table[text[i : i + originalCodeSize]]  # the next originalCodeSize bits will be decoded
            i += originalCodeSize  # skip the next originalCodeSize bits
            current_string = ""

        else:
            decoded_string += decoding_table[current_string]
            current_string = ""

    return decoded_string

def create_decoding_file():
    with open("dict.txt", "w") as decodingFile:
        for code, char in decoding_table.items():

            decodingFile.write(f"{code} {repr(char)}\n")

        decodingFile.write("OTHERS\n")
        for code, char in others_decoding_table.items():
            decodingFile.write(f"{code} {repr(char)}\n")


def load_decoding_file(dict_file):
    global decoding_table, others_decoding_table
    decoding_table.clear()
    others_decoding_table.clear()

    currentSection = "NORMAL"

    for line in dict_file:
        line = line.rstrip("\r\n")

        if not line:
            continue

        if line == "OTHERS":
            currentSection = "OTHERS"
            continue

        if " " in line:
            code, repr_char = line.split(" ", 1)

            char = eval(repr_char)

            if currentSection == "NORMAL":
                decoding_table[code] = char
            else:
                others_decoding_table[code] = char

def main():
    while True:
        choice = int(input("1. Compress\n2. Decompress\n3. Exit\n"))


        if choice == 1:
            fileName = input("Enter file name including extension: ")
            limit = float(input("Enter min limit of ratio: "))
            with open(f"{fileName}", "r") as file:
                #file = f.read()

                create_coding_table(create_huffman_tree(create_node_list(file, limit)), "")
                file.seek(0)

                with open(f"./compressed.txt", "w") as compressedFile:
                    compressedFile.write(encode(file))

                create_others_decoding_table()
                create_decoding_file()

        elif choice == 2:
            fileName = input("Enter file name including extension: ")
            with open(f"./{fileName}", "r") as file:

                dictionaryFileChoice = input(f'Enter decoding table filename to use for decompression (press enter for default "dict.txt"): ')

                if dictionaryFileChoice == "":
                    dict_name = f"dict.txt"
                else:
                    dict_name = dictionaryFileChoice


                dictionaryFile = open(dict_name, "r")
                load_decoding_file(dictionaryFile)
                dictionaryFile.close()


                decompressed_data = decode(
                    file, decoding_table, others_decoding_table
                )
                with open(f"decompressed.txt", "w") as decompressedFile:
                    decompressedFile.write(decompressed_data)

        elif choice == 3:
            break


if __name__ == "__main__":
    main()
