import csv
import pandas as pd
import numpy as np
import math
import sys

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
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    #df['LineID.From'] = pd.to_
    #print(df.head())
    #print(df.dtypes)

    #Set output to file.
    sys.stdout = open('analysis.txt', 'w')

    #Calculate total charged over this period of time.
    #.loc() handles indexing
    total_charge = df.loc[(df.Transaction == 'call') | (df.Transaction == 'sms'), 'Charge'].sum()
    print('Questions:\n\n1. Total Charge: ', total_charge)

    #Find most popular handset model.
    #Total handsets
    models_df = df[['HandsetID.From', 'HandsetModel.From']].drop_duplicates('HandsetID.From')
    most_popular = models_df['HandsetModel.From'].mode()[0]
    max_count = models_df['HandsetModel.From'].value_counts().max()
    #Includes handsets which have models (ones which initiated transactions).
    total_handsets = models_df.count()[0]
    print('\n2. Most popular handset model:', most_popular)
    print(" + Count:", max_count, "| Total handsets:", total_handsets)

    #Find mean number of balance inquiries per person:
    num_balance_inquiries = df.loc[df['Transaction'] == 'balance inquiry'].count()[0]
    print("\n3. Mean number of balance inquiries per person: ", num_balance_inquiries)

    #Create DataFrame of contacts (defined as sms or call transactions)
    contacts_df = df[(df['Transaction'] == 'call') | (df['Transaction'] == 'sms')]

    #Mean degree of contacts per person (incoming and outgong):
    #Multiply count by two to include both incoming and outgoing.
    total_contacts = contacts_df.count()[0]*2
    #Find number of unique people/handsets.
    unique_people = np.unique(df[['LineID.From', 'LineID.To']])
    #remove NaN values (which come from 'LineID.To')
    unique_people = unique_people[~np.isnan(unique_people)]
    num_unique_people = len(unique_people)
    mean_contacts = total_contacts / num_unique_people
    print('\n4. Mean degree of contacts per person: ', mean_contacts)
    print(' + Assumption: Contacts is defined as calls and sms.')
    print(' + Note: 2 people dont make any transactions (only in LineId.To)')

    #Asymmetry:
    #Use contacts_df so topups and balance inquries are filtered out.
    outgoing_frequency = contacts_df['LineID.From'].value_counts().sort_index()
    #first remove NaN values from LineId.To
    incoming_contacts = contacts_df['LineID.To'][~np.isnan(df['LineID.To'])]
    incoming_frequency = incoming_contacts.astype(int).value_counts().sort_index()
    person_asymmetry = outgoing_frequency - incoming_frequency
    #print(person_asymmetry.isnull())
    #Remove nulls from Series
    person_asymmetry = person_asymmetry[~np.isnan(person_asymmetry)]
    #Convert frequency values from float to integer
    person_asymmetry = person_asymmetry.astype(int)
    max_asymmetry = person_asymmetry.abs().idxmax()
    print('\n5. Person with largest asymmetry: ', max_asymmetry)
    print(' + Level of asymmetry: ', person_asymmetry[max_asymmetry], '(Outgoing - Incoming Contacts)')

    print('\n--------\n\nAdditional Analysis')

def main():
    process()

if __name__ == '__main__':
  main()
