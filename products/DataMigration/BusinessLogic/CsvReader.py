
import csv


def read_file(request):
    file = request.data['file']
    file = file.read().decode('utf-8').splitlines()
    csv_files = csv.DictReader(file)
    csv_file = [dict(i) for i in csv_files]
    return csv_file
