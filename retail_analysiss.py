import pandas as pd

#Εισάγω τα Δεδομένα μου
df = pd.read_csv("C:/Users/George/Desktop/Online_Retail.csv", encoding='latin1', sep=';', on_bad_lines='skip')

#Επιθεώρηση Δεδομένων
print(df.info())
print(df.head())
print(df.describe())

#Καθαρισμός τιμών
print(df.isnull().sum())


#Μετατρέπουμε UnitPrice σε float (είναι object αυτή τη στιγμή)
df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')

#Πετάμε τιμές χωρίς περιγραφή (Προϊόν)
df.dropna(subset=['Description'], inplace=True)

#Πετάμε γραμμές με αρνητική τιμή ή ποσότητα (Πιθανές επιστροφές ή λάθη)
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

#Μετατροπή Ημερομηνίας
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True)

#Φτιάχνω μια νέα στήλη: TotalPrice
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

#Πωλήσεις ανά χώρα(Top 10)
top_countries =df.groupby('Country')['InvoiceNo'].count().sort_values(ascending=False).head(10)

import matplotlib.pyplot as plt
plt.figure(figsize=(10,6))
top_countries.plot(kind='bar', color='skyblue')
plt.title('Top 10 Χώρες με τις Περισσότερες Συναλλαγές')
plt.ylabel('InvoiceNo')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#Συνολικά Έσοδα ανά προϊόν (Top 10)
top_products = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10,6))
top_products.plot(kind='barh', color='orange')
plt.title('Top 10 Προϊόντα με τα Περισσότερα Έσοδα')
plt.xlabel('Έσοδα')
plt.gca().invert_yaxis()
plt.tight_layout
plt.show()

#Πωλήσεις ανά μήνα
df['Month'] = df['InvoiceDate'].dt.to_period('M')
monthly_sales = df.groupby('Month')['TotalPrice'].sum()

monthly_sales.plot(figsize=(12,6), marker='o')
plt.title('Έσοδα ανά Μήνα')
plt.ylabel('Σύνολο Εσόδων')
plt.grid(True)
plt.show()

#Μέσο καλάθι αγορών ανά πελάτη
basket_value = df.groupby('CustomerID')['TotalPrice'].sum()
avg_basket = basket_value.mean()
print(f"Μέσο σύνολο αγορών ανά πελάτη: £{avg_basket:.2f}")

#Υπολογισμός RFM metrics
from datetime import timedelta
#Ορίζω 'σημερινή' ημερομηνία (μια μέρα μετά την τελευταία καταγραφή)
snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
#Ομαδοποιώ με βάση CustomerID
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate' :lambda x: (snapshot_date - x.max()).days, #Recency
    'InvoiceNo': 'nunique',                                  #Frequency
    'TotalPrice': 'sum'                                      #Monetary
}).reset_index()
#Μετονομάζουμε τις στήλες
rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']


#Δημιουργώ RFM Scores(1-5)
rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5]).astype(int)
# Συνδυάζω τα RFM scores σε ενα string για segmentation
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

#Ορισμός segments
def segment(row):
    if row['R'] >= 4 and row['F'] >= 4 and row['M'] >=4:
        return 'Champions'
    elif row['R'] >= 3 and row['F'] >= 3:
        return 'Loyal'
    elif row['R'] >= 4:
        return 'Recent'
    elif row['M'] >= 4:
        return 'Big Spenders'
    elif row['F'] >= 4:
        return 'Frequent'
    else:
        return 'Others'
rfm['Segment'] = rfm.apply(segment,axis=1)

#Οπτικοποίηση Segments
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10,6))
sns.countplot(data=rfm, x='Segment', order=rfm['Segment'].value_counts().index, palette='viridis')
plt.title('Κατανομή Πελατών ανά RFM Segment')
plt.ylabel('Αριθμός πελατών')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#Μέση αξία αγορών ανά Segment
segment_value = rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)
print(segment_value)

