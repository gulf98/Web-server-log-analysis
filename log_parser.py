import argparse
import itertools
import json
import re
from pathlib import Path

REGEXP_PATTERN = r"(?P<ip>\S+)\s+" \
                 r"(\S+)\s+" \
                 r"(\S+)\s+" \
                 r"\[(?P<time>.+)\]\s+" \
                 r"\"(?P<method>OPTIONS|GET|HEAD|POST|PUT|PATCH|DELETE|TRACE|CONNECT)\s+" \
                 r"(?P<url>\S+)\s+" \
                 r"(\S+)\"\s+" \
                 r"(\d{3})\s+" \
                 r"(\S+)\s+" \
                 r"\"(.*)\"\s+" \
                 r"\"(.*)\"\s+" \
                 r"(?P<duration>\S+)"


def create_parser():
    _parser = argparse.ArgumentParser()
    _group = _parser.add_mutually_exclusive_group()
    _group.add_argument("--file", nargs="?", const="access.log")
    _group.add_argument("--folder", nargs="?", const="./")
    return _parser


def get_file_paths(_parser):
    _namespace = _parser.parse_args()
    _file = _namespace.file
    _folder = _namespace.folder
    if _file:
        if not re.search(".log$", _file):
            raise ValueError("The file must have a log extension")
        _file_paths = [Path(_file)]
    elif _folder:
        _file_paths = list(Path(_folder).glob("*.log"))
        if not _file_paths:
            raise ValueError("No log file found in folder")
    else:
        raise ValueError("You must specify a directory or file")
    return _file_paths


def get_line_generator(_paths):
    for _path in _paths:
        try:
            with open(_path, "r") as _file:
                for _line in _file:
                    if _line:
                        yield _line
        except Exception as e:
            print("Error while reading file", e)


def parse_line(_line):
    _parsed_line = re.match(REGEXP_PATTERN, _line)
    if _parsed_line:
        return _parsed_line.groupdict()
    else:
        print("No match found for string: ", _line)


def parsing_and_collecting_metrics(_line_generator):
    _ip_metrics = {}
    _method_metrics = {"OPTIONS": 0, "GET": 0, "HEAD": 0, "POST": 0, "PUT": 0, "PATCH": 0, "DELETE": 0, "TRACE": 0,
                       "CONNECT": 0}
    _request_metrics = []

    for _line in _line_generator:
        _parsed_line = parse_line(_line)

        for _key, _value in _parsed_line.items():
            if _key == "ip":
                if not _ip_metrics.get(_value):
                    _ip_metrics.update({_value: 0})
                _ip_metrics.update({_value: _ip_metrics[_value] + 1})
            elif _key == "method":
                _method_metrics.update({_value: _method_metrics[_value] + 1})
            elif _key == "duration":
                _request_metrics.append(_parsed_line)

    _ip_metrics = dict(itertools.islice(sorted(_ip_metrics.items(), key=lambda item: item[1], reverse=True), 3))
    _method_metrics = dict(sorted(_method_metrics.items(), key=lambda item: item[1], reverse=True))
    _request_count = sum(_method_metrics.values())
    _request_metrics = list(
        itertools.islice(sorted(_request_metrics, key=lambda item: int(item["duration"]), reverse=True), 3))

    _metrics = {"request_count": _request_count,
                "method_metrics": _method_metrics,
                "ip_metrics": _ip_metrics,
                "request_metrics": _request_metrics,
                }
    return _metrics


def generate_report(_metrics):
    _report = list()
    _report.append(f"Total number of completed requests: {_metrics['request_count']}")
    _report.append(f"Number of requests by HTTP methods:")
    for key, value in _metrics["method_metrics"].items():
        _report.append(f"\t{key} - {value}")
    _report.append("Top 3 IP addresses from which requests were made:")
    for key, value in _metrics["ip_metrics"].items():
        _report.append(f"\t{key} - {value}")
    _report.append("Top 3 longest requests:")
    for item in _metrics["request_metrics"]:
        _report.append(f"\t{item['method']} {item['url']} {item['ip']} {item['duration']}ms {item['time']}")
    return _report


def output_to_console(_report):
    print(*_report, sep="\n")


def write_to_json(_metrics):
    with open("report.json", "w") as _report_file:
        json.dump(_metrics, _report_file, indent=4)


if __name__ == "__main__":
    parser = create_parser()
    file_paths = get_file_paths(parser)
    line_generator = get_line_generator(file_paths)
    metrics = parsing_and_collecting_metrics(line_generator)
    report = generate_report(metrics)
    output_to_console(report)
    write_to_json(metrics)
