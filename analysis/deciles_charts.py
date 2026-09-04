import argparse
import glob
import json
import logging
import pathlib
import re

import jsonschema
import numpy
import pandas
from ebmdatalab import charts


# replicate cohort-extractor's logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s [%(levelname)-9s] %(message)s [%(module)s]",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)
logger.addHandler(handler)


# This regex matches the outputs of the measures generation action, and allows us to loop over them in the
# get_measure_tables function below.
MEASURE_FNAME_REGEX = re.compile(r"measure_(?P<id>\w+)\.csv")

# This function loops over the given list of input files and checks whether they correspond to the outputs from the previous action.
# It then turns the measures data in the input files into Python objects, each with an 'id' corresponding to the file from which it was created.
def get_measure_tables(input_files):
    for input_file in input_files:
        measure_fname_match = re.match(MEASURE_FNAME_REGEX, input_file.name)
        if measure_fname_match is not None:
            measure_table = pandas.read_csv(input_file, parse_dates=["interval_start"])
            measure_table.attrs["id"] = measure_fname_match.group("id")
            yield measure_table


def drop_zero_denominator_rows(measure_table):
    """
    Zero-denominator rows could cause the deciles to be computed incorrectly, so should
    be dropped beforehand. For example, a practice can have zero registered patients. If
    the measure is computed from the number of registered patients by practice, then
    this practice will have a denominator of zero and, consequently, a ratio of inf.
    Depending on the implementation, this practice's ratio may be sorted as greater than
    other practices' ratios, which may increase the deciles.

    # It's non-trivial to identify the denominator column without the associated Measure
    # instance. It's much easier to test the value column for inf, which is returned by
    # Pandas when the second argument of a division operation is zero.
    """
    is_not_inf = measure_table["ratio"] != numpy.inf
    num_is_inf = len(is_not_inf) - is_not_inf.sum()
    logger.info(f"Dropping {num_is_inf} zero-denominator rows")
    return measure_table[is_not_inf].reset_index(drop=True)


def get_deciles_table(measure_table, config):
    return charts.add_percentiles(
        measure_table,
        period_column="interval_start",
        column="ratio",
        show_outer_percentiles=config["show_outer_percentiles"],
    )


def write_deciles_table(deciles_table, path, filename):
    create_dir(path)
    deciles_table.to_csv(path / filename, index=False)


def get_deciles_chart(measure_table, config):
    return charts.deciles_chart(
        measure_table,
        period_column="interval_start",
        column="ratio",
        show_outer_percentiles=config["show_outer_percentiles"],
    )


def write_deciles_chart(deciles_chart, path, filename):
    create_dir(path)
    deciles_chart.savefig(path / filename, bbox_inches="tight")


# These are helper functions for writing and finding directories.
def create_dir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def get_path(*args):
    return pathlib.Path(*args).resolve()


def match_paths(pattern):
    return [get_path(x) for x in glob.glob(pattern)]


# The following defines some configuration for the deciles charts, and a schema against which to validate that 
# configuration. The configuration can be overridden in part or whole by passing in a different value on the 
# command line, but that value must match the schema defined here.
CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "show_outer_percentiles": {"type": "boolean"},
        "tables": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "output": {"type": "boolean"},
            },
        },
        "charts": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "output": {"type": "boolean"},
            },
        },
    },
}

DEFAULT_CONFIG = {
    "show_outer_percentiles": False,
    "tables": {
        "output": True,
    },
    "charts": {
        "output": True,
    },
}

def parse_config(config_json):
    user_config = json.loads(config_json)
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    try:
        jsonschema.validate(config, CONFIG_SCHEMA)
    except jsonschema.ValidationError as e:
        raise argparse.ArgumentTypeError(e.message) from e
    return config

# This function defines the behaviour of this file when acting as a script (as it will in the project pipeline)
# in terms of the arguments it accepts.
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-files",
        required=True,
        type=match_paths,
        help="Glob pattern for matching one or more input files",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=get_path,
        help="Path to the output directory",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG.copy(),
        type=parse_config,
        help="JSON-encoded configuration",
    )
    return parser.parse_args()

# This function runs when the file is called as a script in the project pipeline.
def main():
    args = parse_args()
    input_files = args.input_files
    output_dir = args.output_dir
    config = args.config

    for measure_table in get_measure_tables(input_files):
        measure_table = drop_zero_denominator_rows(measure_table)
        id_ = measure_table.attrs["id"]
        if config["tables"]["output"]:
            deciles_table = get_deciles_table(measure_table, config)
            fname = f"deciles_table_{id_}.csv"
            write_deciles_table(deciles_table, output_dir, fname)

        if config["charts"]["output"]:
            chart = get_deciles_chart(measure_table, config)
            fname = f"deciles_chart_{id_}.png"
            write_deciles_chart(chart, output_dir, fname)


if __name__ == "__main__":
    main()