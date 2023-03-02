from sys import exit
from collections import defaultdict
import json
import re

fields = [("bus_id", int, True, None),
          ("stop_id", int, True, None),
          ("stop_name", str, True, r"([A-Z].*) (Road|Avenue|Boulevard|Street)"),
          ("next_stop", int, True, None),
          ("stop_type", str, False, r"(S|O|F)"),
          ("a_time", str, True, r"([0-1][0-9]|2[0-4]):[0-5][0-9]")]

# fields = {"bus_id": int, "stop_id": int, "stop_name": str, "next_stop": int,
#           "stop_type": str, "a_time": str}


def take_json():
    data = json.loads(input())
    return data


def check_data(data):
    error_log = {}
    for field in fields:
        error_log[field[0]] = 0
    error_log["total"] = 0
    for stop in data:
        for item in fields:
            field = item[0]
            _type = item[1]
            if not isinstance(stop[field], _type):
                error_log[field] += 1
                error_log["total"] += 1
            elif field == "stop_type" and len(stop[field]) > 1:
                error_log[field] += 1
                error_log["total"] += 1
            elif field != "stop_type" and stop[field] == "":
                error_log[field] += 1
                error_log["total"] += 1
    return error_log


def check_synt(data):
    error_log = {}
    for item in fields:
        if item[3]:
            error_log[item[0]] = 0
    error_log["total"] = 0
    for stop in data:
        for item in fields:
            if item[3]:
                field = item[0]
                req = item[2]
                synt = item[3]
                result = re.fullmatch(synt, stop[field])
                if not result:
                    if req:
                        error_log[field] += 1
                        error_log["total"] += 1
                    elif stop[field] != "":
                        error_log[field] += 1
                        error_log["total"] += 1
    return error_log


def check_lines(data):
    lines_count = defaultdict(int)
    for stop in data:
        lines_count[stop["bus_id"]] += 1
    return lines_count


def check_ondemand(data, transfers):
    errors = []
    for stop in data:
        if stop["stop_type"] == "O" and stop["stop_name"] in transfers:
            errors.append(stop["stop_name"])
    return sorted(errors)


def check_times(data):
    time_errors = {}
    prev_line = 0
    prev_time = ""
    for stop in data:
        if stop["bus_id"] == prev_line and stop["bus_id"] not in time_errors.keys():
            if int(stop["a_time"][:2]) < int(prev_time[:2]) \
                    or (int(stop["a_time"][:2]) == int(prev_time[:2])
                        and int(stop["a_time"][3:]) <= int(prev_time[3:])):
                time_errors[stop["bus_id"]] = stop["stop_name"]
        prev_line = stop["bus_id"]
        prev_time = stop["a_time"]
    return time_errors


def special_stops(data):
    all_lines = set()
    all_stops = set()
    starts_by_line = defaultdict(set)
    finals_by_line = defaultdict(set)
    transfer_stops = set()
    for stop in data:
        all_lines.add(stop["bus_id"])
        if stop["stop_name"] in all_stops:
            transfer_stops.add(stop["stop_name"])
        else:
            all_stops.add(stop["stop_name"])
        if stop["stop_type"] == "S":
            starts_by_line[stop["bus_id"]].add(stop["stop_name"])
        elif stop["stop_type"] == "F":
            finals_by_line[stop["bus_id"]].add(stop["stop_name"])
    for line in all_lines:
        if len(starts_by_line[line]) != 1 or len(finals_by_line[line]) != 1:
            print(f"There is no start or end stop for the line: {line}.")
            exit()
    starts = set()
    finals = set()
    for line, stops in starts_by_line.items():
        starts.update(stops)
    for line, stops in finals_by_line.items():
        finals.update(stops)
    return sorted(starts), sorted(transfer_stops), sorted(finals)


def disp_data_log(error_log):
    print(f'Type and required field validation: {error_log["total"]} errors')
    for item in fields:
        field = item[0]
        print(f'{field}: {error_log[field]}')
    return


def disp_synt_log(error_log):
    print(f'Format validation: {error_log["total"]} errors')
    for item in [x for x in fields if x[3]]:
        field = item[0]
        print(f'{field}: {error_log[field]}')
    return


def disp_spec_stops(starts, transfers, finals):
    print(f"Start stops: {len(starts)} {starts}")
    print(f"Transfer stops: {len(transfers)} {transfers}")
    print(f"Finish stops: {len(finals)} {finals}")


def disp_demand_errors(errors):
    print("On demand stops test:")
    if len(errors) == 0:
        print("OK")
    else:
        print(f"Wrong stop type: {errors}")


def disp_time_errors(time_errors):
    print("Arrival time test:")
    if len(time_errors) == 0:
        print("OK")
    else:
        for line, stop in time_errors.items():
            print(f"bus_id line {line}: wrong time on station {stop}")


def disp_lines_count(lines_count):
    print("Line names and number of stops:")
    for line, count in lines_count.items():
        print(f"bus_id: {line}, stops: {count}")
    return


def main():
    data = take_json()
    starts, transfers, finals = special_stops(data)
    demand_errors = check_ondemand(data, transfers)
    disp_demand_errors(demand_errors)


main()
