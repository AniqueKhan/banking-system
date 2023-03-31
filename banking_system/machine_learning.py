import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle,joblib

df=pd.read_csv("dataset.csv")
# print(df['Loan_Amount_Term'])
df['Loan_Amount_Term'].fillna(df['Loan_Amount_Term'].mode()[0],inplace=True)
df['Coapplicant_Income'].fillna(df['Coapplicant_Income'].mode()[0],inplace=True)
df['Loan_Amount_Log']=np.log(df['Loan_Amount'])

# Split the dataset into training and testing sets with an 80-20 ratio
train_df_original, test_df_original = train_test_split(df, test_size=0.2, random_state=42)

train_df=train_df_original.drop("Loan_ID",axis=1)
test_df=test_df_original.drop("Loan_ID",axis=1)

X , y = train_df.drop("Loan_Status",axis=1) , train_df.Loan_Status

X = pd.get_dummies(X)
train_df=pd.get_dummies(train_df)
test_df=pd.get_dummies(test_df)

x_train, x_cv, y_train, y_cv = train_test_split(X,y, test_size=0.3)

model = LogisticRegression()
model.fit(x_train, y_train)

with open("model.pkl","wb") as f:
    pickle.dump(model,f)