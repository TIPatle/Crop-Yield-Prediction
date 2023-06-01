import pickle

with open('../Model/KNN.pkl', 'rb') as file:
    knn = pickle.load(file)

with open('../Model/RadomForest.pkl', 'rb') as file:
    rf = pickle.load(file)

with open('../Model/VotingEnsemble.pkl', 'rb') as file:
    vr = pickle.load(file)

with open('../Model/Stacking.pkl', 'rb') as file:
    sr = pickle.load(file)

with open('../Model/pipeline.pkl', 'rb') as file:
    pipeline = pickle.load(file)

def prediction(model, test):
    test = pipeline.transform(test)

    if model == 'Random Forest':
        return rf.predict(test)
    elif model == 'K Nearest Neighbor':
        return knn.predict(test)
    elif model == 'Voting Ensemble':
        return vr.predict(test)
    elif model == 'Stacking':
        return sr.predict(test)
    
    return "Invalid Data"