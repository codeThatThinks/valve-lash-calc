"""Ford Valve Lash Bucket Calculator"""

import time


#### CONSTANTS ####
NUM_VALVES = 16

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

# Bucket Choices for each valve
IDEAL_BUCKETS = []

# Note: each choice must be universally unique, so the index for
# the bucket in BUCKET_INV is used instead of the actual bucket ID
CHOICES = []
"""
[
    (
        <valve index>,
        <number of choices>,
        [<list of choices>],
        [<list of weights>],
        <minimum weight>
    ),
    ...
]
"""


#### HELPER FUNCTIONS ####

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

    method =    round: round to nearest; round up if exactly halfway
                floor: always round down
                ceil: always round up
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

            if method == "ceil":
                return b

            if method == "floor":
                return buckets[i - 1]

            raise ValueError("Invalid method")

    # should never end up here
    raise RuntimeError("Could not find closest bucket")


def select_possible_buckets_from_inventory(thickness_min_in:float, thickness_max_in:float) -> list[int]:
    """
    Select buckets in inventory that fall within thickness range in inches (inclusive)
    Returns a list of bucket indicies in BUCKET_INV
    """

    if thickness_min_in > bucket_to_in(max(BUCKET_INV)) or thickness_max_in < bucket_to_in(min(BUCKET_INV)):
        return []

    min_bucket = select_closest_bucket(BUCKET_INV, thickness_min_in, method="ceil")
    max_bucket = select_closest_bucket(BUCKET_INV, thickness_max_in, method="floor")

    i1 = BUCKET_INV.index(min_bucket)

    for i2 in range(len(BUCKET_INV) - 1, -1, -1):
        if BUCKET_INV[i2] == max_bucket:
            break

    return list(range(i1, i2 + 1))


def generate_choices(valve_index:int, bucket:int, lash:float, lash_min:float, lash_max:float, lash_target:float):
    """
    Generate possible bucket choices for a valve and add to CHOICES list
    Also print out valve data
    """

    # calculate valve distance, ideal bucket, and possible bucket choices
    valve_dist = bucket_to_in(bucket) + lash
    ideal_bucket = select_closest_bucket(BUCKETS, valve_dist - lash_target)
    possible = select_possible_buckets_from_inventory(valve_dist - lash_max, valve_dist - lash_min)
    possible_with_w = [(c, int(round(abs(valve_dist - bucket_to_in(c) - lash_target), 4) * 10000)) for c in possible]

    # sort possible choices from lowest to highest weight
    possible_with_w.sort(key=lambda p: p[1])

    # add no choice (purchase) option
    possible_with_w.append((None, 10000))

    # split apart into possible choices and weights (deviations)
    possible_choices = [p[0] for p in possible_with_w]
    possible_weights = [p[1] for p in possible_with_w]
    min_weight = min(possible_weights)

    # print out valve data
    print(f'#{valve_index + 1}\tIdeal: {ideal_bucket}')
    print(f'\tChoices: {possible_choices}')
    print(f'\tWeights: {possible_weights}')
    print("")

    # sanity check
    assert len(possible_choices) == len(possible_weights)

    # add to choices list
    IDEAL_BUCKETS.append(ideal_bucket)
    CHOICES.append((valve_index, len(possible_choices), possible_choices, possible_weights, min_weight))


def map_choices_to_values(choices:list[int]) -> list[int]:
    """
    Map a list of choices (bucket indicies in BUCKET_INV) to a list of bucket ids in order of valves
    """

    mapped_choices = [(CHOICES[i][0], BUCKET_INV[j] if j is not None else None) for i, j in enumerate(choices)]
    mapped_choices.sort(key=lambda v: v[0])

    return [v[1] for v in mapped_choices]


#### OPTIMIZATION FUNCTION ####

# global variables
current_choices = [0] * NUM_VALVES  # temp list for current choices made so far
best_weight = None
best_choices = None

