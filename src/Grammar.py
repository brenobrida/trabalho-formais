import sys
from itertools import chain, groupby, product
from operator import itemgetter
from copy import deepcopy


class Grammar:
    """
    CLASSE DE GRAMÁTICAS

    Esta classe representa gramáticas utilizadas para análise sintática.

    Atributos:
    - productions (dict): Dicionário das produções geradas por cada não-terminal.
    - nterminals (list): Lista de itens não-terminais da gramática.
    - terminals (list): Lista de itens terminais da gramática.
    - firsts (dict): Dicionário contendo o conjunto 'First' de cada item não-terminal.
    - follows (dict): Dicionário contendo o conjunto 'Follow' de cada item não-terminal.
    - tableLL (dict): Tabela de análise preditiva LL(1).
    - lrSet (list): Conjunto de itens LR(0).
    - slrActionTable (dict): Tabela de análise 'Action' SLR(1).
    - slrGOTOtable (dict): Tabela de análise 'Go To' SLR(1).
    """

    def __init__(self, productions):
        """
        PARAMETERS

        productions (dict): Dicionário contendo as produções geradas por cada não-terminal da gramática.
        """

        self.productions = productions
        self.nterminals = [y for x in productions.keys() for y in x if y[0].isupper()]
        self.terminals = [y for x in chain.from_iterable(productions.values()) for y in x if not y in self.nterminals]
        self.terminals = sorted(set(self.terminals))
        self.firsts = dict()
        self.follows = dict()
        self.tableLL = dict()
        self.lrSet = []
        self.slrActionTable = dict()
        self.slrGOTOtable = dict()

        if len(list(productions.keys())[0]) != 1:
            raise Exception('Gramática inválida!')

    def isGLC(self):
        """
        Verifica se a gramática é livre de contexto.
        """

        return all([y[0].isupper() and len(x) == 1 for x in self.productions.keys() for y in x])

    def toStr(self):
        """
        Transforma a gramática em uma string para impressão.
        """


        out = []
        for (nt, t) in self.productions.items():
            out += [f'{" ".join(nt)} -> {" | ".join(" ".join(x) for x in t)}']

        return '\n'.join(out)

    def showGrammar(self):
        """
        Imprime a gramática em formato padrão.
        """

        for (nt, t) in self.productions.items():
            print(f'{" ".join(nt)} -> {" | ".join(" ".join(x) for x in t)}')

    def generateFirstSet(self):
        """
        Gera o conjunto de 'First' para cada não-terminal da gramática.
        """

        def generateFirst(value):
            """
            Gera o conjunto de 'First' para um não-terminal específico da gramática.

            Parameters
            ----------
            value (str): O não-terminal para o qual o conjunto 'First' será gerado.
            """

            if value in self.terminals:
                return [value]

            first = []
            for prod in self.productions[(value,)]:
                if all('&' in generateFirst(p) for p in prod if p != value) or prod == ['&']:
                    first += ['&']

                for p in prod:
                    if p == value: break
                    first += [x for x in generateFirst(p) if x != '&']
                    if '&' not in generateFirst(p): break

            return sorted(set(first))

        if Grammar.removeLeftRecursion(self).productions.keys() != self.productions.keys():
            raise Exception('A gramática não pode ser recursiva à esquerda!')

        self.firsts = dict()
        for nterminal in self.nterminals:
            self.firsts[nterminal] = generateFirst(nterminal)

    def generateFollowSet(self):
        """
        Gera o conjunto de 'Follow' para cada não-terminal da gramática.
        """

        def insert(nterminal, index):
            """
            Faz a análise de determinada produção e atualiza o conjunto 'Follows' com o resultado.

            Parameters
            ----------
            nterminal (str): O não-terminal sendo analisado.
            index (int): O índice do não-terminal na produção.
            """

            if index == len(production) - 1:
                follow[nterminal] = follow.get(nterminal, []) + follow[nt]
            elif production[index + 1] in self.terminals:
                follow[nterminal] = follow.get(nterminal, []) + [production[index + 1]]
            else:
                follow[nterminal] = follow.get(nterminal, []) + [x for x in self.firsts[production[index + 1]] if
                                                                 x != '&']

                if '&' in self.firsts[production[index + 1]]:
                    insert(nterminal, index + 1)

        self.generateFirstSet()

        follow = dict.fromkeys(self.nterminals, [])
        follow[self.nterminals[0]] = ['$']
        while True:
            size = len([y for x in follow.values() for y in x])

            for ((nt,), productions) in self.productions.items():
                for production in productions:
                    for index in range(len(production)):
                        if production[index] in self.nterminals:
                            insert(production[index], index)

            for key in follow.keys():
                follow[key] = sorted(set(follow[key]))

            if len([y for x in follow.values() for y in x]) == size:
                break

        self.follows = follow

    def buildtableLL(self):
        """
        Gera a tabela de análise preditivo LL(1).
        """

        grammar = Grammar.removeLeftRecursion(Grammar.factorate(self))
        grammar.generateFollowSet()

        for nterminal in grammar.nterminals:
            if any(production == ['&'] for production in grammar.productions[(nterminal,)]):
                if set(grammar.firsts[nterminal]) & set(grammar.follows[nterminal]):
                    raise Exception('Interseção entre First e Follow não é vazia!')

        table = dict.fromkeys(product(grammar.nterminals, [x for x in grammar.terminals if x != '&'] + ['$']), '')
        for ((nt,), productions) in grammar.productions.items():
            for production in productions:
                for p in production:
                    firsts = grammar.firsts.get(p, [p])

                    if '&' in firsts:
                        for follow in grammar.follows[nt]:
                            table[(nt, follow)] = production

                    for first in [x for x in firsts if x != '&']:
                        table[(nt, first)] = production

                    if '&' not in firsts:
                        break

        grammar.tableLL = table
        return grammar

    def readInputLL(self, input):
        """
        Lê uma entrada, utilizando a tabela de análise preditivo LL(1).

        Parameters
        ----------
        input (str): O valor da entrada a ser analisada.
        """

        input = input.split()
        input += ['$']

        grammar = self
        if not self.tableLL:
            grammar = self.buildtableLL()

        stack = ['$', grammar.nterminals[0]]
        read = input.pop(0)

        while True:
            if read == stack[-1] and read == '$':
                return True
            elif read == stack[-1] and read != '$':
                stack.pop()
                read = input.pop(0)
            elif stack[-1] in grammar.nterminals and grammar.tableLL.get((stack[-1], read), ''):
                aux = grammar.tableLL[(stack.pop(), read)][::-1]
                if aux != ['&']:
                    stack += aux
            else:
                return False

    def goto(self, closure_set, value):
        """
        Computa a função 'Go To' para um determinado conjunto de itens LR(0) através de um terminal ou não-terminal.

        Parameters
        ----------
        closure_set (list): O conjunto de itens LR(0).
        value (str): O terminal ou não-terminal para computar.
        """

        items = dict()
        for (nt, production) in [(nt, production) for (nt, productions) in closure_set for production in productions]:
            index = production.index('.')

            if index != len(production) - 1 and production[index + 1] == value:
                production[index], production[index + 1] = production[index + 1], production[index]
                items[nt] = items.get(nt, []) + [production]

        return list(items.items())

    def closure(self, items):
        """
        Computa a função 'Closure' para um determinado conjunto de itens LR(0).

        Parameters
        ----------
        items (list): A lista de itens LR(0).
        """

        closure_set = items
        while True:
            size = len(closure_set)

            for production in [production for (_, productions) in closure_set for production in productions]:
                index = production.index('.')

                if index != len(production) - 1 and production[index + 1] in self.nterminals:
                    for x in [(production[index + 1], [['.'] + (x if x != ['&'] else []) for x in
                                                       self.productions[(production[index + 1],)]])]:
                        if x not in closure_set: closure_set.append(x)

            if len(closure_set) == size:
                break

        return closure_set

    def generateLRSet(self):
        """
        Gera a Coleção LR(0) Canônica para uma determinada gramática.
        """

        new_productions = {(self.nterminals[0] + '*',): [[self.nterminals[0]]]}
        new_productions.update(self.productions)

        grammar = Grammar(new_productions)
        grammar = Grammar.removeLeftRecursion(Grammar(new_productions))
        grammar.generateFollowSet()

        lrSet = [grammar.closure(
            [(grammar.nterminals[0], [['.'] + x for x in grammar.productions[(grammar.nterminals[0],)]])])]

        while True:
            size = len(lrSet)

            for item in deepcopy(lrSet):
                for value in grammar.nterminals + grammar.terminals:
                    new_closure = grammar.goto(deepcopy(item), value)
                    if new_closure:
                        new_closure = sorted(grammar.closure(deepcopy(new_closure)))
                        if new_closure not in lrSet:
                            lrSet += [new_closure]

            if size == len(lrSet):
                break

        grammar.lrSet = lrSet
        return grammar

    def buildSLRTable(self):
        """
        Constrói a tabela de análise SLR.
        """

        grammar = self.generateLRSet()
        action = dict.fromkeys(product(range(len(grammar.lrSet)), [x for x in grammar.terminals if x != '&'] + ['$']),
                               '')
        goto = dict.fromkeys(product(range(len(grammar.lrSet)), grammar.nterminals), '')
        for items in grammar.lrSet:
            for (nt, production) in [(nt, production) for (nt, productions) in items for production in productions]:
                index = production.index('.')

                if index != len(production) - 1 and production[index + 1] in grammar.terminals:
                    indexTarget = grammar.lrSet.index(
                        sorted(grammar.closure(grammar.goto(deepcopy(items), production[index + 1]))))
                    action[(grammar.lrSet.index(items), production[index + 1])] = ('S', indexTarget)
                elif index == len(production) - 1 and nt != grammar.nterminals[0]:
                    for follow in grammar.follows[nt]:
                        action[(grammar.lrSet.index(items), follow)] = ('R', (nt, production[0:-1]))
                elif index == len(production) - 1 and nt == grammar.nterminals[0]:
                    action[(grammar.lrSet.index(items), '$')] = ('acc',)

                if index != len(production) - 1 and production[index + 1] in grammar.nterminals:
                    indexTarget = grammar.lrSet.index(
                        sorted(grammar.closure(grammar.goto(deepcopy(items), production[index + 1]))))
                    goto[(grammar.lrSet.index(items), production[index + 1])] = indexTarget

        grammar.slrActionTable = action
        grammar.slrGOTOtable = goto

        return grammar

    def readInputSLR(self, input):
        """
        Lê uma entrada, utilizando a tabela de análise SLR(1).

        Parameters
        ----------
        input (str): O valor da entrada a ser analisada.
        """

        input = input.split()
        input += ['$']

        grammar = self
        if not self.slrActionTable or not self.slrGOTOtable:
            grammar = self.buildSLRTable()

        stack = [0]
        read = input.pop(0)
        while True:
            result = grammar.slrActionTable.get((stack[-1], read), '')

            if not result:
                return False
            elif result[0] == 'S':
                stack.append(result[1])
                read = input.pop(0)
            elif result[0] == 'R':
                [stack.pop() for _ in range(len(result[1][1]))]
                stack.append(grammar.slrGOTOtable[(stack[-1], result[1][0])])
            elif result[0] == 'acc':
                return True
            else:
                return False

    def saveFile(self, file):
        """
        Salva a gramática em um arquivo especificado.

        Parameters
        ----------
        file (str): O caminho do arquivo onde a gramática será salva.
        """

        original_stdout = sys.stdout
        with open(file, 'w') as f:
            sys.stdout = f
            self.showGrammar()
            sys.stdout = original_stdout

    @staticmethod
    def factorate(grammar):
        """
        Remove a ambiguidade em produções da gramática.

        Parameters
        ----------
        grammar (Grammar object): A instância de uma gramática.
        """

        def removeDirect(productions):
            """
            Remove a ambiguidade direta em produções.

            Parameters
            ----------
            productions (list): A lista de produções de um não terminal.
            """

            counter = 1
            newProductions = dict()
            for production, items in groupby(sorted(productions), itemgetter(0)):
                items = list(items)
                if len(items) > 1:
                    newProductions[(nt,)] = newProductions.get((nt,), []) + [[production, f'{nt}{counter}']]
                    newProductions[(f'{nt}{counter}',)] = newProductions.get((f'{nt}{counter}',), []) + [x[1:] or ['&']
                                                                                                       for x in items]
                    counter += 1
                else:
                    newProductions[(nt,)] = newProductions.get((nt,), []) + items
            return newProductions

        def removeIndirect(productionList, visitedNonTerminals):
            """
            Deriva produções indiretas em produções diretas.

            Parameters
            ----------
            productionList (list): A lista de produções de um não terminal.
            visitedNonTerminals (list): A lista de não terminais já visitados.
            """

            while True:
                ambiguousProductions = [prod for prod in productionList if
                      prod[0] in grammar.nterminals and prod[0] not in visitedNonTerminals]  # Produções com ambiguidade indireta
                nonAmbiguousProductions = [prod for prod in productionList if
                      prod[0] not in grammar.nterminals or prod[0] in visitedNonTerminals]  # Produções sem ambiguidade indireta
                visitedNonTerminals += [prod[0] for prod in ambiguousProductions]

                if ambiguousProductions:
                    ambiguousProductions = [([] if y == ['&'] and x[1:] else y) + x[1:] for x in ambiguousProductions for y in old_productions[(x[0],)]]
                    return removeIndirect(ambiguousProductions + nonAmbiguousProductions, visitedNonTerminals)
                else:
                    break
            return nonAmbiguousProductions

        if not grammar.isGLC():
            raise Exception('A gramática deve ser livre de contexto!')

        old_productions = grammar.productions
        counter = 0
        limit = 100
        while True:
            new_productions = dict()
            for ((nt,), productions) in old_productions.items():
                new_productions.update(removeDirect(productions))

            counter += 1
            if counter >= limit:
                raise Exception('Limite de execuções atingido! Talvez a gramática seja inerentemente ambígua...')

            if new_productions == old_productions:
                break
            else:
                old_productions = new_productions

        while True:
            new_productions = dict()
            for ((nt,), productions) in old_productions.items():
                indirect = removeDirect(removeIndirect(productions, [nt]))
                if len(indirect.keys()) > 1:
                    new_productions.update(indirect)
                else:
                    new_productions.update({(nt,): old_productions[(nt,)]})

            counter += 1
            if counter >= limit:
                raise Exception('Limite de execuções atingido! Talvez a gramática seja inerentemente ambígua...')

            if new_productions == old_productions:
                break
            else:
                old_productions = new_productions

        return Grammar(new_productions)

    @staticmethod
    def removeLeftRecursion(grammar):
        """
        Remove a recursão à esquerda em produções da gramática.

        Parameters
        ----------
        grammar (Grammar object): A instância de uma gramática.
        """

        def removeDirectLeftRecursion(productions_list):
            """
            Remove a recursão direta em produções.

            Parameters
            ----------
            productions_list (list): A lista de produções de um não terminal.
            """

            new_productions = dict()
            productions_with_recursion = [prod for prod in productions_list if
                                          nt == prod[0]]  # Produções com recursão direta à esquerda
            productions_without_recursion = [prod for prod in productions_list if nt != prod[0]]  # Produções sem recursão

            if productions_with_recursion:
                productions_with_recursion = [prod[1:] + [f'{nt}\''] for prod in productions_with_recursion] + [['&']]
                productions_without_recursion = [prod + [f'{nt}\''] for prod in productions_without_recursion] or [
                    f'{nt}\'']

            new_productions[(nt,)] = productions_without_recursion
            if productions_with_recursion:
                new_productions[(f'{nt}\'',)] = productions_with_recursion

            return new_productions

        def removeRecursion(productions, limit=100, counter=0):
            """
            Deriva recursões indiretas em recursões diretas.

            Parameters
            ----------
            productions (list): A lista de produções de um não terminal.
            limit (int, optional): O limite de execuções. Valor padrão é 100.
            counter (int, optional): O contador de execuções. Valor padrão é 0.
            """

            while True:
                productions_with_recursion = [prod for prod in productions if
                                              prod[0] in visited]  # Produções com recursão indireta
                productions_without_recursion = [prod for prod in productions if
                                                 prod[0] not in visited]  # Produções sem recursão indireta

                if counter >= limit:
                    raise Exception('Limite de execuções atingido! Talvez a gramática seja inerentemente recursiva...')

                if productions_with_recursion:
                    productions_with_recursion = [(y if y != ['&'] else []) + x[1:] for x in productions_with_recursion
                                                  for y in new_productions[(x[0],)]]
                    return removeRecursion(productions_with_recursion + productions_without_recursion, limit,
                                              counter + 1)
                else:
                    break

            return productions_without_recursion

        if not grammar.isGLC():
            raise Exception('A gramática deve ser livre de contexto!')

        visited = []
        new_productions = dict()
        for ((nt,), productions) in grammar.productions.items():
            new_productions.update(removeDirectLeftRecursion(removeRecursion(productions)))
            visited.append(nt)

        return Grammar(new_productions)

    @staticmethod
    def readFile(data):
        """
        Lê um arquivo e retorna uma gramática.

        Parameters
        ----------
        arquivo (str): O caminho do arquivo a ser lido.
        """

        try:
            file = open(data).readlines()
            file = [row.strip().split('->') for row in file if row[0:2] != '--']

            productions_dict = dict()
            for row in file:
                if row[0] and row[1:][0] and row[0][0:2] != '--':
                    nterminal = row[0].split()
                    terminals = row[1].split('|')
                    productions_dict[tuple(nterminal)] = productions_dict.get(tuple(nterminal), []) + [x.split() for x in
                                                                                             terminals]
        except:
            raise Exception('Arquivo inválido!')

        return Grammar(productions_dict)
