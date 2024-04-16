import time

# 54 items
INVENTORY = [1, 1, 6, 6, 11, 11, 11, 11, 11, 11, 16, 16, 21, 21, 21, 21, 26, 31, 36, 36, 41, 41, 41, 46, 46, 51, 51, 51, 51, 51, 51, 56, 56, 66, 71, 76, 76, 81, 81, 81, 81, 86, 86, 86, 91, 91, 91, 96, 96, 96, 96, 96, 96, 96]

# choices and weights for each position
CHOICES = [
    [23, 24, None],
    [20, 21, 22, 23, 24, 18, 19, 25, 26, 27, 28, 29, 30, None],
    [25, 26, 27, 28, 29, 30, 31, 32, None],
    [23, 24, 25, 26, 27, 28, 29, 30, None],
    [4, 5, 6, 7, 8, 9, 10, 11, 2, 3, 12, 13, 14, 15, None],
    [16, 12, 13, 14, 15, 17, 10, 11, None],
    [20, 21, 22, 18, 19, 23, 24, 17, 25, 26, 27, 28, 29, 30, None],
    [12, 13, 14, 15, 10, 11, 16, 4, 5, 6, 7, 8, 9, None],
    [17, 16, 18, 19, 12, 13, 14, 15, None],
    [34, 33, None],
    [37, 38, 39, 40, 35, 36, 41, 42, 43, 34, 44, 45, 46, None],
    [25, 26, 27, 28, 29, 30, 23, 24, 31, 32, None],
    [18, 19, None],
    [20, 21, 22, 18, 19, None],
    [31, 32, 25, 26, 27, 28, 29, 30, 23, 24, 33, None],
    [25, 26, 27, 28, 29, 30, 31, 32, None],
]

WEIGHTS = [
    [1, 1, 1000],
    [2, 2, 2, 3, 3, 7, 7, 8, 8, 8, 8, 8, 8, 1000],
    [2, 2, 2, 2, 2, 2, 3, 3, 1000],
    [2, 2, 3, 3, 3, 3, 3, 3, 1000],
    [2, 2, 2, 2, 2, 2, 3, 3, 7, 7, 8, 8, 8, 8, 1000],
    [1, 4, 4, 4, 4, 6, 9, 9, 1000],
    [0, 0, 0, 5, 5, 5, 5, 10, 10, 10, 10, 10, 10, 10, 1000],
    [2, 2, 2, 2, 3, 3, 7, 8, 8, 8, 8, 8, 8, 1000],
    [2, 3, 7, 7, 8, 8, 8, 8, 1000],
    [2, 3, 1000],
    [1, 1, 1, 1, 4, 4, 6, 6, 6, 9, 11, 11, 11, 1000],
    [1, 1, 1, 1, 1, 1, 4, 4, 6, 6, 1000],
    [1, 1, 1000],
    [1, 1, 1, 4, 4, 1000],
    [1, 1, 4, 4, 4, 4, 4, 4, 9, 9, 11, 1000],
    [2, 2, 2, 2, 2, 2, 3, 3, 1000],
]


def iterate_choices_brute(pos, current_choices, current_weight, combos):
    """Attempt #1 -- just brute force through all combinations"""

    if pos >= len(CHOICES):
        # no more choices to make, add this combo to list
        combos.append((current_weight, current_choices))
        return

    # iterate through choices for current position
    for i in range(len(CHOICES[pos])):
        c = CHOICES[pos][i]
        w = WEIGHTS[pos][i]
        if c is not None and c in current_choices:
            # choice already selected, skip
            continue

        iterate_choices_brute(pos + 1, current_choices + [c], current_weight + w, combos)


best_weight = None
def iterate_choices_best(pos, current_choices, current_weight, combos):
    """Attempt #2 -- skip checking some branches by keeping track of the best total weight so far"""

    global best_weight

    if pos >= len(CHOICES):
        # no more choices to make, add this combo to list

        combos.append((current_weight, current_choices))

        # record weight if it's the best we've seen so far
        if best_weight is None or current_weight < best_weight:
            best_weight = current_weight

        return

    # iterate through choices for current position
    for i in range(len(CHOICES[pos])):
        c = CHOICES[pos][i]
        w = WEIGHTS[pos][i]

        if best_weight is not None and current_weight + w >= best_weight:
            # we're already worst than other combo, so skip this branch
            continue

        if c is not None and c in current_choices:
            # choice already selected, skip
            continue

        iterate_choices_best(pos + 1, current_choices + [c], current_weight + w, combos)


if __name__ == "__main__":
    all_combos = []
    s = time.perf_counter()
    #iterate_choices_brute(0, [], 0, all_combos)
    iterate_choices_best(0, [], 0, all_combos)
    e = time.perf_counter()
    all_combos.sort(key=lambda c: c[0])
    e2 = time.perf_counter()

    print(f'Iteration took {e - s:.06f} sec')
    print(f'Sort took {e2 - e:.06f} sec')
    print("")

    print("Weight\tChoices")
    print("-------\t--------")
    for i in range(len(all_combos)):
        print(f'{all_combos[i][0]}\t{all_combos[i][1]}')
    print("")
