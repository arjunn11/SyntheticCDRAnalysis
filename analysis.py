import csv
import pandas as pd
import numpy as np
import math
import sys
import matplotlib.pyplot as plt

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
    num_unique_people = pd.concat([df['LineID.From'], df['LineID.To']]).nunique()
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
    #remove NaN values from LineId.To
    incoming_contacts = contacts_df['LineID.To'][~np.isnan(df['LineID.To'])]
    incoming_frequency = incoming_contacts.astype(int).value_counts().sort_index()
    person_asymmetry = outgoing_frequency - incoming_frequency
    #Remove nulls from Series
    person_asymmetry = person_asymmetry[~np.isnan(person_asymmetry)]
    #Convert frequency values from float to integer
    person_asymmetry = person_asymmetry.astype(int)
    max_asymmetry = person_asymmetry.abs().idxmax()
    print('\n5. Person with largest asymmetry: ', max_asymmetry)
    print(' + Level of asymmetry (Outgoing - Incoming Contacts): ', person_asymmetry[max_asymmetry])

def additional_analysis(df):
    print('\n--------\n\nAdditional Analysis')
    charge_pivot = charge_analysis(df)
    df_handset2, df_handset = handset_analysis(df)
    handsetChart = handset_piechart(df_handset)
    #handsetChart.savefig('handset.jpg')
    transaction_pivot = transaction_analysis(df)
    #Output to Excel:
    writer = pd.ExcelWriter('output.xlsx')
    df.to_excel(writer, 'Raw Data')
    charge_pivot.to_excel(writer, 'Charge per Person')
    df_handset.to_excel(writer, 'Users per Handset Model')
    df_handset2.to_excel(writer, 'Calls per Handset model')
    transaction_pivot.to_excel(writer, 'Transaction Stats')
    writer.close()

def charge_analysis(df):
    print('\nCharges:\n')
    total_charge = df[(df.Transaction == 'call') | (df.Transaction == 'sms')]
    totalCharge = sum(total_charge['Charge'])
    maxCharge = total_charge['Charge'].max()
    meanCharge = totalCharge/pd.concat([df['LineID.From'], df['LineID.To']]).nunique()
    print('Total Charge:', totalCharge)
    charge_pivot = pd.pivot_table(total_charge,values='Charge',index='LineID.From',aggfunc='sum')
    charge_pivot=charge_pivot.reset_index()
    print('Max Charge / Person:\n', charge_pivot[charge_pivot['Charge'] == charge_pivot['Charge'].max()])
    print('Min Charge / Person:\n', charge_pivot[charge_pivot['Charge'] == charge_pivot['Charge'].min()])
    print('Standard Deviation: ',total_charge['Charge'].std())
    print('Coefficient of Variation: ',total_charge['Charge'].var())
    return charge_pivot

def handset_analysis(df):
    print('\nHandsets:\n')
    df_handset = pd.pivot_table(df, values = 'HandsetID.From',index='HandsetModel.From',aggfunc=pd.Series.nunique) #create pd.pivot_table
    df_handset = df_handset.reset_index() #reset index to force into dataframe format
    df_handset = df_handset.rename(columns={'HandsetID.From':'# Users','HandsetModel.From':'Handset Model'})
    df_handset.loc[:,'% Users'] = df_handset.loc[:,'# Users']/sum(df_handset['# Users'])
    idx = df_handset['# Users'].max()
    print('Most popular handset model:')
    print( df_handset[df_handset['# Users'] == df_handset['# Users'].max()] )
    df['Count'] = 1
    pivot_handset_calls = pd.pivot_table(df, values='Count',index='HandsetModel.From',aggfunc='sum')
    pivot_handset_calls = pivot_handset_calls.reset_index()
    pivot_handset_calls = pivot_handset_calls.rename(columns={'Count':'# Calls','HandsetModel.From':'Handset Model'})
    print('Most Active Handset:')
    print(pivot_handset_calls[pivot_handset_calls['# Calls'] == pivot_handset_calls['# Calls'].max()])
    print('Least Active Handset Model:')
    print(pivot_handset_calls[pivot_handset_calls['# Calls'] == pivot_handset_calls['# Calls'].min()])
    return pivot_handset_calls, df_handset

def handset_piechart(df_handset):
    #plot handset user percentage
    return df_handset['% Users'].plot.pie(labels=df_handset['Handset Model'], autopct='%.2f')

def transaction_analysis(df):
    print('\nTransactions:\n')
    df['Count'] = 1
    transaction_pivot = pd.pivot_table(df,values='Count',index='Transaction',aggfunc='sum')
    transaction_pivot = transaction_pivot.reset_index()
    transaction_pivot = transaction_pivot.rename(columns={'Count':'# Transactions'})
    transaction_users = pd.pivot_table(df,values='HandsetID.From',index='Transaction',aggfunc=pd.Series.nunique)
    transaction_users = transaction_users.reset_index()
    transaction_users = transaction_users.rename(columns={'HandsetID.From':'# Users'})
    transaction_pivot = pd.merge(transaction_pivot,transaction_users,how='inner',on="Transaction")
    print('Transactions Table:')
    print(transaction_pivot, '\n')
    return transaction_pivot

def main():
    df = pd.read_csv('syntheticCDR.csv')
    #Strip whitespace from DataFrame headers (column titles).
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    #Set output to file.
    sys.stdout = open('analysis.txt', 'w')
    print('Assumptions: \n+ 100 people, but 98 models, as 2 people never had any transactions. \n+ Contacts is defined as calls and sms. This can be changed to just calls by removing the sms filter on the data.')
    basic_analysis(df)
    additional_analysis(df)


if __name__ == '__main__':
  main()
