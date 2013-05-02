# -*- coding: utf-8 -*-

from primo.reasoning import RandomNode
from primo.reasoning.density import CanonicalForm


class GaussNode(RandomNode):
    '''TODO: write doc'''

    def __init__(self):
        super(GaussNode, self).__init__()
        self.cpd = CanonicalForm()
        
    def set_density_parameters(mean, var, linear):
        self.cpd.K=0
