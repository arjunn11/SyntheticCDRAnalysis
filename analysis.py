import csv
import pandas as pd

def convert_to_csv():
    with open('syntheticCDR.txt', 'r') as in_file:
        #remove whitespace
        stripped = (line.strip() for line in in_file)
        #ignore empty lines
        lines = (line for line in stripped if line)
        with open('syntheticCDR.csv', 'w') as out_file:
            out_file.write('\n'.join(lines))

def process():
    print(pd.read_csv('syntheticCDR.csv'))

def main():
    convert_to_csv()
    process()

if __name__ == '__main__':
  main()
