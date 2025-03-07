import json
import csv

with open('result.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

with open('result.csv', 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['pnk', 'url', 'qty']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    writer.writeheader()
    for item in data:
        writer.writerow(item)
