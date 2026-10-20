
# ================= classes ====================


class Node:

    def __init__(
        self,
        char=None,
    ):
        self.char = char
        self.probability = 0
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.probability < other.probability


# ================= global variables ===================
encoding_table = {}  # I know its a bad practice to make global variables
decoding_table = {}
others_encoding_table = {}
others_decoding_table = {}

# ================= functions ==========================


def create_node_list(text, limit):
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
        nodeProbability = count / lettersCount

        if nodeProbability > limit:
            node = Node(char)
            node.probability = nodeProbability
            node_list.append(node)

        else:
            others_encoding_table[char] = shortCode
            shortCode = format(
                int(shortCode, 2) + 1, "06b"
            )  # increment the short code
            othersNode.probability += nodeProbability

    # add the othersNode to the final list
    node_list.append(othersNode)
    # sort based on probability
    node_list.sort()

    return node_list


def create_huffman_tree(nodes):
    while len(nodes) > 1:
        newNodeProbability = nodes[0].probability + nodes[1].probability
        newNode = Node(None)
        newNode.probability = newNodeProbability

        newNode.left = nodes[0]
        newNode.right = nodes[1]

        nodes.pop(0)
        nodes.pop(0)
        nodes.insert(0, newNode)

        # re-sort
        nodes.sort()

    return nodes[0]  # returns only the root


def create_codes(node, current_code):
    if node.char is None:
        create_codes(node.left, current_code + "0")
        create_codes(node.right, current_code + "1")

    else:
        encoding_table[node.char] = current_code
        decoding_table[current_code] = node.char


def encode(text):
    encoded_text = ""

    for char in text:
        if char in others_encoding_table:
            encoded_text += encoding_table["others"] + str(
                others_encoding_table[char]
            )
        else:
            encoded_text += encoding_table[char]

    return encoded_text


def decode(text, decoding_tbl, others_decoding_tbl):
    current_string = ""
    decoded_string = ""

    i = 0
    while i < len(text):
        current_bit = text[i]
        current_string += text[i]
        i += 1

        if current_string not in decoding_tbl:
            continue

        # if the current code is "others" code
        if decoding_tbl[current_string] == "others":
            decoded_string += others_decoding_tbl[
                text[i : i + 6]
            ]  # the next 6 bits will be decoded
            i += 6  # skip the next 6 bits
            current_string = ""

        else:
            decoded_string += decoding_tbl[current_string]
            current_string = ""

    return decoded_string


def create_decoding_file(fileName):
    with open(f"./dict.txt", "w") as decodingFile:
        for code, char in decoding_table.items():
            decodingFile.write(f"{code} {char}\n")


def load_decoding_file(dict_filename):
    global decoding_table, others_decoding_table
    decoding_table = {}
    others_decoding_table = {}

    with open(f"./{dict_filename}", "r") as f:
        for line in f:
            line = line.strip()
            # Check if the line is not empty and contains a space
            if line and " " in line:
                code, char = line.split(" ", 1)
                decoding_table[code] = char

                # If it's part of the 'others' escape scheme (6-bit short codes)
                if len(code) == 6 and code.isdigit():
                    others_decoding_table[code] = char

def main():
    while True:
        choice = int(input("1. Compress\n2. Decompress\n"))
        fileName = input("Enter file name including extension: ")

        if choice == 1:
            limit = float(input("Enter min limit of probability: "))
            with open(f"./{fileName}", "r") as f:
                file = f.read()

            create_codes(create_huffman_tree(create_node_list(file, limit)), "")

            with open(f"./{fileName[:-4]}_compressed.txt", "w") as compressedFile:
                compressedFile.write(encode(file))
            print(encode(file))

            create_decoding_file(fileName[:-4])

        elif choice == 2:
            with open(f"./{fileName}", "r") as f:
                file = f.read()

            decodingFileChoice = input(
                f'Enter decoding table filename to use for decompression (press enter for default "dict.txt"): '
            )

            if decodingFileChoice == "":
                dict_name = f"dict.txt"
            else:
                dict_name = decodingFileChoice

            # Load the dictionary from file into our tables
            load_decoding_file(dict_name)

            # Perform decoding and write to output file
            decompressed_data = decode(
                file, decoding_table, others_decoding_table
            )
            with open(
                f"./{fileName[:-4]}_decompressed.txt", "w"
            ) as decompressedFile:
                decompressedFile.write(decompressed_data)

        # reset global tables for next loop iteration
        decoding_table = {}
        encoding_table = {}
        others_decoding_table = {}
        others_encoding_table = {}


if __name__ == "__main__":
    main()
