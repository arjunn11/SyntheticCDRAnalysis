import csv
import pandas as pd
import numpy as np
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
    #text_to_csv()
    df = pd.read_csv('syntheticCDR.csv')
    #Strip whitespace from DataFrame headers (column titles).
    df.rename(columns=lambda x: x.strip(), inplace=True)
    #print(df.head())
    #print(df.dtypes)

    #Calculate total charged over this period of time.
    #.loc() handles indexing
    call_charge = df.loc[df['Transaction'] == 'call', 'Charge'].sum()
    sms_charge = df.loc[df['Transaction'] == 'sms', 'Charge'].sum()
    total_charge = call_charge + sms_charge
    print('Total Charge: ', total_charge, '\n')

    #Find most popular handset model.
    #Total handsets
    models_df = df[['HandsetID.From', 'HandsetModel.From']].drop_duplicates('HandsetID.From')
    most_popular = models_df['HandsetModel.From'].mode()[0]
    model_counts = models_df['HandsetModel.From'].value_counts()
    #Includes handsets which have models (ones which initiated transactions).
    total_handsets = models_df.count()[0]
    print('Most popular handset model:', most_popular)
    print("Count:", model_counts.max(), "| Total models:", total_handsets, '\n')

    #Find mean number of balance inquiries per person.
    num_balance_inquiries = df.loc[df['Transaction'] == 'balance inquiry'].count()[0]
    print("Mean number of balance inquiries per person: ", num_balance_inquiries, '\n')

    #Mean degree of contacts per person (incoming and outgong)
    print('Assumption: Contacts is defined as calls and sms.')
    calls_df = df[df['Transaction'] == 'call']
    sms_df = df[df['Transaction'] == 'sms']
    #Multiply each count by two to include both incoming and outgoing.
    total_contacts = sms_df.count()[0]*2 + calls_df.count()[0]*2
    #Find number of unique people/handsets.
    print('Note: 2 people dont make any transactions (only in LineId.To)')
    unique_contacts = np.unique(df[['LineID.From', 'LineID.To']])
    #remove NaN values
    unique_contacts = unique_contacts[~np.isnan(unique_contacts)]
    num_unique_contacts = len(unique_contacts)
    mean_contacts = total_contacts / num_unique_contacts
    print("Mean degree of contacts per person: ", mean_contacts)

def main():
    process()

if __name__ == '__main__':
  main()
