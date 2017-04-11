from decimal import getcontext, Decimal

class Node:
    def __init__(self, n, name="",type=0):  #chance node: type=0, decision node: type=1, utility node: type=2
        self.__node_name = name    #node name
        self.__node_type = type    #node type
        self.__node_parents = []   #node parents table, save as set of node name
        self.__node_numParents = 0 #node number of parents
        self.__node_valTable = {} #probability table for decision node, utility for utility node
        self.sortnum = n #sort number

    def getNodeName(self):
        return self.__node_name

    def getNodeType(self):
        return self.__node_type

    def getNodeParents(self):
        return self.__node_parents

    def getNodeParent(self, index):
        return self.__node_parents[index]

    def getNumofParents(self):
        return self.__node_numParents

    def getVal(self,key):
        return self.__node_valTable[key]

    def addValTable(self, key, val):
        self.__node_valTable[key] = val

    def setType(self,t):
        self.__node_type = t

    def addParent(self,p):
        self.__node_parents.append(p)
        self.__node_numParents += 1

# conditionQuery with only one outcome
class conditionQuery:

    def __init__(self, res="", con={}):
        self.__outcome = res
        self.__condition = con.copy()
    def setOutcome(self, res):
        self.__outcome = res
    def setCondition(self,con):
        self.__condition = con.copy()
    def getOutcome(self):
        return self.__outcome
    def getCondition(self):
        return self.__condition

