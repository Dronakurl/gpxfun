# test sdas file
# A greate place to test code
import pandas as pd
import plotly.express as px 
from sklearn.linear_model import Lasso, LassoCV
from sklearn.model_selection import (
    GridSearchCV,
    cross_val_predict,
    cross_val_score,
    train_test_split,
)
from sklearn.svm import SVR

from analyzer import BaseAnalyzer
from analyzer_factory import AnalyzerFactory
from app_data_functions import get_data_from_pickle_session
from mylog import get_log
from prepare_data import get_prepared_data

log = get_log("gpxfun", 10)

# get data
d, _ = get_data_from_pickle_session("test")


def test_lasso(d):
    # Test LASSO
    dr = get_prepared_data(d, startendcluster=0)
    a = AnalyzerFactory().get_analyzer("AnalyzeLasso")(dr)
    a.analyze(alpha=0.1)
    print(a.coeffs)


dr = get_prepared_data(d)
a = AnalyzerFactory().get_analyzer("AnalyzeSVR")(dr)

 

X = pd.get_dummies(dr[list(BaseAnalyzer.varformatdict.keys())])
dummycols = pd.Series(X.columns)
y = dr["speed"]
model = LassoCV(cv=10)
model.fit(X,y)
model.coef_

model = Lasso()
cross_val_predict(model,X,y)

scores=cross_val_score(model,X,y,cv=5)
print(scores)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
model=SVR()
model.fit(X_train,y_train)
yp=model.predict(X_test)
fig=px.scatter(x=y_test,y=yp)
fig.show()

parameters = {'kernel':('linear', 'rbf', 'poly'), 'degree':(2,3,4), 'C':[1, 10]}
clf=GridSearchCV(model,parameters)
clf.fit(X_train,y_train)
model=clf.best_estimator_
model.fit(X_train,y_train)
yp=model.predict(X_test)
fig=px.scatter(x=y_test,y=yp)
fig.show()
