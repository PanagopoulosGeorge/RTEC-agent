import argparse

from utilities.compare import compare_ce, precision, recall, f1_score, get_micro, get_macro
from utilities.parser import parse_file


def parse_args():
    parser = argparse.ArgumentParser(description=""
                                                 "Compare two RTEC output files, "
                                                 "in terms of precision, recall and"
                                                 "F1 score. A report is printed on "
                                                 "the terminal as well as in an "
                                                 "output file.")

    parser.add_argument(
        '--gt',
        type=str,
        required=True,
        help='Path to the ground truth file.'
    )

    parser.add_argument(
        '--test',
        type=str,
        required=True,
        help='Path to the test file.'
    )

    parser.add_argument(
        '--out',
        type=str,
        required=True,
        help='Path to the scores file.'
    )

    return parser.parse_args()

# Example usage
if __name__ == "__main__":
    args = parse_args()

    gt_file_path = args.gt
    test_file_path = args.test
    output_file_path = args.out

    ces_gt = parse_file(gt_file_path)
    ces_test = parse_file(test_file_path)

    results = {}
    for ce in ces_gt:
        if ce in ces_test:
            results[ce] = compare_ce(ces_gt[ce], ces_test[ce])
        else:
            results[ce] = compare_ce(ces_gt[ce])

    micro_res = get_micro(results)

    macro_res = get_macro(results)

    results[("avgscores","micro")] = micro_res
    results[("avgscores","macro")] = macro_res


with open(output_file_path,'w') as out:
        out.write(",".join(["fluent","value",
                            "tp", "fp", "fn",
                            "precision", "recall",
                            "f1"])+"\n")

        for key in results:
            out.write(",".join([
                str(key[0]),
                str(key[1]),
                str(results[key]["tp"]),
                str(results[key]["fp"]),
                str(results[key]["fn"]),
                str(results[key]["precision"]),
                str(results[key]["recall"]),
                str(results[key]["f1"])
            ])+"\n")
