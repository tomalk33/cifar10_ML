from sklearn.ensemble import RandomForestClassifier as rfc
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import IncrementalPCA as IPCA
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
import numpy as np

import statistics


def rfclassifier(X, y, estimators=50, method='preprocessing',  num_features=200):
    print('Random Forest Classification using estimators', estimators)
    classifier = rfc(n_estimators=estimators)

    if method == 'pca':
        print('Performing dimensional reduction with features', num_features)
        X_train = dimensional_reduction(
            X.astype(float), y, num_features=num_features)
    else:
        print('Performing sklearn preprocessing')
        X_train = preprocessing.scale(X.astype(float))

    y_train = y
    classifier.fit(X_train, y_train)
    return classifier, X_train


def dimensional_reduction(X, y, num_features=200, batch_size=500):
    ipca = IPCA(n_components=num_features, batch_size=batch_size)
    ipca.fit(X, y)
    return ipca.transform(X)


def logistic_classifier(X, y, num_features, method):
    print('Logistic Regression with features', num_features)
    classifier = LogisticRegression()

    if method == 'pca':
        print('Performing dimensional reduction with features', num_features)
        X_train = dimensional_reduction(
            X.astype(float), y, num_features=num_features)
    else:
        print('Performing sklearn preprocessing')
        X_train = preprocessing.scale(X.astype(float))

    X_train = dimensional_reduction(
        X.astype(float), y, num_features=num_features)
    y_train = y
    classifier.fit(X_train, y_train)
    return classifier, X_train


def cnn_classifier(x_train, y_train, x_test, y_test, lr=0.0001):
    print('Performing cnn classification with learning rate', lr)
    batch_size = 32
    num_classes = 10
    epochs = 1
    data_augmentation = True

    # Data preprocessing
    # Convert class vectors to binary class matrices.
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255

    model = Sequential()

    model.add(Conv2D(32, (3, 3), padding='same',
                     input_shape=x_train.shape[1:]))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))

    # initiate RMSprop optimizer
    opt = keras.optimizers.rmsprop(lr=lr, decay=1e-6)

    # Let's train the model using RMSprop
    model.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    cnn_model = model.fit(x_train, y_train,
                          batch_size=batch_size,
                          epochs=epochs,
                          validation_data=(x_test, y_test),
                          shuffle=True)

    result = model.predict(x_test, batch_size=128)
    y_test_predicted = np.argmax(result, axis=1)
    score = model.evaluate(x_test, y_test, batch_size=32, verbose=1)

    # plot model history
    statistics.plot_cnn_stats(cnn_model)
    return model, y_test_predicted, score
