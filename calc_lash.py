"""Ford Valve Lash Bucket Calculator"""

import copy
import sys

# Engine Parameters
CYLINDERS = 4
VALVES = 16

# Lash Limits
INTAKE_MIN =        0.007   # in
INTAKE_TARGET =     0.0095  # in
INTAKE_MAX =        0.012   # in

EXHAUST_MIN =       0.012   # in
EXHAUST_TARGET =    0.0142  # in
EXHAUST_MAX =       0.017   # in

# Current Measurements
#                    intake                                                   exhaust
CURRENT_BUCKETS =   [  382,   482,   542,   402,   442,   262,   302,   362,    342,   422,   342,   402,   322,   482,   462,   302]
CURRENT_LASH =      [0.012, 0.006, 0.008, 0.011, 0.009, 0.014, 0.009, 0.012,  0.014, 0.011, 0.012, 0.010, 0.014, 0.007, 0.007, 0.012]

# All Possible Buckets
BUCKETS = [0, 25, 50, 75, 100, 122, 142, 168, 182, 202, 222, 242, 262, 282, 302, 322, 342, 362, 382, 402, 422, 442, 462, 482, 502, 522, 542, 562, 582, 602, 625, 650, 675, 700, 725]

# Bucket Inventory
BUCKET_INV = [302, 322, 342, 342, 342, 342, 362, 362, 362, 362, 362, 362, 362, 362, 382, 382, 402, 402, 402, 422, 422, 422, 422, 675]
BUCKET_INV += CURRENT_BUCKETS
BUCKET_INV.sort()


def bucket_to_in(bucket_id:int) -> float:
    """
    Convert a bucket ID to a thickness in inches

    bucket id is decimal part of thickness in mm:
    XXX == 3.XXX mm
    """

    return (3 + bucket_id / 1000) / 25.4


def select_closest_bucket(buckets:list[int], thickness_in:float, method:str="round") -> int:
    """
    Select bucket in list closest to a thickness in inches
    """

    ideal_bucket = int(round((thickness_in * 25.4 - 3) * 1000))

    if ideal_bucket > max(buckets):
        return max(buckets)

    if ideal_bucket < min(buckets):
        return min(buckets)
    
    if ideal_bucket in buckets:
        return ideal_bucket

    for i, b in enumerate(buckets):
        if b > ideal_bucket:
            if method == "round":
                return b if b - ideal_bucket <= ideal_bucket - buckets[i - 1] else buckets[i - 1]
            elif method == "ceil":
                return b
            elif method == "floor":
                return buckets[i - 1]
            else:
                raise ValueError("Invalid method")


def select_possible_buckets(buckets:list[int], thickness_min_in:float, thickness_max_in:float) -> list[int]:
    """
    Select buckets in list that fall within thickness range in inches
    """

    if thickness_min_in > bucket_to_in(max(buckets)) or thickness_max_in < bucket_to_in(min(buckets)):
        return []

    min_bucket = select_closest_bucket(buckets, thickness_min_in, method="ceil")
    max_bucket = select_closest_bucket(buckets, thickness_max_in, method="floor")

    i1 = buckets.index(min_bucket)

    for i2 in range(len(buckets) - 1, -1, -1):
        if buckets[i2] == max_bucket:
            break

    return buckets[i1:i2+1]


def iterate(choices_all_positions):
    global c

    if len(choices_all_positions) == 1:
        # no more choices to make, return each choice for this position
        combos = [[c] for c in choices_all_positions[0]]
        c += len(combos)
        print(f'\r{c}', end='')
        sys.stdout.flush()
        return combos

    # iterate through all choices per position
    combos_this_position = []
    for choice in choices_all_positions[0]:
        choices_following_positions = copy.deepcopy(choices_all_positions[1:])

        # if we're making a choice, remove it from all following choices
        if choice is not None:
            # remove choice from next choices
            for position in range(len(choices_following_positions)):
                if choice in choices_following_positions[position]:
                    choices_following_positions[position].remove(choice)

        # iterate through choices for next position
        combos_following_positions = iterate(choices_following_positions)

        # add current choice to each combo for following positions
        for combo in combos_following_positions:
            combo.insert(0, choice)
            combos_this_position.append(combo)

    return combos_this_position


