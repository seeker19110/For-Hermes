import csv
def read_data(path):
    with open(path, "r") as f:
        return list(csv.reader(f))