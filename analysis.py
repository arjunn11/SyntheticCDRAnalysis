import csv
import pandas as pd
import math
def text_to_csv():
    with open('syntheticCDR.txt', 'r') as in_file:
        #remove whitespace
        stripped = (line.strip() for line in in_file)
        #ignore empty lines
        lines = (line for line in stripped if line)
        with open('syntheticCDR.csv', 'w') as out_file:
            out_file.write('\n'.join(lines))

def process():
    text_to_csv()
    data = pd.read_csv('syntheticCDR.csv')
    #Strip whitespace from DataFrame headers (column titles).
    data.rename(columns=lambda x: x.strip(), inplace=True)
    print(data.head())
    print(data.dtypes)

    #Calculate total charged over this period of time.
    total_charge = data.loc[(data['Transaction'] == 'call' or data['Transaction'] == 'sms'), 'Charge'].sum()
    print('total charge: ', total_charge)

    calls = data[data['Transaction'] == 'call']

def main():
    process()

if __name__ == '__main__':
  main()
