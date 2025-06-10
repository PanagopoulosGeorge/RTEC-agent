from utilities.temporal_ops import temporal_union


def maximal_intervals_from_str(lomi_str):
    str_timepoints_list = lomi_str.replace("(", "").replace(")", "").split(",")
    c = 0
    maximal_intervals_list = list()
    while c < len(str_timepoints_list):
        maximal_intervals_list.append(
            [int(str_timepoints_list[c]), int(str_timepoints_list[c + 1])]
        )
        c += 2
    return maximal_intervals_list


def maximal_intervals_to_str(lomi):
    output_str = "["
    for c in range(0, len(lomi)):
        start, finish = lomi[c]
        output_str += "(" + str(start) + "," + str(finish) + ")"
        if c < len(lomi) - 1:
            output_str += ","
    output_str += "]"
    return output_str


def parse_line(line):
    complex_event = {
        "name": "",
        "args": [],
        "value": "",
        "intervals": []
    }
    # Parse CE name
    name = line.split(",")[1]
    complex_event["name"] = name
    # Parse CE arguments
    args = line.split("[[")[1].split("]")[0].split(",")
    complex_event["args"] = args
    # Parse CE value
    value = line.split("],")[1]
    complex_event["value"] = value

    intervals_str = line.split(",[")[2].split("]).")[0]
    maximal_intervals_list = maximal_intervals_from_str(intervals_str)
    complex_event["intervals"] = maximal_intervals_list

    return complex_event


def parse_file(file_path):
    complex_events = {}
    with open(file_path, "r") as inp:
        # parse lines
        for line in inp:
            if "recognitions" in line:
                ce = parse_line(line)
                # key for FVP (without args)
                key = (ce["name"], ce["value"])
                args_key = tuple(ce["args"])
                # add FVP if not exists
                # also add a dict for that FVP, the ground
                # arguments, and the intervals for that instance
                if key not in complex_events:
                    complex_events[key] = {args_key: ce["intervals"]}
                else:
                    # if the arguments of current CE exist
                    # we need to amalgamate with the previous
                    # intervals (temporal union).
                    if args_key in complex_events[key]:
                        curr_int_list = complex_events[key][args_key]
                        new_int_list = ce["intervals"]
                        complex_events[key][args_key] = temporal_union(curr_int_list,
                                                                         new_int_list)
                    else:
                        complex_events[key][args_key] = ce["intervals"]
    return complex_events
