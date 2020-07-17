# -*- coding: utf-8 -*-
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
#from keras.wrappers.scikit_learn import KerasRegressor
#from sklearn.model_selection import cross_val_score
#from sklearn.model_selection import KFold

def ComputeOnline(
    onlineProblemData, operatorCompressionOutputData, timep
):
    """
    Compute the online stage using the method of POD on the snapshots and a regression on the coefficients

    The parameters must have been initialized in onlineProblemData

    Parameters
    ----------
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)

    Returns
    -------
    collections.OrderedDict
        onlineCompressedSnapshots; dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """
    regressor = operatorCompressionOutputData[0]
    scalerParameter = operatorCompressionOutputData[1]
    scalerCoefficients = operatorCompressionOutputData[2]

    timeSequence = onlineProblemData.GetParametersTimeSequence()

    print("[INFO] Regressor...")

    onlineParameters = onlineProblemData.GetParametersList()
    if timep:
       onlineParameters = np.hstack([onlineParameters, np.asarray(timeSequence, dtype=np.float32).reshape(len(timeSequence),1)]) ###overwrite if time
    print("[INFO] parameters...\n", onlineParameters)

    onlineParameters = scalerParameter.transform(onlineParameters)

    onlineCoefficients = regressor.predict(onlineParameters)
    
    onlineCoefficients = scalerCoefficients.inverse_transform(onlineCoefficients)

    import collections
    onlineCompressedSnapshots = collections.OrderedDict()

    for i, time in enumerate(timeSequence):
        onlineCompressedSnapshots[time] = onlineCoefficients[i,:]

    return onlineCompressedSnapshots


def CompressOperator(
    collectionProblemData, solutionName, timep=True
):
    """
    Computes the offline operator compression stage using the method of POD on the snapshots and a regression on the coefficients

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    solutionName : str
        name of the solution to be treated
    """
    assert isinstance(solutionName, str)

    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes(
        solutionName
    )
    numberOfSnapshots = collectionProblemData.GetGlobalNumberOfSnapshots(solutionName)
    parameterDimension = collectionProblemData.GetParameterDimension()

    coefficients = np.zeros((numberOfSnapshots, numberOfModes))
    parameters = np.zeros((numberOfSnapshots, parameterDimension))   
    if timep:
       parameters = np.zeros((numberOfSnapshots, parameterDimension+1))    ###attention overwirite, added +1 for time

    count = 0
    for key, problemData in collectionProblemData.GetProblemDatas().items():

        localNumberOfSnapshots = problemData.GetSolution(
            solutionName
        ).GetNumberOfSnapshots()

        times = problemData.GetSolution(solutionName).GetTimeSequenceFromCompressedSnapshots()

        coefficients[count : count + localNumberOfSnapshots, :] = (
            problemData.GetSolution(solutionName).GetCompressedSnapshotsList()
        )

        localParameters = np.array([problemData.GetParameterAtTime(t) for t in times])
        if len(times)>1:
            localParameters = np.hstack([localParameters, np.asarray(times, dtype=np.float32).reshape(len(times),1)]) ###overwrite if time
        parameters[count : count + localNumberOfSnapshots, :] = localParameters

        count += localNumberOfSnapshots

    from sklearn.preprocessing import MinMaxScaler

    scalerParameter = MinMaxScaler()
    scalerCoefficients = MinMaxScaler()

    print("[INFO] parameters...")
    print(parameters)

    scalerParameter.fit(parameters)
    scalerCoefficients.fit(coefficients)

    parameters = scalerParameter.transform(parameters)
    coefficients = scalerCoefficients.transform(coefficients)

    def create_mlp(inputDim, outputDim):   ### mean_squared_error seems working slightly better
            model = Sequential()
            model.add(Dense(inputDim, input_dim=inputDim, kernel_initializer='normal', activation='relu'))
            model.add(Dense(60, activation="relu"))
            model.add(Dense(60, activation="relu"))
            model.add(Dense(outputDim, kernel_initializer='normal'))
            ## Compile model
            #model.compile(loss='mean_squared_error', optimizer='adam')
            model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

            return model

    def train(parameters, coefficients, trainTest=False):
      trainX = parameters
      trainY = coefficients
      testX = 0
      testY = 0

      if trainTest:
        # construct a training and testing split with 75% of the data used
        # for training and the remaining 25% for evaluation
        from sklearn.model_selection import train_test_split
        print("[INFO] constructing training/testing split... (random_state)")
        #(train, test) = train_test_split(np.hstack([trainX,trainY]), test_size=0.25, random_state=42)
        (train, test) = train_test_split(np.hstack([trainX,trainY]), test_size=0.1, random_state=42)
        inputp = list(range(0,trainX.shape[1]))
        outputc = list(range(trainX.shape[1],trainX.shape[1]+trainY.shape[1]))
        trainX = train[:,inputp]
        trainY = train[:,outputc]
        testX = test[:,inputp]
        testY = test[:,outputc]

      return trainX, trainY, testX, testY

    regressor = create_mlp(parameters.shape[1], coefficients.shape[1])  ##number of parameters, coefficients

    ########
    ## train the model
    print("[INFO] training model...")
    verb = 0 #1
    nepochs = 600 #4000
    print("[INFO] verbose...", verb)
    print("[INFO] epochs...", nepochs)

    ####
    #print("[INFO] without split (trainig loss)")
    #trainX, trainY, _, _ = train(parameters, coefficients)
    ##regressor.fit(trainX, trainY, epochs=10, batch_size=2, verbose=0)
    #regressor.fit(trainX, trainY, epochs=nepochs, batch_size=1, verbose=verb)
    
    ###
    print("[INFO] with split (trainig loss and validation loss)")
    trainX, trainY, testX, testY = train(parameters, coefficients, trainTest=True)
    regressor.fit(trainX, trainY, validation_data=(testX, testY),
            epochs=nepochs, batch_size=1, verbose=verb)
    print("[INFO] parameters for the online test...")
    print(scalerParameter.inverse_transform(testX))



    # evaluate the keras model ###needs metrics=['accuracy']
    _, accuracy = regressor.evaluate(trainX, trainY)
    print('[INFO] Accuracy: %.2f' % (accuracy*100))

    collectionProblemData.SetOperatorCompressionData((regressor, scalerParameter, scalerCoefficients))  ###fit coeff and parameters with both training and testing
