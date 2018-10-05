import csv

with open('dataexample.csv', newline='', mode='r') as csvfile:
    spamreader = csv.reader(csvfile)
    row_count = 0
    for row_index, row in enumerate(spamreader):
        row_count = row_index
        if row_index == 0:
            print(f'Column names are {" ".join(row)}')
        elif row_index == 1:
            print(f'x y z values are {" ".join(row)}')
        else:
            temp = 'values for row ' + str(row_index) + ': '
            for cell_index, cell in enumerate(row):
                temp = temp + ',' + str(cell)
            print(f'{temp}')

    print(f'{row_count} rows are processed!')