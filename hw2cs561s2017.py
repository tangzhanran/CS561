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

class CNFProcessor:
    def __init__(self):
        self.m_relation = []
       # self.m_literas = []
        self.m_cnf = Sentence()
        self.m_guestnum = 0
        self.m_tablenum = 0

    # ci and cj are tuples represent clause
    #return 0 if cannot resolve or always true
    #return a tuple of resolved clause
    def __pl_resolve(self,ci,cj):
        resolvelist = []
        result = self.__remove_complement(ci,cj)
        if  result == 0:
            return 0
        resolvelist.extend(result)
        resolvelist.extend(self.__remove_complement(cj,ci))
        resolvelist.sort()
        t = tuple(resolvelist)
        return t

    # ci and cj are tuples represent clause
    # return 0 if no complement or more than 1 pair of complement
    # return a single list with remove result
    def __remove_complement(self, ci, cj):
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

    # def __tuple_negate(self, c):
    #     l = list(c)
    #     for i in range(len(l)):
    #         if l[i] < 0:
    #             l[i] = -l[i]
    #     t = tuple(l)
    #     return t

    def __listExtendWithoutDuplicate(self, lstorigin, lstnew):
        return lstorigin

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
        self.m_cnf.addLiterals(posliterals)

    def createCNF(self):
        guestnum = self.m_guestnum
        tablenum = self.m_tablenum
        for i in range(guestnum):  #creating cnf for a single guest
            tmplist = []
            for j in range(tablenum):
                for k in range(j+1, tablenum):
                    t = (-self.m_cnf.m_literals[i*tablenum+k].m_index, -self.m_cnf.m_literals[i*tablenum+j].m_index)
                    self.m_cnf.m_clause_set.add(t)
                tmplist.append(self.m_cnf.m_literals[i*tablenum+j].m_index)
            t = tuple(tmplist)
            self.m_cnf.m_clause_set.add(t)
            del tmplist
        for i in range(guestnum):   #creating cnf from relations
            for j in range(i,guestnum):
                if self.m_relation[i][j] == 1:
                    for t in range(tablenum):
                        tu1 = (-self.m_cnf.m_literals[i*tablenum+t].m_index, self.m_cnf.m_literals[j*tablenum+t].m_index)
                        tu2 = (-self.m_cnf.m_literals[j*tablenum+t].m_index, self.m_cnf.m_literals[i*tablenum+t].m_index)
                        self.m_cnf.m_clause_set.add(tu1)
                        self.m_cnf.m_clause_set.add(tu2)
                elif self.m_relation[i][j] == -1:
                    for t in range(tablenum):
                        leftliteral = -self.m_cnf.m_literals[i * tablenum + t].m_index
                        rightliteral = -self.m_cnf.m_literals[j * tablenum + t].m_index
                        if leftliteral > rightliteral:
                            tmp = leftliteral
                            leftliteral = rightliteral
                            rightliteral = tmp
                        tu = (leftliteral,rightliteral)
                        self.m_cnf.m_clause_set.add(tu)

    def PLResolution(self):
        # cnfLength = len(self.m_cnf.m_clause_set)
        clauses = self.m_cnf.m_clause_set.copy()
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
tu1 = (1,2)
tu2 = (2,1)
tu3 = (3,4)
s1 = set()
s1.add(tu1)
s1.add(tu3)
s2 = set(tu2)
print s2.issubset(s1)

processor = CNFProcessor()
processor.parseInput("Samples test cases\input5.txt")
processor.createCNF()
print processor.PLResolution()
print processor.m_relation