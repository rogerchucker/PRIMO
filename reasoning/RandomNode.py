# -*- coding: utf-8 -*-

from core.Node import Node
from reasoning.AbstractCPD import AbstractCPD


class RandomNode(Node):
    '''TODO: write doc'''

    cpd = AbstractCPD()

    def __init__(self):
        super(RandomNode, self).__init__()