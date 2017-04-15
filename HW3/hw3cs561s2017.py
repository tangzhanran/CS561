from decimal import Decimal

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

    def getValTable(self):
        return self.__node_valTable

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
        self.__exProbVal = {}
        self.__EU = {}
        self.__MEU_List = []
        self.__EU_List = []
        self.__prob_List = []

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
                        node.addValTable("+" + name,1)
                        node.addValTable("-" + name,1)
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
        infile.close()

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
        if self.__net_nodes[outcome_node].getNumofParents() == 0:
            for i in node_list:
                q = conditionQuery(query[i] + i,{})
                result_list.append(q)
            return result_list
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
        if len(e) == 0 and self.__net_nodes[name].getNumofParents() == 0:
            if self.__net_nodes[name].getNodeType() == 1:
                return 1
            else:
                if val == '+':
                    return self.__net_nodes[name].getVal("+" + name)
                else:
                    return 1-self.__net_nodes[name].getVal("+" + name)
        sum = 0
        ekeys = e.keys()
        ekeys.append(name)
        ekeys = self.__sortNodes(ekeys)
        exi = e.copy()
        bn = e.keys()
        bn += name
        hidden = self.__exploreHidden(bn)
        bn += hidden
        bn = list(set(bn))
        bn = self.__sortNodes(bn)
        countdict = self.__countParentTimes(bn)
        for i in range(0,2):
            if i==0:
                exi[name] = "+"
            else:
                exi[name] = "-"
            Q.append(self.__Enumerate_All(bn[:],exi.copy(),ekeys[:], [], countdict.copy()))
            sum += Q[i]
        if val == '+':
            return Q[0]/sum
        else:
            return Q[1]/sum

    def __Enumerate_All(self, node_queue, exi, e, newevis, countdict):
        # node_queue is a list of unexplored node in net
        # exi is a dictionary with all evidences e.g. {E:+,B:-,C:+,A:+}
        # e is a list of original evidences
        # newevis is a list of new evidences variable added during calls
        # countdict is a dictionary shows how much time each node appeared as parent
        # return a probabilty value
        if len(node_queue) == 0:
            return 1
        Y = node_queue[-1]
        node_queue.pop()
        tag = "".join(node_queue)
        for keys in e:
            tag += exi[keys]+keys
        condition = ""
        if self.__net_nodes[Y].getNumofParents() == 0:
            condition = "+" + Y
        else:
            parents = self.__net_nodes[Y].getNodeParents()
            for i in parents:
                val = exi[i]
                condition += val + i
            count = len(newevis)
            index = 0
            for times in range(0,count):
                if newevis[index][1:] in parents:
                    countdict[newevis[index][1:]] -= 1
                    if countdict[newevis[index][1:]] <= 0:
                        del newevis[index]
                    else:
                        index += 1
                else:
                    index += 1
        if len(newevis) > 0:
            tag += "".join(newevis)
        enumprob = 0
        if Y in exi:
            if self.__exProbVal.has_key(tag):
                enumprob = self.__exProbVal[tag]
            else:
                enumprob = self.__Enumerate_All(node_queue[:], exi.copy(), e[:], newevis, countdict)
                self.__exProbVal[tag] = enumprob
            if self.__net_nodes[Y].getNodeType() == 1:
                return enumprob
            if exi[Y] == '+':
                return self.__net_nodes[Y].getVal(condition) * enumprob
            else:
                return (1-self.__net_nodes[Y].getVal(condition)) * enumprob
        else:
            sum = 0
            for i in range(0,2):
                if i==0:
                    postag = tag
                    posnewevis = newevis[:]
                    poscountdict = countdict.copy()
                    exi[Y] = '+'
                    posnewevis.append('+'+Y)
                    postag += "+" + Y
                    if self.__exProbVal.has_key(postag):
                        enumprob = self.__exProbVal[postag]
                    else:
                        enumprob = self.__Enumerate_All(node_queue[:], exi.copy(), e[:], posnewevis, poscountdict)
                        self.__exProbVal[postag] = enumprob
                    sum += self.__net_nodes[Y].getVal(condition) * enumprob
                else:
                    negtag = tag
                    negnewevis = newevis[:]
                    negcountdict = countdict.copy()
                    exi[Y] = '-'
                    negnewevis.append('-' + Y)
                    negtag += "-" + Y
                    if self.__exProbVal.has_key(negtag):
                        enumprob = self.__exProbVal[negtag]
                    else:
                        enumprob = self.__Enumerate_All(node_queue[:], exi.copy(),e[:], negnewevis, negcountdict)
                        self.__exProbVal[negtag] = enumprob
                    sum += (1-self.__net_nodes[Y].getVal(condition)) * enumprob
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

    def solve(self, index, ofile):
        #calculate the indexth query
        query = self.__net_queries[index].split()
        query = "".join(query)
        querylist_multi = []
        querylist_devide = []
        if query[0] == 'P':
            query = query[2:-1]
            result = self.__generateQueries(query)
            if len(result) == 0:
                return 0
            querylist_multi = result[0][:]
            if len(result) > 1:
                querylist_devide = result[1][:]
            if index == len(self.__net_queries)-1:
                ofile.write(str('{:.2f}'.format(Decimal(self.__calProb(querylist_multi,querylist_devide)))))
            else:
                ofile.write(str('{:.2f}'.format(Decimal(self.__calProb(querylist_multi, querylist_devide))))+"\n")
        elif query[0] == 'E':
            query = query[3:-1]
            eu = self.__calEU(query)
            self.__EU[query] = eu
            # self.__EU_List.append(round(eu))
            if index == len(self.__net_queries) - 1:
                ofile.write(str(int(round(eu))))
            else:
                ofile.write(str(int(round(eu))) + "\n")
        else:
            query = query[4:-1]
            splitquery = query
            con = ""
            if '|' in query:
                splitquery = query.split('|')
                con = splitquery[1]
                splitquery = splitquery[0]
            splitquery = splitquery.split(',')
            vartab = [[] for k in range(len(splitquery))]
            dim = 0
            for var in splitquery:
                for i in range(0,2):
                    if i == 0:
                        vartab[dim].append(var+"=+")
                    else:
                        vartab[dim].append(var+"=-")
                dim += 1
            eutab = []
            eusign = []
            for i in range(0,pow(2,dim)):
                euquery = ""
                querysign = ""
                for j in range(0,len(vartab)):
                    euquery += vartab[j][(pow(2,j)&i)/pow(2,j)]+","
                    querysign += euquery[-2]+" "
                euquery = euquery[:-1]
                eusign.append(querysign)
                if len(con) > 0:
                    euquery += "|" + con
                if self.__EU.has_key(euquery):
                    eutab.append(self.__EU[euquery])
                else:
                    eu = self.__calEU(euquery)
                    eutab.append(eu)
                    self.__EU[euquery] = eu
            meu = max(eutab)
            indexmeu = eutab.index(meu)
            output = eusign[indexmeu] + str(int(round(meu)))
            if index == len(self.__net_queries) - 1:
                ofile.write(output)
            else:
                ofile.write(output + "\n")

    def __generateQueries(self,query):
        # get nominate and denominate queries from query
        # return a list of multi and divide
        result = []
        if '|' in query:
            splitquery = query.split('|')
            dict_union = {}
            outcome = splitquery[0].split(',')
            for i in outcome:
                dict_union[i[0:-2]] = i[-1]
            condition = splitquery[1].split(',')
            dict_condition = {}
            for i in condition:
                if dict_union.has_key(i[0:-2]):
                    if i[-1] != dict_union[i[0:-2]]:
                        return []
                dict_union[i[0:-2]] = i[-1]
                dict_condition[i[0:-2]] = i[-1]
            querylist_multi = self.__rewriteQuery(dict_union)
            querylist_devide = self.__rewriteQuery(dict_condition)
            result.append(querylist_multi)
            result.append(querylist_devide)
        else:
            dict_union = {}
            outcome = query.split(',')
            for i in outcome:
                if dict_union.has_key(i[0:-2]):
                    if i[-1] != dict_union[i[0:-2]]:
                        return []
                dict_union[i[0:-2]] = i[-1]
            querylist_multi = self.__rewriteQuery(dict_union)
            result.append(querylist_multi)
        return result

    def __calProb(self,multi,div):
        # multi is a list of multiply query
        # div is a list of divided query
        # return probability
        nomi = 1
        denomi = 1
        for i in multi:
            nomi *= self.__Enumeration_Ask(i.getOutcome(), i.getCondition())
        for i in div:
            denomi *= self.__Enumeration_Ask(i.getOutcome(), i.getCondition())
        return nomi / denomi

    def __changeFormat(self,str):
        result = ""
        sign = str[0]
        for c in str[1:]:
            if c == '+' or c == '-':
                result += "="+sign+","
                sign = c
                continue
            else:
                result += c
        result += "="+sign+","
        return result

    def __calEU(self,query):
        vallist = self.__net_nodes['utility'].getValTable().keys()
        eu = 0
        querylist_multi = []
        querylist_devide = []
        for val in vallist:
            outcome = self.__changeFormat(val) + query
            result = self.__generateQueries(outcome)
            if len(result) == 0:
                continue
            querylist_multi = result[0][:]
            if len(result) > 1:
                querylist_devide = result[1][:]
            eu += self.__calProb(querylist_multi, querylist_devide) * self.__net_nodes['utility'].getVal(val)
        return eu

    def __countParentTimes(self,nodelist):
        # Count how many times each node in nodelist appears as parents
        # return a dictionary of times
        result_dict = {}
        for node in nodelist:
            result_dict[node] = 0
        for node in nodelist:
            parents = self.__net_nodes[node].getNodeParents()
            for p in parents:
                result_dict[p] += 1
        return result_dict

solver = NetSolver()
solver.readFile("Sample test cases\input12.txt")
ofile = open("output.txt", "w")
for i in range(0,len(solver.getNetQueries())):
    solver.solve(i,ofile)
ofile.close()