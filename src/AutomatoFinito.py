import sys
import itertools
from tabulate import tabulate


class AutomatoFinito:
    # classe dos autômatos finitos:

    # states: lista de estados do autômato
    # transitions: dicionário de transições do autômato
    # initial: estado inicial
    # final: lista de estados de aceitação

    def __init__(self, states, transitions, initial, final):
        # states: lista de estados do autômato
        # transitions: dicionário de transições do autômato
        # initial: estado inicial
        # final: lista de estados de aceitação

        if not all([x in states for x in set(itertools.chain(*transitions))]):
            raise Exception("Transições entre estados inexistentes não são permitidas!")
        if not initial in states:
            raise Exception("Estado inicial não encontrado!")
        if not all(x in states for x in final):
            raise Exception("Estado(s) de aceitação não encontrado(s)!")

        self.states = states
        self.transitions = transitions
        self.initial = initial
        self.final = final
        self.terminals = sorted(set(itertools.chain(*transitions.values())))

    def nextState(self, state, terminal):
        # Retorna os possíveis próximos estados, a partir de um terminal

        # state: estado atual
        # terminal: símbolo terminal

        return [
            ns
            for (cs, ns), x in self.transitions.items()
            if cs == state and terminal in x
        ]

    def isNonDeterministic(self):
        # Verifica se o autômato é não-determinístico

        if "&" in self.terminals:
            return True

        for state, terminal in itertools.product(self.states, self.terminals):
            aux = self.nextState(state, terminal)
            if len(aux) > 1:
                return True

        return False

    def tableAutomata(self):
        # Retorna o autômato em formato de tabela de transições

        data = dict.fromkeys(self.terminals)

        if not data:
            raise Exception("Autômato vazio!")

        for terminal in self.terminals:
            data[terminal] = [
                ", ".join(map(str, self.nextState(state, terminal))).strip() or "-"
                for state in self.states
            ]

        index = len(self.states) * [""]
        for i in range(len(self.states)):
            if self.states[i] == self.initial:
                index[i] += "-> "
            if self.states[i] in self.final:
                index[i] += "* "
            index[i] += str(self.states[i])

        return tabulate(
            data,
            headers="keys",
            showindex=index,
            tablefmt="presto",
            colalign=("right",),
        )

    def printAutomata(self):
        # Imprime o autômato em formato de tabela de transições

        print(self.tableAutomata())

    def printFile(self, arquivo):
        # Imprime, em um arquivo, o autômato em formato de tabela de transições

        # arquivo: caminho do arquivo

        original_stdout = sys.stdout
        with open(arquivo, "w") as f:
            sys.stdout = f
            self.printAutomata()
            sys.stdout = original_stdout

    def saveFile(self, arquivo):
        # Salva o autômato finito em um arquivo especificado

        # arquivo: caminho do arquivo

        original_stdout = sys.stdout
        with open(arquivo, "w") as f:
            sys.stdout = f

            print("*states", len(self.states))
            print("*initial", self.initial)
            print("*final", *self.final)
            print("*transitions")
            for (fonte, destino), transition in self.transitions.items():
                print(str(fonte) + " > " + str(destino) + " | ", end="")
                print(*transition)

            sys.stdout = original_stdout

    @staticmethod
    def removeUnreachable(AutomatoFinito):
        # Remove estados inalcançáveis de um autômato finito

        # AutomatoFinito: instância de um autômato finito

        def private(state, visited):
            # Através de recursão, retorna os estados alcançáveis do autômato

            # state: estado inicial para realizar a busca
            # visited: lista de estados já visitados pelo algoritmo

            visited.append(state)
            [
                private(destino, visited)
                for (fonte, destino) in AutomatoFinito.transitions.keys()
                if fonte == state and destino not in visited
            ]
            return sorted(visited)

        new_states = private(AutomatoFinito.initial, [])
        new_transitions = dict(
            [
                ((fonte, destino), value)
                for ((fonte, destino), value) in AutomatoFinito.transitions.items()
                if fonte in new_states and destino in new_states
            ]
        )

        return AutomatoFinito(
            new_states,
            new_transitions,
            AutomatoFinito.initial,
            [state for state in AutomatoFinito.final if state in new_states],
        )

    @staticmethod
    def removeDead(AutomatoFinito):
        # Remove estados mortos de um autômato finito

        # AutomatoFinito: instância de um autômato finito

        def private(states, visited):
            # Através de recursão, retorna os estados não mortos do autômato

            # states: lista de estados para realizar a busca
            # visited: lista de estados já visitados pelo algoritmo

            if states:
                visited += list(set(states))
                private(
                    [
                        fonte
                        for (fonte, destino) in AutomatoFinito.transitions.keys()
                        if destino in states and fonte not in visited
                    ],
                    visited,
                )
            return sorted(set(visited))

        new_states = private(AutomatoFinito.final, [])
        new_transitions = dict(
            [
                ((fonte, destino), value)
                for ((fonte, destino), value) in AutomatoFinito.transitions.items()
                if fonte in new_states and destino in new_states
            ]
        )

        return AutomatoFinito(
            new_states,
            new_transitions,
            AutomatoFinito.initial,
            [state for state in AutomatoFinito.final if state in new_states],
        )

    @staticmethod
    def equivalenceClasses(AutomatoFinito):
        # Remove estados com mesma classe de equivalência de um autômato finito

        # AutomatoFinito: instância de um autômato finito

        def getKey(state, classes):
            # Retorna a classe de determinado estado

            # state: estado do autômato
            # classes: dicionário de classes do autômato

            for key, value in classes.items():
                if state in value:
                    return key

        def private(classes):
            # Através de recursão, separa os estados do autômato em classes de equivalência

            # classes: dicionário de classes do autômato

            new_classes = dict()
            new_classes_dict = dict()
            for state in AutomatoFinito.states:
                aux = [
                    x
                    for terminal in AutomatoFinito.terminals
                    for x in sorted(AutomatoFinito.nextState(state, terminal)) or [0]
                ]
                index = str(
                    [getKey(state, classes)] + [getKey(x, classes) or 0 for x in aux]
                )
                new_classes_dict[index] = sorted(
                    new_classes_dict.get(index, []) + [state]
                )
            for i in range(1, len(new_classes_dict) + 1):
                new_classes[i] = new_classes_dict[list(new_classes_dict.keys())[i - 1]]
            return (
                new_classes
                if len(new_classes) == len(classes)
                else private(new_classes)
            )

        classes = private(
            {
                1: set(AutomatoFinito.states) ^ set(AutomatoFinito.final),
                2: AutomatoFinito.final,
            }
        )

        new_transitions = dict()
        for (fonte, destino), value in AutomatoFinito.transitions.items():
            fonte = getKey(fonte, classes)
            destino = getKey(destino, classes)
            new_transitions[(fonte, destino)] = (
                new_transitions.get((fonte, destino), []) + value
            )

        return AutomatoFinito(
            list(classes.keys()),
            new_transitions,
            getKey(AutomatoFinito.initial, classes),
            [getKey(final, classes) for final in AutomatoFinito.final],
        )

    @staticmethod
    def minimize(AutomatoFinito):
        # Faz a minimização de estados de um autômato finito

        # AutomatoFinito: instância de um autômato finito

        return AutomatoFinito.equivalenceClasses(
            AutomatoFinito.removeDead(AutomatoFinito.removeUnreachable(AutomatoFinito))
        )

    @staticmethod
    def union(AF1, AF2):
        # Faz a união de dois autômatos finitos

        # AF1: instância de um autômato finito
        # AF2: instância de um autômato finito

        total = len(AF1.states) + 1

        nv = [total] + [x + total for x in AF2.states]
        nf = [x + total for x in AF2.final]
        nt = dict(
            zip(
                [(x + total, y + total) for (x, y) in AF2.transitions.keys()],
                AF2.transitions.values(),
            )
        )
        nt[(total, AF1.initial)] = ["&"]
        nt[(total, AF2.initial + total)] = ["&"]
        nt.update(AF1.transitions)

        return AutomatoFinito(AF1.states + nv, nt, total, AF1.final + nf)

    @staticmethod
    def intersection(AF1, AF2):
        # Faz a intersecção, por meio do produto cartesiano, de dois autômatos finitos

        # AF1: instância de um autômato finito
        # AF2: instância de um autômato finito

        new_states = list(itertools.product(AF1.states, AF2.states))
        new_states_dict = dict(zip(new_states, range(1, len(new_states) + 1)))
        new_initial = new_states_dict[(AF1.initial, AF2.initial)]
        new_final = [
            new_states_dict[(final_af1, final_af2)]
            for final_af1 in AF1.final
            for final_af2 in AF2.final
        ]

        new_transitions = dict()
        for state1, state2 in new_states:
            for terminal in set(AF1.terminals + AF2.terminals):
                af1_transition = AF1.nextState(state1, terminal)
                af2_transition = AF2.nextState(state2, terminal)
                fonte = new_states_dict[(state1, state2)]

                if terminal == "&":
                    for x in af1_transition:
                        destino = new_states_dict[(x, state2)]
                        new_transitions[(fonte, destino)] = new_transitions.get(
                            (fonte, destino), []
                        ) + [terminal]
                    for x in af2_transition:
                        destino = new_states_dict[(state1, x)]
                        new_transitions[(fonte, destino)] = new_transitions.get(
                            (fonte, destino), []
                        ) + [terminal]

                elif af1_transition and af2_transition:
                    for x in list(itertools.product(af1_transition, af2_transition)):
                        destino = new_states_dict[x]
                        new_transitions[(fonte, destino)] = new_transitions.get(
                            (fonte, destino), []
                        ) + [terminal]

        return AutomatoFinito(
            range(1, len(new_states) + 1), new_transitions, new_initial, new_final
        )

    @staticmethod
    def readFile(arquivo):
      # Lê um arquivo e retorna um autômato finito

      # arquivo: caminho do arquivo

        try:
            file = open(arquivo).readlines()
            file = [row.split() for row in file]

            for row in file:
                if "*states" in row:
                    n = int(row[1])
                if "*initial" in row:
                    initial = int(row[1])
                if "*final" in row:
                    final = [int(f) for f in row[1:]]

            states = [*range(1, n + 1)]
            transitions = [x for x in file[file.index(["*transitions"]) + 1 :] if x]
            transitions = dict(
                [((int(a), int(b)), x) for a, _, b, _, *x in transitions]
            )
        except:
            raise Exception("Arquivo inválido!")

        return AutomatoFinito(states, transitions, initial, final)
