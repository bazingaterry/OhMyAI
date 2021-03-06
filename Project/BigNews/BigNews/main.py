import json

from numpy import array, zeros, e, power
from numpy.random import random


def sigmoid(_s):
    return 1 / (1 + power(e, -_s))


class Sample(object):
    length = None

    def __init__(self, _vector, _label):
        vec = [1]
        vec.extend(_vector)
        self.vector = array(vec)
        if Sample.length is None:
            Sample.length = self.vector.size
        else:
            assert Sample.length == self.vector.size
        self.label = int(_label)


class Score(object):
    def __init__(self, _w):
        self.w = _w
        self.tp = 0
        self.fn = 0
        self.fp = 0
        self.tn = 0

    def test(self, _test_case):
        if _test_case.label == 1:
            if sigmoid(_test_case.vector.dot(self.w)) > 0.3:
                self.tp += 1
            else:
                self.fn += 1
        else:
            if sigmoid(_test_case.vector.dot(self.w)) > 0.3:
                self.fp += 1
            else:
                self.tn += 1

    @property
    def accuracy(self):
        try:
            return (self.tp + self.tn) / (self.tp + self.fp + self.tn + self.fn)
        except ZeroDivisionError:
            return 0

    @property
    def recall(self):
        try:
            return self.tp / (self.tp + self.fn)
        except ZeroDivisionError:
            return 0

    @property
    def precision(self):
        try:
            return self.tp / (self.tp + self.fp)
        except ZeroDivisionError:
            return 0

    @property
    def f1(self):
        try:
            return 2 * self.precision * self.recall / (self.precision + self.recall)
        except ZeroDivisionError:
            return 0


def read_file(data_file, train_rate):
    """
    :param data_file: json
    :param train_rate: 0-1, divide train list into train or test
    """
    _train_list = list()
    _valid_list = list()
    with open(data_file) as file:
        _data = json.load(file)
        for _sample in _data:
            if random(1) < 0.8:
                pass
            _s = Sample(_sample['line'], _sample['label'])
            if random(1) < train_rate:
                _train_list.append(_s)
            else:
                _valid_list.append(_s)
    return _train_list, _valid_list


def err(_train_list, _w):
    _delta_err = zeros(Sample.length, dtype='float64')
    for i in range(Sample.length):
        for ele in _train_list:
            _delta_err[i] += (sigmoid(ele.vector.dot(_w)) - ele.label) * ele.vector[i]
    return _delta_err


if __name__ == '__main__':
    train_list, valid_list = read_file('data/train.json', 0.8)
    w = zeros(Sample.length, dtype='float64')
    count = 0
    eta = 0.00005
    last_f1 = 0
    best_f1 = 0
    best_w = None
    while count < 300:
        w -= eta * err(train_list, w)
        count += 1
        s = Score(w)
        for v in valid_list:
            s.test(v)
        if s.f1 >= last_f1:
            eta *= 1.000001
        else:
            eta *= 0.9
        last_f1 = s.f1
        print('%d times' % count)
        print('Current eta:', eta)
        print('F1:', s.f1)
        print(s.tp, s.fp, s.fn)
        if last_f1 > best_f1:
            best_w = w.copy()
            best_f1 = last_f1
            print('w vector is: %s' % w)
            print('Accuracy:', s.accuracy)
            print('Best F1:', best_f1)
            print('\n')
