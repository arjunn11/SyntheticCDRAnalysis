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

def basic_analysis(df):
    #Calculate total charged over this period of time.
    #.loc() handles indexing
    total_charge = df.loc[(df.Transaction == 'call') | (df.Transaction == 'sms'), 'Charge'].sum()
    print('Questions:\n1. Total Charge: ', total_charge)

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
    #Find number of unique people/handsets.
    unique_people = np.unique(df[['LineID.From', 'LineID.To']])
    #remove NaN values (which come from 'LineID.To')
    unique_people = unique_people[~np.isnan(unique_people)]
    num_unique_people = len(unique_people)
    mean_balance_inquiries = num_balance_inquiries/num_unique_people
    print("\n3. Mean number of balance inquiries per person: ", mean_balance_inquiries)

    #Create DataFrame of contacts (defined as sms or call transactions)
    contacts_df = df[(df['Transaction'] == 'call') | (df['Transaction'] == 'sms')]

    #Mean degree of contacts per person (incoming and outgong):
    #Multiply count by two to include both incoming and outgoing.
    total_contacts = contacts_df.count()[0]*2
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
    #Remove nulls from Series
    person_asymmetry = person_asymmetry[~np.isnan(person_asymmetry)]
    #Convert frequency values from float to integer
    person_asymmetry = person_asymmetry.astype(int)
    max_asymmetry = person_asymmetry.abs().idxmax()
    print('\n5. Person with largest asymmetry: ', max_asymmetry)
    print(' + Level of asymmetry (Outgoing - Incoming Contacts)', person_asymmetry[max_asymmetry])

def additional_analysis(df):
    print('\n--------\n\nAdditional Analysis')
    charge(df)

def charge(df):
    total_charge = df[(df.Transaction == 'call') | (df.Transaction == 'sms')]
    totalCharge = sum(total_charge['Charge'])
    maxCharge = total_charge['Charge'].max()
    meanCharge = totalCharge/pd.concat([df['LineID.From'], df['LineID.To']]).nunique()
    print('Total Charge:', totalCharge)
    charge_pivot = pd.pivot_table(df,values='Charge',index='LineID.To',aggfunc='sum')
    charge_pivot=charge_pivot.reset_index()
    print(charge_pivot.columns.tolist())
    print('Max Charged User Spent:')
    print(charge_pivot[charge_pivot['Charge'] == charge_pivot['Charge'].max()])
    print('Min Charged User Spent:')
    print(charge_pivot[charge_pivot['Charge'] == charge_pivot['Charge'].min()], '\n')

def main():
    df = pd.read_csv('syntheticCDR.csv')
    #Strip whitespace from DataFrame headers (column titles).
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    #print(df.dtypes)
    #Set output to file.
    sys.stdout = open('analysis.txt', 'w')
    print('Assumptions: \n+ 100 people, but 98 models, as 2 people never had any transactions. \n+ Contacts is defined as calls and sms. This can be changed to just calls by removing the sms filter on the data.')
    basic_analysis(df)
    additional_analysis(df)


if __name__ == '__main__':
  main()
