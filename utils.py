
import mxnet as mx
from mxnet import nd, autograd, gluon
import numpy as np
import json
from collections import defaultdict
import os

def cal_cos(grad_1, grad_2):
    return nd.dot(grad_1, grad_2)/(nd.norm(grad_1) + 1e-9) / (nd.norm(grad_2) + 1e-9)


def median_grad(gradients):
    param_list = [nd.concat(*[xx.reshape((-1, 1))
                            for xx in x], dim=0) for x in gradients]
    sorted_arr = nd.sort(nd.concat(*param_list, dim=1), axis=-1)
    median_idx = sorted_arr.shape[-1] // 2
    if sorted_arr.shape[-1] % 2 == 0:
        # if the number of elements is even, take the average of the two middle elements
        median = mx.nd.mean(sorted_arr[:,median_idx-1:median_idx], axis=-1)
    else:
        # if the number of elements is odd, take the middle element
        median = mx.nd.take(sorted_arr, median_idx, axis=-1)


    return median


def read_dir(data_dir):
    clients = []
    groups = []
    data = defaultdict(lambda: None)

    files = os.listdir(data_dir)
    files = [f for f in files if f.endswith('.json')]
    for f in files:
        file_path = os.path.join(data_dir, f)
        with open(file_path, 'r') as inf:
            cdata = json.load(inf)
        clients.extend(cdata['users'])
        if 'hierarchies' in cdata:
            groups.extend(cdata['hierarchies'])
        data.update(cdata['user_data'])

    clients = list(sorted(data.keys()))
    return clients, groups, data


def read_data(train_data_dir, test_data_dir):
    """Parses data in given train and test data directories
    assumes:
    - the data in the input directories are .json files with
        keys 'users' and 'user_data'
    - the set of train set users is the same as the set of test set users

    Return:
        clients: list of client ids
        groups: list of group ids; empty list if none found
        train_data: dictionary of train data
        test_data: dictionary of test data
    """
    train_clients, train_groups, train_data = read_dir(train_data_dir)
    test_clients, test_groups, test_data = read_dir(test_data_dir)

    assert train_clients == test_clients
    assert train_groups == test_groups

    return train_clients, train_groups, train_data, test_data