if __name__ == "__main__":
    print(f'Intake target: {INTAKE_TARGET:.04f} in')
    print(f'Intake range: {INTAKE_MIN:.04f} - {INTAKE_MAX:.04f} in')
    print(f'Exhaust target: {EXHAUST_TARGET:.04f} in')
    print(f'Exhaust range: {EXHAUST_MIN:.04f} - {EXHAUST_MAX:.04f} in')
    print("")

    ideal_buckets = []
    possible_buckets = []
    possible_deviations = []

    # for intake valves, calculate ideal bucket and possible buckets in inventory
    print("Intake:")
    i = 0
    for bucket, lash in zip(CURRENT_BUCKETS[:VALVES // 2], CURRENT_LASH[:VALVES // 2]):
        valve_dist = bucket_to_in(bucket) + lash
        ideal_bucket = select_closest_bucket(BUCKETS, valve_dist - INTAKE_TARGET)
        possible = select_possible_buckets(BUCKET_INV, valve_dist - INTAKE_MAX, valve_dist - INTAKE_MIN)
        deviations = [valve_dist - bucket_to_in(b) - INTAKE_TARGET for b in possible]

        possible_uniq = list(set(possible))
        possible_uniq.sort()
        print(f'#{i+1}\tValve Distance: {valve_dist:.04f} in')
        print(f'\tIdeal: {ideal_bucket}')
        print(f"\tPossible: {possible_uniq}")
        #for p in possible_uniq:
        #    print(f'\t\t{p}\tlash = {valve_dist - bucket_to_in(p):.04f} in')

        # add no choice (purchase) option
        possible.append(None)
        deviations.append(0)

        ideal_buckets.append(ideal_bucket)
        possible_buckets.append(possible)
        possible_deviations.append(deviations)

        i += 1
        print("")

    print("")

    # for exhaust valves, calculate ideal bucket and possible buckets in inventory
    print("Exhaust:")
    i = 0
    for bucket, lash in zip(CURRENT_BUCKETS[VALVES // 2:], CURRENT_LASH[VALVES // 2:]):
        valve_dist = bucket_to_in(bucket) + lash
        ideal_bucket = select_closest_bucket(BUCKETS, valve_dist - EXHAUST_TARGET)
        possible = select_possible_buckets(BUCKET_INV, valve_dist - EXHAUST_MAX, valve_dist - EXHAUST_MIN)
        deviations = [valve_dist - bucket_to_in(b) - EXHAUST_TARGET for b in possible]

        possible_uniq = list(set(possible))
        possible_uniq.sort()
        print(f'#{i+1}\tValve Distance: {valve_dist:.04f} in')
        print(f'\tIdeal: {ideal_bucket}')
        print(f"\tPossible: {possible_uniq}")
        #for p in possible_uniq:
        #    print(f'\t\t{p}\tlash = {valve_dist - bucket_to_in(p):.04f} in')

        # add no choice (purchase) option
        possible.append(None)
        deviations.append(0)

        ideal_buckets.append(ideal_bucket)
        possible_buckets.append(possible)
        possible_deviations.append(deviations)

        i += 1
        print("")

    # iterate through possible bucket choices to build list of all combinations
    num_combos = 1
    for p in possible_buckets:
        num_combos *= len(p)
    print(f'{num_combos} combinations (at most)')

    combos = []
    purchases = []
    total_deviations = []

    print("Calculating combinations")
    print("0", end='')
    sys.stdout.flush()
    c = 0
    combos = iterate(possible_buckets)
    print(f'{len(combos)} actual combinations')

    # determine number of purchases and deviations for each combo
    # for combo in combos:
    #     purchases.append(combo.count(None))
    #     total_dev = 0
    #     for i, bucket in enumerate(combo):
    #         if bucket is not None:
    #             total_dev += possible_deviations[i][possible_buckets[i].index(bucket)]
    #     total_deviations.append(total_dev)


"""
rules:
- for each position, there are a list of possible choices, which is a subset of total choices
- for each position, choose from possible choices, or make no choice (in that case, purchase ideal bucket)
- choices are made without replacement from the list of total choices
- for each choice, deviation is calculated

p_1 = [
    c_1         d_1
    c_2         d_2
    c_n         d_n
    no choice   0
]

p_2 = [
    c_1         d_1
    c_2         d_2
    c_n         d_n
    no choice   0
]

p_n = [
    c_1         d_1
    c_2         d_2
    c_n         d_n
    no choice   0
]


best solution:
sort by fewest no choices (purchases), then sort by lowest total deviation
"""