class NetSolver:
    def __init__(self):
        self.__net_queries = [] #queries
        self.__net_nodes = {}   #all nodes
        self.__nodesNum = 0

    def readFile(self,filepath):
        infile = open(filepath,"r")
        line = infile.readline().strip('\n')
        while line:
            if line == "******":
                break
            else:
                self.__net_queries.append(line)
            line = infile.readline().strip('\n')
        nodecount = 0
        while line:
            if line == "***" or line=="******":
                line = infile.readline().strip('\n')
                if line=="":
                    break
                title = line.split('|')
                name = title[0].split()[0]
                node = Node(nodecount,name)
                nodecount += 1
                self.__net_nodes[name] = node
                if name == "utility":
                    node.setType(2)
                if len(title) == 1:
                    line = infile.readline().strip('\n')
                    if line=="decision":
                        node.setType(1)
                    else:
                        node.addValTable("+" + name,float(line))
                else:
                    parents = title[1].split()
                    for p in parents:
                        node.addParent(p)
                    for i in range(0,pow(2,node.getNumofParents())):
                        line = infile.readline().strip('\n')
                        value = line.split()
                        tag = ""
                        for j in range(1,len(value)):
                            if value[j] == "+":
                                tag += "+" + node.getNodeParent(j-1)
                            else:
                                tag += "-" + node.getNodeParent(j-1)
                        node.addValTable(tag,float(value[0]))
            line = infile.readline().strip('\n')
        self.__nodesNum = nodecount

    def __rewriteQuery(self,query):
        #query is a dictionary of query in joint form, separated by ','
        #e.g. {E:+,B:-,C:+,A:+}
        #the function return a query list
        #the queries contain only 1 outcome conditional prob with 0 or more conditions
        result_list = []
        node_list = query.keys()
        if len(node_list) == 1:
            q = conditionQuery(query[node_list[0]]+node_list[0],{})
            result_list.append(q)
            return result_list
        outcome_node = self.__getLowestNode(node_list)
        condition_dict = {}
        for i in node_list:
            if i != outcome_node:
                condition_dict[i] = query[i]
        q = conditionQuery(query[outcome_node] + outcome_node, condition_dict)
        result_list.append(q)
        result_list += self.__rewriteQuery(condition_dict)
        return result_list

    def __Enumeration_Ask(self, X, e):
        # X is a string of query variable
        # X has form of "Value"+"Name" e.g."+A"
        # e is a dictionary of evidence e.g.{E:+,B:-,C:+,A:+}
        Q = []
        val = X[0]
        name = X[1:]
        sum = 0
        exi = e.copy()
        bn = e.keys()
        bn += name
        hidden = self.__exploreHidden(bn)
        bn += hidden
        bn = list(set(bn))
        bn = self.__sortNodes(bn)
        for i in range(0,2):
            if i==0:
                exi[name] = "+"
            else:
                exi[name] = "-"
            Q.append(self.__Enumerate_All(bn[:],exi.copy()))
            sum += Q[i]
        if val == '+':
            return Q[0]/sum
        else:
            return Q[1]/sum

    def __Enumerate_All(self, node_queue, exi):
        # node_queue is a queue of unexplored node in net
        # exi is a dictionary with all evidences e.g. {E:+,B:-,C:+,A:+}
        # return a probabilty value
        if len(node_queue) == 0:
            return 1
        Y = node_queue[-1]
        node_queue.pop()
        condition = ""
        if self.__net_nodes[Y].getNumofParents() == 0:
            condition = "+" + Y
        else:
            parents = self.__net_nodes[Y].getNodeParents()
            for i in parents:
                val = exi[i]
                condition += val + i
        if Y in exi:
            if exi[Y] == '+':
                return self.__net_nodes[Y].getVal(condition) * self.__Enumerate_All(node_queue[:], exi.copy())
            else:
                return (1-self.__net_nodes[Y].getVal(condition)) * self.__Enumerate_All(node_queue[:], exi.copy())
        else:
            sum = 0
            for i in range(0,2):
                if i==0:
                    exi[Y] = '+'
                    sum += self.__net_nodes[Y].getVal(condition) * self.__Enumerate_All(node_queue[:], exi.copy())
                else:
                    exi[Y] = '-'
                    sum += (1-self.__net_nodes[Y].getVal(condition))*self.__Enumerate_All(node_queue[:],exi.copy())
            return sum

    def __sortNodes(self,nodelist):
        # nodelist is a list of node name
        sortedlist = [0 for i in range(0,self.__nodesNum)]
        for i in nodelist:
            sortedlist[self.__nodesNum-self.__net_nodes[i].sortnum-1] = i
        result = []
        for i in sortedlist:
            if i != 0:
                result += i
        return result

    def __getLowestNode(self,nodelist):
        max = float("-inf")
        maxnode = ""
        for i in nodelist:
            num = self.__net_nodes[i].sortnum
            if num > max:
                max = num
                maxnode = i
        return  maxnode

    def getNetQueries(self):
        return self.__net_queries

    def getNumofQueries(self):
        return len(self.__net_queries)

    def __exploreHidden(self,nodename):
        # return all the node which has higher level of node
        hidden_list = []
        for n in nodename:
            node = self.__net_nodes[n]
            parents = node.getNodeParents()
            for i in parents:
                hidden_list += i
                hidden = self.__exploreHidden(i)
                if len(hidden) > 0:
                    hidden_list += hidden
        return hidden_list

    def solve(self, index):
        #calculate the indexth query
        query = self.__net_queries[index].split()
        query = "".join(query)
        querylist_multi = []
        querylist_devide = []
        if query[0] == 'P':
            query = query[2:-1]
            if '|' in query:
                splitquery = query.split('|')
                dict_union = {}
                outcome = splitquery[0].split(',')
                for i in outcome:
                    dict_union[i[0:-2]] = i[-1]
                condition = splitquery[1].split(',')
                dict_condition = {}
                for i in condition:
                    dict_union[i[0:-2]] = i[-1]
                    dict_condition[i[0:-2]] = i[-1]
                querylist_multi = self.__rewriteQuery(dict_union)
                querylist_devide = self.__rewriteQuery(dict_condition)
            else:
                dict_union = {}
                outcome = query.split(',')
                for i in outcome:
                    dict_union[i[0:-2]] = i[-1]
                querylist_multi = self.__rewriteQuery(dict_union)
            nomi = 1
            denomi = 1
            for i in querylist_multi:
                nomi *= self.__Enumeration_Ask(i.getOutcome(),i.getCondition())
            for i in querylist_devide:
                denomi *= self.__Enumeration_Ask(i.getOutcome(),i.getCondition())
            return nomi/denomi


solver = NetSolver()
solver.readFile("Sample test cases\input11.txt")
for i in range(0,len(solver.getNetQueries())):
    print round(solver.solve(i),2)