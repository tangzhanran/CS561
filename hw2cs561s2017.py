class Litera:
    def __init__(self, i, g=0, t=0, s=1, v=True):
        self.m_index = i
        self.m_value = v
        self.m_guest = g
        self.m_table = t
        self.m_symbol = s

    def equal(self, literal):   #return true if literal has same number
        if self.m_guest == literal.m_guest and self.m_table == literal.m_table:
            return True
        return False

    def isComplement(self, literal):    #return true if literals are complement
        if self.m_index == literal.m_index and self.m_symbol == 1-literal.m_symbol:
            return True
        return False

class Clause:
    def __init__(self, literas=[]):
        self.m_litera_list = literas[:]

class Sentence:
    def __init__(self, clauses=[]):
        self.m_clause_list = clauses[:]

class CNFProcessor:
    def __init__(self):
        self.m_relation = []
        self.m_literas = []
        self.m_cnf = Sentence()
        self.m_guestnum = 0
        self.m_tablenum = 0

    def __pl_resolve(self,ci,cj):
        count = 0
        set = list()
        for li in ci.m_litera_list:
            for lj in cj.m_litera_list:
                if li.equal(lj) and li.m_value != lj.m_value:
                    count += 1
                    break


    def setRelationMatrix(self, relation):
        self.m_relation = relation[:]

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
        self.m_literas = [[] for i in range(self.m_guestnum)]
        for i in range(self.m_guestnum):
            for j in range(self.m_tablenum):
                #l = Litera(i+1,j+1,0)
                #nl = Litera(i+1,j+1,1)
                self.m_literas[i].append(Litera(i+1,j+1))
                self.m_literas[i].append(Litera(i+1,j+1,False))

    def createCNF(self):
        for i in range(self.m_guestnum):  #creating cnf for a single guest
            tmplist = []
            for j in range(self.m_tablenum):
                #if j+1 < self.m_tablenum:
                for k in range(j+1, self.m_tablenum):
                    #tmplist = []
                    #tmplist.append(self.m_literas[i][2*k+1])
                    #tmplist.append(self.m_literas[i][2*k+3])
                    c = Clause()
                    c.m_litera_list.append(self.m_literas[i][2*j+1])
                    c.m_litera_list.append(self.m_literas[i][2*k+1])
                    self.m_cnf.m_clause_list.append(c)
                    #del tmplist
                tmplist.append(self.m_literas[i][2*j])
            c = Clause(tmplist)
            self.m_cnf.m_clause_list.append(c)
            del tmplist
        for i in range(self.m_guestnum):   #creating cnf from relations
            for j in range(i,self.m_guestnum):
                if self.m_relation[i][j] == 1:
                    for t in range(self.m_tablenum):
                        #tmplist = []
                        #tmplist.append(self.m_literas[i][2 * t + 1])
                        #tmplist.append(self.m_literas[j][2 * t])
                        c = Clause()
                        c.m_litera_list.append(self.m_literas[i][2 * t + 1])
                        c.m_litera_list.append(self.m_literas[j][2 * t])
                        self.m_cnf.m_clause_list.append(c)
                        #del tmplist[:]
                        #tmplist.append(self.m_literas[i][2 * t])
                        #tmplist.append(self.m_literas[j][2 * t + 1])
                        c = Clause()
                        c.m_litera_list.append(self.m_literas[i][2 * t])
                        c.m_litera_list.append(self.m_literas[j][2 * t + 1])
                        self.m_cnf.m_clause_list.append(c)
                        #del tmplist
                        #del c
                elif self.m_relation[i][j] == -1:
                    for t in range(self.m_tablenum):
                        #tmplist = []
                        #tmplist.append(self.m_literas[i][2 * t + 1])
                        #tmplist.append(self.m_literas[j][2 * t + 1])
                        c = Clause()
                        c.m_litera_list.append(self.m_literas[i][2 * t + 1])
                        c.m_litera_list.append(self.m_literas[j][2 * t + 1])
                        self.m_cnf.m_clause_list.append(c)
                        #del tmplist
                        #del c

    def PLResolution(self):
        cnfLength = len(self.m_cnf)
        clauses = self.m_cnf[:]
        newClauses = list()
        while True:
            for i in range(cnfLength-1):
                for j in range(i+1,cnfLength):

        return

a = Litera(1,2)
b = Litera(3,4)
d = Litera(5,6)

c1 = Clause()
c1.m_litera_list.append(a)
c1.m_litera_list.append(b)
c2 = Clause()
c2.m_litera_list.append(a)
c2.m_litera_list.append(b)
c3 = Clause()
c3.m_litera_list.append(a)
c3.m_litera_list.append(d)

s1 = set()
s1.add(c1)
s1.add(c3)

s2 = set()
s2.add(c2)

print s2.issubset(s1)

processor = CNFProcessor()
processor.parseInput("Samples test cases\input4.txt")
processor.createCNF()
print processor.m_relation