def iterate_choices(pos, prev_weight) -> bool:
    """
    pos: Current index in CHOICES
    prev_weight: Total weight of choices made so far

    Returns True if a new best combo is found
    """

    global best_weight, best_choices

    #time.sleep(1)
    #print(prev_weight, current_choices[:pos+1], "\033[K\r", end="")

    if pos == NUM_VALVES:
        # no more choices to make, check this combo
        # if it's the best we've seen so far, update best_weight and print it out
        if best_weight is None or prev_weight < best_weight:
            best_weight = prev_weight
            best_choices = current_choices[:]
            print(prev_weight, map_choices_to_values(current_choices))
            return True

        return False

    # recurse through choices for current position
    for i in range(CHOICES[pos][1]):
        c = CHOICES[pos][2][i]
        w = CHOICES[pos][3][i]
        current_choices[pos] = c
        current_weight = prev_weight + w

        if best_weight is not None:
            if current_weight >= best_weight:
                # already we're not better than best
                # since choices are pre-sorted, latter choices are same or worse
                # so skip rest of this branch
                break

            min_total_weight = current_weight + sum([CHOICES[p][4] for p in range(pos+1,NUM_VALVES)])
            if min_total_weight >= best_weight:
                # lower bound of total_weight for this branch is not better
                # not possible for this branch to have a better combo
                # since choices are pre-sorted, latter choices are same or worse
                # so skip rest of choices for this position
                break

        if c is not None and c in current_choices[:pos]:
            # choice already selected, skip
            continue

        if iterate_choices(pos + 1, current_weight):
            # since choices are pre-sorted, latter choices are same or worse
            # so if we find a new best, skip rest of choices for this position
            break

    return False


#### MAIN ####

def main():
    print("Ford Duratec/Ecoboost Valve Lash Calculator")
    print("")
    print(f'Intake lash: range {INTAKE_MIN:.04f} - {INTAKE_MAX:.04f} in, target {INTAKE_TARGET:.04f} in')
    print(f'Exhaust lash: range {EXHAUST_MIN:.04f} - {EXHAUST_MAX:.04f} in, target {EXHAUST_TARGET:.04f} in')
    print("")

    # generate possible choices for each valve and print it out
    print("Intake Valves:")
    i = 0
    for bucket, lash in zip(CURRENT_BUCKETS[:NUM_VALVES // 2], CURRENT_LASH[:NUM_VALVES // 2]):
        generate_choices(i, bucket, lash, INTAKE_MIN, INTAKE_MAX, INTAKE_TARGET)
        i += 1
    print("")

    print("Exhaust Valves:")
    for bucket, lash in zip(CURRENT_BUCKETS[NUM_VALVES // 2:], CURRENT_LASH[NUM_VALVES // 2:]):
        generate_choices(i, bucket, lash, EXHAUST_MIN, EXHAUST_MAX, EXHAUST_TARGET)
        i += 1
    print("")

    # sanity check
    assert len(CHOICES) == NUM_VALVES

    # sort CHOICES by valves with fewest choices to most
    CHOICES.sort(key=lambda v: v[1])

    # run optimization function to iterate through choices
    print("Calculating best combos (lower weight is better)...")
    print("")
    s = time.perf_counter()
    iterate_choices(0, 0)
    e = time.perf_counter()

    print("")
    print("Done.")
    print(f'Iteration took {e - s:.06f} sec')
    print("")

    # print out best choices
    print("Best Solution:")
    best_choices_mapped = map_choices_to_values(best_choices)

    for i, c in enumerate(best_choices_mapped):
        print(f'#{i + 1}\t{c if c is not None else IDEAL_BUCKETS[i]}')
    print("")

    if best_choices_mapped.count(None) == 0:
        print("No need to purchase buckets.")
    else:
        print("Purchase the following buckets:")
        purchases = []
        for i, c in enumerate(best_choices_mapped):
            if c is None:
                # purchase ideal bucket for valve
                purchases.append(IDEAL_BUCKETS[i])
        print(f'{purchases}')
    print("")



if __name__ == "__main__":
    main()
