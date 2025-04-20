import os
import argparse
import re
from collections import defaultdict
import json

default_log_directory = "logs/"
patern = r'(\S+) - - \[(.+)\] "(\S+) (\S+)\s?(\S+)?\s?(\S+)?" (\d+) (\d+) "(.+)" "(.+)" (\d+)'


def write_to_json(json_name, data):
    with open(json_name, "w") as file:
        json.dump(data, file)


def parsing_line(line):
    patern_compile = re.compile(patern)
    result = patern_compile.findall(line)
    if result:
        return {
            "ip": result[0][0],
            "date": result[0][1],
            "method": result[0][2],
            "url": result[0][8],
            "duration": int(result[0][10]),
        }
    return None


def parsing_file(file_path):
    total_requests = 0
    ip_dict = defaultdict(int)
    method_dict = defaultdict(int)
    duration_list = []
    result_dict = {}

    with open(file_path, "r") as f:
        for line in f.readlines():
            total_requests += 1

            result = parsing_line(line)

            if result:
                duration_list.append(result)
                ip_dict[result["ip"]] += 1
                method_dict[result["method"]] += 1

        top_ips = sorted(ip_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        duration_list.sort(key=lambda x: x["duration"], reverse=True)

        top_durations = duration_list[:3]

        result_dict = {
            "top_ips": dict(top_ips),
            "top_longest": top_durations,
            "total_stat": dict(method_dict),
            "total_requests": total_requests,
        }
        write_to_json(
            os.path.splitext(os.path.basename(file_path))[0] + ".json", result_dict
        )
    return result_dict


parser = argparse.ArgumentParser(description="Parser for server log file")
parser.add_argument(
    "-f",
    "--folder",
    help="Input logs folder name or name of log file",
    type=str,
    default=default_log_directory,
)
args = parser.parse_args()
logs_path = "/home/masha/" + args.folder

try:
    if os.path.isdir(logs_path):
        list_logs = os.listdir(logs_path)

        for file_name in list_logs:
            file_path = logs_path + "/" + file_name
        result = parsing_file(file_path)
        json_data = json.dumps(result, indent=4)
        print(json_data)

    elif os.path.isfile(logs_path):
        result = parsing_file(logs_path)
        json_data = json.dumps(result, indent=4)
        print(json_data)
except FileNotFoundError:
    print("Incorrect file name or directory")
