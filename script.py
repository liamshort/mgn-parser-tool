import argparse
import csv
import boto3

def _configure():
    parser = argparse.ArgumentParser(description="Insert the ID of the Target Instance")
    parser.add_argument(
        "-r",
        "--region", 
        help="AWS Region (default eu-west-1)", 
        nargs="?", 
        dest="region",
        default="eu-west-1"
    )
    parser.add_argument(
        "-e",
        "--exclude", 
        help="List of Source Server IDs to exclude from results (default [])", 
        nargs="?", 
        dest="exclude",
        default=[]
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Name of output CSV file (default mgn_data)",
        nargs="?",
        dest="output",
        default="mgn_data"
    )
    parser.add_argument(
        "-m",
        "--max-source-servers",
        help="Maximum number of Source Servers to parse (default 100)",
        nargs="?",
        dest="max",
        default=100
    )

    args = vars(parser.parse_args())

    region = args["region"]
    exclude = args["exclude"]
    output = args["output"] + ".csv"
    max = int(args["max"])

    return region, exclude, output, max

def main(region, exclude, output, max):
    client_mgn = boto3.client(
        "mgn",
        region
    )

    source_servers = client_mgn.describe_source_servers(
        maxResults = max
    )

    count_server = 0
    count_disks = 0
    size = 0

    with open(output, "w", newline="") as file:
        writer = csv.writer(file)
        csv_write(writer, ["Hostname", "Disk", "Size"])
        
        for server in source_servers["items"]:
            if server["sourceServerID"] not in exclude:
                count_server = count_server + 1
                for index, disk in enumerate(server["sourceProperties"]["disks"]):
                    if (len(server["sourceProperties"]["disks"]) > 1) and (index != 0):
                        csv_write(writer, [None, disk["deviceName"].replace(":0", ""), str(disk["bytes"]/1073741824)])
                    else:
                        csv_write(writer, [server["sourceProperties"]["identificationHints"]["hostname"], disk["deviceName"].replace(":0", ""), str(disk["bytes"]/1073741824)])
                    count_disks = count_disks + 1
                    size = size + disk["bytes"]

        csv_write(writer, [])
        csv_write(writer, ["Total Size (GiB)", str(size/1073741824)])
        csv_write(writer, ["Number of Disks", str(count_disks)])
        csv_write(writer, ["Number of Servers", str(count_server)])

def csv_write(writer, values):
    writer.writerow(values)

if __name__ == "__main__":
    region, exclude, output, max = _configure()
    main(region, exclude, output, max)
