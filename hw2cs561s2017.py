import random

class Litera:
    def __init__(self, i, g=0, t=0, s=1, v=True):
        self.m_index = i
        self.m_value = v
        self.m_symbol = s
        self.m_guest = g
        self.m_table = t

    def equal(self, literal):   #return true if literal has same number
        if self.m_guest == literal.m_guest and self.m_table == literal.m_table:
            return True
        return False

    def isComplement(self, literal):    #return true if literals are complement
        if self.m_index == literal.m_index and self.m_symbol == 1-literal.m_symbol:
            return True
        return False

class Clause:
    def __init__(self, literas):
        self.m_litera_tuple = literas

class Sentence:
    def __init__(self):
        self.m_clause_set = set()   #set of tuples with literal index
        self.m_literals = []    #all literals
        #self.m_neg_literals = []    #all negated literals

    def addLiterals(self, literals):    #literals is a list of literal
        self.m_literals = literals[:]
        #self.m_neg_literals.append(negliterals)

class Model:
    def __init__(self, m):
        self.truth_list = m[:]
        self.max_satisdied = 0
        self.falselist = []

    def isModelSatisfied(self, sentence):
        cnflist = list(sentence.m_clause_set)
        for ci in cnflist:
            flag = False
            for li in ci:
                if ((self.truth_list[abs(li)-1]) and (li > 0)) or ((not(self.truth_list[abs(li)-1])) and (li < 0)):
                    flag = True
                    break
            if not flag:
                self.falselist.append(ci)
            else:
                self.max_satisdied += 1
        if self.max_satisdied == len(cnflist):
            return True
        return False

    def selectFalseClause(self):
        index = random.randint(0,len(self.falselist)-1)
        return self.falselist[index]

    def flipSymbol(self,clause):
        clauselength = len(clause)
        i = random.randint(0,clauselength-1)
        index = abs(clause[i])-1
        self.truth_list[index] = not self.truth_list[index]

    def flipMaximize(self,clause, sentence):
        # flip whichever symbol in clause maximizes the number of clauses in sentence
        # return true if all clauses are satisfied after any single flip
        # return false if some clauses remain false
        truthlist = self.truth_list[:]
        cnflist = list(sentence.m_clause_set)
        for li in clause:
            countsatisfied = 0
            truthlist[abs(li)-1] = not truthlist[abs(li)-1]
            for ci in cnflist:
                for sli in ci:
                    if ((truthlist[abs(sli)-1]) and (sli > 0)) or ((not(truthlist[abs(sli)-1])) and (sli < 0)):
                        countsatisfied += 1
                        break
            if countsatisfied == len(cnflist):
                self.truth_list = truthlist[:]
                return True
            if countsatisfied > self.max_satisdied:
                max_satisdied = countsatisfied
                self.truth_list = truthlist[:]
            truthlist[abs(li)-1] = not truthlist[abs(li)-1]
        return False

