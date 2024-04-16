"""Ford Valve Lash Bucket Calculator"""

import sys
import time

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

ideal_buckets = []
possible_buckets = []
"""
[
    [(bucket, weight), ...],
    ...
]
"""


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


best_weight = None
def iterate_choices_best(pos, current_choices, current_weight, combos):
    """Attempt #2 -- skip checking some branches by keeping track of the best total weight so far"""

    global best_weight, possible_buckets

    if pos >= len(possible_buckets):
        # no more choices to make, add this combo to list

        combos.append((current_weight, current_choices))

        # record weight if it's the best we've seen so far
        if best_weight is None or current_weight < best_weight:
            best_weight = current_weight
            print(f'New best weight is {best_weight}')

        return

    # iterate through choices for current position
    for i in range(len(possible_buckets[pos])):
        c = possible_buckets[pos][i][0]
        w = possible_buckets[pos][i][1]

        if best_weight is not None and current_weight + w >= best_weight:
            # we're already worst than other combo, so skip this branch
            continue

        if c is not None and c in current_choices:
            # choice already selected, skip
            continue

        iterate_choices_best(pos + 1, current_choices + [c], current_weight + w, combos)


if __name__ == "__main__":
    print(f'Intake target: {INTAKE_TARGET:.04f} in')
    print(f'Intake range: {INTAKE_MIN:.04f} - {INTAKE_MAX:.04f} in')
    print(f'Exhaust target: {EXHAUST_TARGET:.04f} in')
    print(f'Exhaust range: {EXHAUST_MIN:.04f} - {EXHAUST_MAX:.04f} in')
    print("")

    # for intake valves, calculate ideal bucket and possible buckets in inventory
    print("Intake:")
    i = 0
    for bucket, lash in zip(CURRENT_BUCKETS[:VALVES // 2], CURRENT_LASH[:VALVES // 2]):
        valve_dist = bucket_to_in(bucket) + lash
        ideal_bucket = select_closest_bucket(BUCKETS, valve_dist - INTAKE_TARGET)
        possible = select_possible_buckets(BUCKET_INV, valve_dist - INTAKE_MAX, valve_dist - INTAKE_MIN)
        possible_with_dev = [(c, int(round(abs(valve_dist - bucket_to_in(c) - INTAKE_TARGET)*100000))) for c in possible]

        # sort possible by deviation
        possible_with_dev.sort(key=lambda c: c[1])

        #possible_uniq = list(set(possible))
        #possible_uniq.sort()
        print(f'#{i+1}\tValve Distance: {valve_dist:.04f} in')
        print(f'\tIdeal: {ideal_bucket}')
        #print(f"\tPossible: {possible_uniq}")

        # add no choice (purchase) option
        possible_with_dev.append((None, 10000))

        ideal_buckets.append(ideal_bucket)
        possible_buckets.append(possible_with_dev)

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
        possible_with_dev = [(c, int(round(abs(valve_dist - bucket_to_in(c) - INTAKE_TARGET)*100000))) for c in possible]
        
        # sort possible by deviation
        possible_with_dev.sort(key=lambda c: c[1])

        #possible_uniq = list(set(possible))
        #possible_uniq.sort()
        print(f'#{i+1}\tValve Distance: {valve_dist:.04f} in')
        print(f'\tIdeal: {ideal_bucket}')
        #print(f"\tPossible: {possible_uniq}")

        # add no choice (purchase) option
        possible_with_dev.append((None, 10000))

        ideal_buckets.append(ideal_bucket)
        possible_buckets.append(possible_with_dev)

        i += 1
        print("")

    print("Possible buckets = [")
    for b in possible_buckets:
        print(f'\t{[c[0] for c in b]}')
    print("]\n")

    print("Possible deviations = [")
    for b in possible_buckets:
        print(f'\t{[c[1] for c in b]}')
    print("]\n")

    combos = []
    s = time.perf_counter()
    iterate_choices_best(0, [], 0, combos)
    e = time.perf_counter()

    print(f'Iteration took {e - s:.06f} sec')
    print("")

    print("Best Combos:")
    for i in range(len(combos)):
        print(f'{combos[i][0]}\t{combos[i][1]}')
    print("")