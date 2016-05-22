# -*- coding: utf-8 -*-

import os
import numpy as np
import copy
from abstract_learner import AbstractClassifier
from base.dataloader import DataLoader
from base.common_function import *
from optimizer.sgd import StochasticGradientDescent
from base.metric import accuracy_score
from loss.cross_entropy import CrossEntropy


class LogisticRegression(AbstractClassifier):
    def __init__(self, max_iter=10, batch_size=10, learning_rate=0.001, is_plot_loss=True):
        super(LogisticRegression, self).__init__()
        self._nFeat = None
        self._nClass = None
        self._label2ix = None
        self._ix2label = None
        self._lossor = CrossEntropy()

        self._batch_size = batch_size
        self._max_iter = max_iter
        self._learning_rate = learning_rate
        self._is_plot_loss = is_plot_loss

    def predict(self, X):
        assert self._is_trained, 'model must be trained before predict.'
        nSize = X.shape[0]
        proj = np.dot(X, self._parameter['weight']) + np.repeat(
            np.reshape(self._parameter['bias'], (1, self._parameter['bias'].shape[0])), X.shape[0], axis=0)
        h = sigmoid(proj)
        pred = [1 if v >= 0.5 else 0 for v in h]
        return np.array([self._ix2label[ix] for ix in pred])

    def fit(self, X, y):
        _X = copy.deepcopy(X)
        _y = copy.deepcopy(y)
        assert self.__check_valid(_X, _y), 'input is invalid.'
        if self._is_trained is False:
            self._label2ix = {label: i for i, label in enumerate(np.unique(_y))}
            self._ix2label = {i: label for i, label in enumerate(np.unique(_y))}
            self._nFeat = _X.shape[1]
            self._nClass = len(np.unique(_y))
            assert self._nClass == 2, 'class number must be 2.'
            self._parameter['weight'] = np.random.uniform(0, 0.08, (self._nFeat, 1))
            self._parameter['bias'] = np.zeros(1)
            self._grad_parameter['weight'] = np.zeros((self._nFeat, 1))
            self._grad_parameter['bias'] = np.zeros(1)
        _y = np.array([self._label2ix[label] for label in _y])
        nSize = _X.shape[0]
        assert nSize >= self._batch_size, 'batch size must less or equal than X size.'
        optimizer = StochasticGradientDescent(learning_rate=self._learning_rate, batch_size=self._batch_size,
                                              max_iter=self._max_iter, epoches_per_plot=100)
        optimizer.run(feval=self.feval, X=_X, y=_y, parameter=self._parameter)
        self._is_trained = True

    def __check_valid(self, X, y):
        if self._is_trained is False:
            return True
        else:
            is_valid = False
            nFeat = X.shape[1]
            nClass = len(np.unique(y))
            if nFeat == self._nFeat and nClass == self._nClass:
                is_valid = True
            return is_valid

    def feval(self, parameter, X, y):
        y = np.reshape(y, (y.shape[0], 1))
        nSize = X.shape[0]
        proj = np.dot(X, parameter['weight']) + np.repeat(
            np.reshape(parameter['bias'], (1, parameter['bias'].shape[0])), X.shape[0], axis=0)
        h = sigmoid(proj)
        loss = self._lossor.calculate(y, h)
        residual = h - y
        self._grad_parameter['weight'] = 1. / nSize * np.dot(X.T, residual)
        self._grad_parameter['bias'] = 1. / nSize * np.sum(residual)
        return loss, self._grad_parameter


if __name__ == '__main__':
    path = os.getcwd() + '/../dataset/electricity-normalized.arff'
    loader = DataLoader(path)
    dataset = loader.load(target_col_name='Class')
    trainset, testset = dataset.cross_split()
    lr = LogisticRegression(max_iter=2000, batch_size=100, learning_rate=0.01, is_plot_loss=True)
    lr.fit(trainset[0], trainset[1])
    predict = lr.predict(testset[0])
    acc = accuracy_score(testset[1], predict)
    print 'test accuracy:', acc
    lr.dump('LR.model')
    # lr = LogisticRegression.load('LR.model')
    # predict = lr.predict(testset[0])
    # print accuracy_score(testset[1], predict)
