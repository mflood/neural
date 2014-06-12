import yaml
import argparse

def create_arg_parser():
    parser = argparse.ArgumentParser(description='Kick off the neural modeller')
    parser.add_argument("-c",
                        "--config",
                        required=True,
                        metavar="FILEPATH",
                        help='path to config file')
    parser.add_argument("--testdata",
                        required=False,
                        metavar="FILEPATH",
                        help='path to test data file')
    parser.add_argument("--traindata",
                        required=False,
                        metavar="FILEPATH",
                        help='path to train data file')

    parser.add_argument("-e",
                        "--environments",
                        default=None,
                        metavar="[dev|qa|prod]",
                        help='comma separated list of envs to determins which hosts to poll for data')
    parser.add_argument("--explore",
                        action="store_true",
                        dest="explore",
                        help='Explore Model')
    parser.add_argument("--print",
                        action="store_true",
                        dest="print_model",
                        help='Print Model')
    parser.add_argument("-p",
                        action="store_true",
                        dest="do_prune",
                        help='Prune model')
    parser.add_argument("-q",
                        action="store_true",
                        help='Set log level to warning')
    return parser


if __name__ == "__main__":

    args = create_arg_parser().parse_args()
