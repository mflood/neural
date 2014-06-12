#!/usr/bin/python
import logging
import sys
import yaml
from model import Model
from configtool import create_arg_parser
from data import Data

from loghelper import init_logging

init_logging(logging.DEBUG)
logger = logging.getLogger("mesh")


args = create_arg_parser().parse_args()
yaml_file = args.config

config_dict = None
with open(yaml_file, "r") as handle:
    config_dict = yaml.load(handle)

model = Model()
for target in config_dict["targets"]:
    model.add_target(target)

for input_def in config_dict["inputs"]:
    input_name = input_def['name']
    values = input_def["values"]
    weight_adj = input_def.get("weight_adj", 1)
    model.add_input(input_name, values, weight_adj)

if config_dict.get("range_inputs"):
    for input_def in config_dict["range_inputs"]:
        input_name = input_def['name']
        ranges = input_def['ranges']
        weight_adj = input_def.get("weight_adj", 1)
        model.add_range_input(input_name, ranges, weight_adj)

if args.explore:
    data_set = Data(args.traindata)
    columns = data_set.columns()
    for column in columns:
        print "%s" % column
        all_values = data_set.all_values(column)
        print all_values
        print "min: %s max: %s" % (min([float(value) for value in all_values]), max([float(value) for value in all_values]))
        print "\n"
    sys.exit(1)



if args.traindata:
    data_set = Data(args.traindata)
    data_set.open_csv()
    for row in data_set:
        #print "input row: %s" % row
        model.train(row, config_dict["target_key"])
        #print model

    if args.do_prune:
        model.prune()
        #print model
    


def run_test():
    train_set = Data(args.testdata)
    train_set.open_csv()
    correct_dict = {}
    incorrect_dict = {}
    num_correct = 0
    num_rows = 0
    logger.info("Processing data")
    # CSV Header
    print "Id,%s" % config_dict["target_key"]
    for row in train_set:
        num_rows += 1
        #print "input row: %s" % row
        results = model.evaluate(row)
        print "%s,%s" % (row["Id"], results[0]['target'])
        if config_dict["target_key"] in row:
            correct_answer = row[config_dict["target_key"]] 
            logger.info("%s %s" % (results[0]['target'] , correct_answer))

            if results[0]['target'] == correct_answer:
                logger.debug("Correct")
                num_correct += 1
                correct_dict.setdefault(correct_answer, 0)
                correct_dict[correct_answer] += 1
                logger.debug("%s => %s" % ( correct_answer, results[0]))
            else:
                incorrect_dict.setdefault(correct_answer, 0)
                incorrect_dict[correct_answer] += 1
                logger.debug(" %s => %s" % ( correct_answer, results))
        if num_rows % 10000 == 0:
            logger.info("another 10000")
            

    logger.info("%s" % ((1.0 * num_correct) / (1.0 * num_rows)))
    logger.info("correcT: %s" % correct_dict)
    logger.info("incorrecT: %s" % incorrect_dict)

if args.testdata:
    #import cProfile
    #cProfile.run('run_test()')
    run_test()

if args.print_model:
    print model
