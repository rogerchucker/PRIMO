# -*- coding: utf-8 -*-

import itertools
from primo.core import BayesianDecisionNetwork
from primo.decision import DecisionNode
from primo.decision import UtilityTable
from primo.reasoning import DiscreteNode

class MakeDecision(object):
    
    def __init__(self, bdn = None):
        super(MakeDecision, self).__init__()
        self.bdn = bdn
        
    def set_bdn(self, bdn):
        self.bdn = bdn
    
    def get_bdn(self):
        return self.bdn
    
    def max_sum(self, decisionNode):
        '''Implementation of the max sum Algorithm to get the best Decision (according to the MEU principle).
        maximize over decisions and summing over RandomNodes.
        This function sets the state of provided DecisionNode, so later decisions can't affect that Node
        
        Argumentlist
        decisionNode -- Decision Node on which the decision should be made
        '''
        if self.bdn == None:
            raise Exception("Bayesian Decision Network was not set!")
        
        partialOrder = self.bdn.get_partialOrdering()
        utility_nodes = self.bdn.get_all_utility_nodes()
        
        
        if not partialOrder:
            raise Exception("No partial Order was set!")
        
        if decisionNode not in partialOrder:
            raise Exception("Decision Node is not in the partial Order!")
        
        if not self.bdn.is_valid():
            raise Exception("The Bayesian Decision Network is not valid!")
        
        #Check if the Decision Nodes that are ordered before the provided Decision Node have a state
        for node in partialOrder:
            if isinstance(node, DecisionNode):
                if not decisionNode.name == node.name:
                    if node.get_state() is None:
                        raise Exception("Decision Nodes that are ordered before the provided Decision Node must have a state!")
                else:
                    break
        
        '''Run through the partialOrder in reverse. Get the last two Nodes, reduce the Random Nodes with the Decision Node 
        parent and with the decisions already made. Then multiply the cpts of the Random Nodes. Multiply the probability values 
        with the sum of the utility values and calculate the best decision (which has the MEU).
        '''
        randomNodes = self.bdn.get_all_nodes()
        future_best_decisions = []
        finish = False
        for i in range(len(partialOrder)-1, -1, -2):
            max_utility = []
            #for every decision value of the decision node
            for decValue in partialOrder[i-1].get_value_range():
                
                #if the decision already have a value then abort. The decision has already been made.
                if not partialOrder[i-1].get_state() == None:
                    finish = True
                    break
                
                cpts = []
                #reduce Random Nodes with a Decision value
                for rNode in randomNodes:
                    if partialOrder[i-1] in self.bdn.get_parents(rNode):
                        cpts.append(rNode.get_cpd_reduced([(partialOrder[i-1], decValue)]))
                    else:
                        cpts.append(rNode.get_cpd())
                
                #reduce the cpts with the future_best_decisions
                for j in range(0,len(cpts)):
                    for node,value in future_best_decisions:
                        if node in cpts[j].get_variables():
                            cpts[j] = cpts[j].reduction([(node,value)])
                
                #multiply the cpts
                jointCPT = cpts[0]
                for j in range(1,len(cpts)):
                    jointCPT = jointCPT.multiplication(cpts[j])
                
                #calculate Utility
                table = jointCPT.get_table()
                value_range_list = []
                #get every variable instantiation
                for var in jointCPT.get_variables():
                    tupleList=[]
                    for value in var.get_value_range():
                        tupleList.append((var,value))
                    if tupleList:    
                        value_range_list.append(tupleList)
                
                #get all possible assignments 
                permutationList = []
                
                if len(value_range_list) >= 2:
                    permutationList = list(itertools.product(*value_range_list))
                else:
                    permutationList = value_range_list
                
                #save the results of each probability value and the according sum of utilities
                result = []
                if len(permutationList) > 1:
                    for perm in permutationList:
                        index = jointCPT.get_cpt_index(perm)
                        value = table[index]
                        result.append(value * self.calculate_utility(perm, (partialOrder[i-1],decValue), future_best_decisions))
                else:
                    for perm in permutationList[0]:
                        index = jointCPT.get_cpt_index([perm])
                        value = table[index]
                        result.append(value * self.calculate_utility([perm], (partialOrder[i-1],decValue), future_best_decisions))
                
                #end result for this decision
                max_utility.append((decValue,sum(result)))
            
            #nothing more to do since the decision has already been made
            if finish:
                break
            
            zippedList = zip(*max_utility)
            val = max(zippedList[1])
            ind = zippedList[1].index(val)
            
            #Best Decision
            best_decision = zippedList[0][ind]
            future_best_decisions.append((partialOrder[i-1],best_decision))
            
        #the last one is the decision that we want to know about    
        return future_best_decisions[len(future_best_decisions)-1]    
    
    def calculate_utility(self, assignment, currentDecision, list_of_best_decision):
        '''Sums up the utility values
        
        Argumentlist
        assignment -- the assignment of the variables
        currentDecision -- the current decision that we want to calculate
        list_of_best_decision -- list of the decisions that are lying in the future
        '''
        utilityList=[]
        zippedAssignment = zip(*assignment)
        zippedDecisions = zip(*list_of_best_decision)
        utility_nodes = self.bdn.get_all_utility_nodes()

        for uNode in utility_nodes:
            tempList = []
            parent_nodes = self.bdn.get_parents(uNode)
            for node in parent_nodes:
                if node in zippedAssignment[0]:
                    index = zippedAssignment[0].index(node)
                    tempList.append((node,zippedAssignment[1][index]))
                elif zippedDecisions:    
                    if node in zippedDecisions[0]:
                        index = zippedDecisions[0].index(node)
                        tempList.append((node,zippedDecisions[1][index]))
                    else:
                        tempList.append(currentDecision)
                else:    
                    tempList.append(currentDecision)      
            utilityList.append(uNode.get_utility(tempList))    
        return sum(utilityList)    