class CNFProcessor:
    def __init__(self):
        self.m_relation = []
       # self.m_literas = []
        self.__m_cnf = Sentence()
        self.m_guestnum = 0
        self.m_tablenum = 0

    def __pl_resolve(self,ci,cj):
        # ci and cj are tuples represent clause
        # return 0 if cannot resolve or always true
        # return a tuple of resolved clause
        resolvelist = []
        result = self.__remove_complement(ci,cj)
        if  result == 0:
            return 0
        resolvelist.extend(result)
        resolvelist.extend(self.__remove_complement(cj,ci))
        resolvelist.sort()
        t = tuple(resolvelist)
        return t

    def __remove_complement(self, ci, cj):
        # ci and cj are tuples represent clause
        # return 0 if no complement or more than 1 pair of complement
        # return a single list with remove result
        uniqci = tuple(set(ci))
        uniqcj = tuple(set(cj))
        clauselist = []
        count = 0
        flag = True
        for li in uniqci:
            for lj in uniqcj:
                if li+lj == 0:
                    flag = False
                    count += 1
                    break
            if flag:
                clauselist.append(li)
            if count > 1:
                break
            flag = True
        if count != 1:
            return 0
        return clauselist

    def parseInput(self, input_path):
        file = open(input_path)
        lines = file.readlines()
        numbers = lines[0].split()
        self.m_guestnum = int(numbers[0])
        self.m_tablenum = int(numbers[1])
        self.m_relation = [[0 for i in range(self.m_guestnum)] for i in range(self.m_guestnum)]
        for i in range(1,len(lines)):
            relate = lines[i].split()
            if (len(relate) != 3):
                continue
            if relate[2] == 'F':
                self.m_relation[int(relate[0])-1][int(relate[1])-1] = 1
                self.m_relation[int(relate[1])-1][int(relate[0])-1] = 1
            elif relate[2] == 'E':
                self.m_relation[int(relate[0])-1][int(relate[1])-1] = -1
                self.m_relation[int(relate[1])-1][int(relate[0])-1] = -1
        posliterals = []
        #negliterals = []
        index = 1
        for i in range(self.m_guestnum):
            for j in range(self.m_tablenum):
                l = Litera(index,i+1,j+1,1,True)
                posliterals.append(l)
                index += 1
        self.__m_cnf.addLiterals(posliterals)

    def createCNF(self):
        guestnum = self.m_guestnum
        tablenum = self.m_tablenum
        for i in range(guestnum):  #creating cnf for a single guest
            tmplist = []
            for j in range(tablenum):
                for k in range(j+1, tablenum):
                    t = (-self.__m_cnf.m_literals[i*tablenum+k].m_index, -self.__m_cnf.m_literals[i*tablenum+j].m_index)
                    self.__m_cnf.m_clause_set.add(t)
                tmplist.append(self.__m_cnf.m_literals[i*tablenum+j].m_index)
            t = tuple(tmplist)
            self.__m_cnf.m_clause_set.add(t)
            del tmplist
        for i in range(guestnum):   #creating cnf from relations
            for j in range(i,guestnum):
                if self.m_relation[i][j] == 1:
                    for t in range(tablenum):
                        tu1 = (-self.__m_cnf.m_literals[i*tablenum+t].m_index, self.__m_cnf.m_literals[j*tablenum+t].m_index)
                        tu2 = (-self.__m_cnf.m_literals[j*tablenum+t].m_index, self.__m_cnf.m_literals[i*tablenum+t].m_index)
                        self.__m_cnf.m_clause_set.add(tu1)
                        self.__m_cnf.m_clause_set.add(tu2)
                elif self.m_relation[i][j] == -1:
                    for t in range(tablenum):
                        leftliteral = -self.__m_cnf.m_literals[i * tablenum + t].m_index
                        rightliteral = -self.__m_cnf.m_literals[j * tablenum + t].m_index
                        if leftliteral > rightliteral:
                            tmp = leftliteral
                            leftliteral = rightliteral
                            rightliteral = tmp
                        tu = (leftliteral,rightliteral)
                        self.__m_cnf.m_clause_set.add(tu)

    def PLResolution(self):
        # cnfLength = len(self.m_cnf.m_clause_set)
        clauses = self.__m_cnf.m_clause_set.copy()
        newClauses = list()
        clauseslist = list(clauses)
        while True:
            cnfLength = len(clauseslist)
            print "Clauses Length: " + `cnfLength`
            for i in range(cnfLength-1):
                for j in range(i+1,cnfLength):
                    t = self.__pl_resolve(clauseslist[i],clauseslist[j])
                    if t == 0:
                        continue
                    if len(t) == 0:
                        return False
                    newClauses.append(t)
            tmpclauseset = set(clauseslist)
            tmpnewclauseset = set(newClauses)
            if tmpnewclauseset.issubset(tmpclauseset):
                return True
            clauseslist.extend(list(tmpnewclauseset))
            #clauseslist = list(set(clauseslist))

    def WalkSAT(self, max_flips, p=0.5):
        numofliterals = len(self.__m_cnf.m_literals)
        modellist = [True for i in range(numofliterals)]
        model = Model(modellist)
        for i in range(max_flips):
            if model.isModelSatisfied(self.__m_cnf):
                return model
            clause = model.selectFalseClause()
            pro = random.random()
            if pro <= p:
                #flip symbol
                model.flipSymbol(clause)
            else:
                #flip a symbol maximize the number of satisfied clauses
                if model.flipMaximize(clause,self.__m_cnf):
                    return model
        return False

    def getCNF(self):
        return self.__m_cnf

processor = CNFProcessor()
processor.parseInput("Samples test cases\input6.txt")
processor.createCNF()
if processor.PLResolution():
    print "yes"
    model = processor.WalkSAT(10000,0.5)
    if model != False:
        literals = processor.getCNF().m_literals
        for i in range(len(model.truth_list)):
            if model.truth_list[i]:
                print `literals[i].m_guest` + " " + `literals[i].m_table`
else:
    print "no"