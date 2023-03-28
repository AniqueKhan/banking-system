import pandas as pd
from sklearn.preprocessing import OrdinalEncoder 
from sklearn.model_selection import train_test_split  
from sklearn.metrics import precision_score, recall_score, accuracy_score 
from sklearn.tree import DecisionTreeClassifier
import joblib 

# Reading the data
train_data = pd.read_csv("dataset.csv")

# Dropping Loan_ID
train_data.drop(["Loan_ID"], axis=1, inplace=True)

#### Dealing with Numerical Values missig_data ##  

n_cols = train_data[["Coapplicant_Income", "Loan_Amount_Term"]] 
for i in n_cols: 
    train_data[i].fillna(train_data[i].mean(axis=0), inplace=True)

ord_enc = OrdinalEncoder()
train_data[["Gender",'Married','Education','Self_Employed','Property_Area','Loan_Status']] = ord_enc.fit_transform(train_data[["Gender",'Married','Education','Self_Employed','Property_Area','Loan_Status']])
train_data[["Gender",'Married','Education','Self_Employed','Property_Area','Loan_Status']] = train_data[["Gender",'Married','Education','Self_Employed','Property_Area','Loan_Status']].astype('int')


X = train_data.drop("Loan_Status", axis=1) 
y = train_data["Loan_Status"] 

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=2) 



def loss(y_true, y_pred): 
    pre=  precision_score(y_true, y_pred) 
    rec = recall_score(y_true, y_pred) 
    acc = accuracy_score(y_true, y_pred) 


ds = DecisionTreeClassifier(max_depth=8, max_features=0.9, max_leaf_nodes=30,
                       min_impurity_decrease=0.05, min_samples_leaf=0.02,
                       min_samples_split=10, min_weight_fraction_leaf=0.005,
                       random_state=2, splitter='random') 
ds.fit(X_train, y_train) 
pred4 =ds.predict(X_test) 
loss(y_test, pred4)

joblib.dump(ds, "model2.pkl") 


