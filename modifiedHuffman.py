import heapq, math, ast


class Node:
    def __init__(self, symbol=None, frequency=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


def count_and_ratio(text, max_ratio):
    dictionary = {}
    for ch in text:
        if ch in dictionary:
            dictionary[ch] += 1
        else:
            dictionary[ch] = 1
    ret = []
    other = ["other", 0]
    for ch, freq in dictionary.items():
        ratio = freq / len(text)
        if max_ratio < ratio:
            # ratio = round(ratio, 2)
            ret.append([ch, ratio])
        else:
            other[1] += ratio
    if other[1] > 0:
        ret.append(other)
    return [ret, dictionary]


def build_huffman_tree(chars):
    pq = []
    for pair in chars:
        node = Node(pair[0], pair[1])
        pq.append(node)
    heapq.heapify(pq)
    while len(pq) > 1:
        left = heapq.heappop(pq)
        right = heapq.heappop(pq)
        merged_node = Node(frequency=left.frequency + right.frequency)
        merged_node.left = left
        merged_node.right = right
        heapq.heappush(pq, merged_node)
    return pq[0]


def char_binary_codes(node, code="", codes_dictionary=None):
    if codes_dictionary == None:
        codes_dictionary = {}
    if node != None:
        if node.symbol != None:
            codes_dictionary[node.symbol] = code
        char_binary_codes(node.left, code + "0", codes_dictionary)
        char_binary_codes(node.right, code + "1", codes_dictionary)
    return codes_dictionary


def char_original_codes(dictinary, original_codes_len):
    original_codes = {}
    cnt = 0
    for ch, freq in dictinary.items():
        binary = format(cnt, "b")
        for i in range(0, original_codes_len - len(binary)):
            binary = "0" + binary
        original_codes[ch] = binary
        cnt += 1
    return original_codes


def modified_huffman_compress(file1="file1", file2="file2", max_ratio=0.05):
    with open(file1 + ".txt", encoding="utf-8", newline="") as fileOpener:
        text = fileOpener.read()
        [char_freq, dictionary] = count_and_ratio(text, max_ratio)
        num_chars = len(dictionary)
        root = build_huffman_tree(char_freq)
        codes_dictionary = char_binary_codes(root)
        original_codes_len = math.ceil(math.log2(num_chars))
        original_codes = char_original_codes(dictionary, original_codes_len)
        result = ""
        for ch in text:
            if ch in codes_dictionary:
                result += codes_dictionary[ch]
            else:
                result += codes_dictionary["other"] + original_codes[ch]
        with open(file2 + ".txt", "w", encoding="utf-8", newline="") as export:
            export.write(f"{result}")
        with open("codes_dictionary.txt", "w", encoding="utf-8", newline="") as cd:
            for ch, code in codes_dictionary.items():
                cd.write(f"{repr(ch)} {code}\n")
        with open(
            "original_codes_dictionary.txt", "w", encoding="utf-8", newline=""
        ) as ocd:
            for ch, code in original_codes.items():
                ocd.write(f"{repr(ch)} {code}\n")


def modified_huffman_decompress(file2="file2", file3="file3"):
    codes_dictionary = {}
    original_codes = {}
    with open("codes_dictionary.txt", encoding="utf-8", newline="") as cd:
        for line in cd:
            res = line.strip().rsplit(" ", 1)
            codes_dictionary[res[1]] = ast.literal_eval(res[0])
    with open("original_codes_dictionary.txt", encoding="utf-8", newline="") as ocd:
        for line in ocd:
            res = line.strip().rsplit(" ", 1)
            original_codes[res[1]] = ast.literal_eval(res[0])
    with open(file2 + ".txt", encoding="utf-8", newline="") as fileOpener:
        binary = fileOpener.read()
        text = ""
        look = ""
        i = 0
        while i < len(binary):
            look += binary[i]
            if look in codes_dictionary:
                if codes_dictionary[look] == "other":
                    j = 1
                    look = ""
                    while j <= math.ceil(math.log2(len(original_codes))):
                        look += binary[j + i]
                        j += 1
                    text += original_codes[look]
                    i += j - 1
                else:
                    text += codes_dictionary[look]
                look = ""
            i += 1
        with open(file3 + ".txt", "w", encoding="utf-8", newline="") as export:
            export.write(f"{text}")


while True:
    print("1. Compress\n2. Decompress\n0. Exit\n")
    choice = input()
    if choice == "0":
        break
    elif choice == "1":
        print("Plz enter the maximum ratio for the other component from 0 to 100")
        max_ratio = int(input())
        if max_ratio >= 0 and max_ratio <= 100:
            max_ratio /= 100
            print(
                "Default reader is file1 and exporter file2. Change?\n1. Yes\n2. No\n"
            )
            choice = input()
            if choice == "1":
                print("Input file reader name\n")
                file = input()
                print("Input exporter name\n")
                newFile = input()
                modified_huffman_compress(file, newFile, max_ratio)
            elif choice == "2":
                modified_huffman_compress(max_ratio=max_ratio)
            else:
                print("Wrong input")
        else:
            print("Wrong input")
    elif choice == "2":
        print("Default reader is file2 and exporter file3. Change?\n1. Yes\n2. No\n")
        choice = input()
        if choice == "1":
            print("Input file reader name\n")
            file = input()
            print("Input exporter name\n")
            newFile = input()
            modified_huffman_decompress(file, newFile)
        elif choice == "2":
            modified_huffman_decompress()
        else:
            print("Wrong input")
