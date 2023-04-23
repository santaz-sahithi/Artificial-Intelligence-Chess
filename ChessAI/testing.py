import json

valid_moves = {
    "knight": [],
    "king": [],
    "bishop": [],
    "rook": [],
    "queen": [],
}
knight_vm = []


def main():
    t = [-2, -1, 1, 2]
    for x in t:
        for y in t:
            if abs(x) != abs(y):
                knight_vm.append((x, y))
    valid_moves["knight"] = knight_vm

    t = [-1, 0, 1]
    for x in t:
        for y in t:
            valid_moves["king"].append((x, y))

    t = [-7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7]

    for x in t:
        valid_moves["bishop"].append((x, x))
        valid_moves["rook"].append((0, x))
        valid_moves["rook"].append((x, 0))

        valid_moves["queen"].append((x, x))
        valid_moves["queen"].append((0, x))
        valid_moves["queen"].append((x, 0))

    with open("chess_info.json", "r", encoding="UTF-8") as fp:
        data = json.load(fp)

    data["valid_moves"] = valid_moves

    with open("chess_info.json", "w", encoding="UTF-8") as fp:
        json.dump(data, fp, indent=4)


if __name__ == '__main__':
    main()
