import itertools
from AutomatoFinito import AutomatoFinito


class NonDeterministic(AutomatoFinito):
    # Uma classe usada para representar autômatos finitos não-determinísticos

    # Extends
    # classe AutomatoFinito

    # states: lista com os estados do autômato
    # transitions: dicionário de transições do autômato
    # initial: estado inicial
    # final: lista de estados de aceitação

    def __init__(self, AutomatoFinito):
        # AutomatoFinito: instância de um autômato finito

        super().__init__(
            AutomatoFinito.states,
            AutomatoFinito.transitions,
            AutomatoFinito.initial,
            AutomatoFinito.final,
        )

        if not super().isNonDeterministic():
            raise Exception("O autômato é determinístico!")

    def calculateEpsilon(self, state):
        # Calcula o ε-fecho de determinado estado

        # state: estado

        return [state] + list(
            itertools.chain(
                *[
                    self.calculateEpsilon(x)
                    for x in self.nextState(state, "&")
                    if x != state
                ]
            )
        )

    def readEntry(self, input):
        # Verifica se o autômato reconhece determinada cadeia de entrada

        # input: cadeia de caracteres de entrada

        fecho = dict(
            zip(self.states, [self.calculateEpsilon(state) for state in self.states])
        )

        cs = fecho[self.initial]
        for t in input:
            cs = [y for state in cs for x in self.nextState(state, t) for y in fecho[x]]

        return any([x in self.final for x in cs])

    def toDeterministic(self):
        # Converte o autômato finito não-determinístico para um autômato finito determinístico

        from Deterministic import Deterministic

        fecho = dict(
            zip(self.states, [self.calculateEpsilon(state) for state in self.states])
        )

        new_states = {str(fecho[self.initial]): 1}
        new_transitions = dict()
        new_final = []
        count = 1

        current_states = [fecho[self.initial]]
        for states in current_states:
            for terminal in [t for t in self.terminals if t != "&"]:
                aux = sorted(
                    set(
                        [
                            y
                            for state in states
                            for x in self.nextState(state, terminal)
                            for y in fecho[x]
                        ]
                    )
                )
                if aux not in current_states:
                    count += 1
                    new_states[str(aux)] = count

                    if any([x in self.final for x in aux]):
                        new_final.append(new_states[str(aux)])

                    current_states.append(aux)

                new_transitions[
                    new_states[str(states)], new_states[str(aux)]
                ] = new_transitions.get(
                    (new_states[str(states)], new_states[str(aux)]), []
                ) + [
                    terminal
                ]

        return Deterministic(
            AutomatoFinito(list(new_states.values()), new_transitions, 1, new_final)
        )

    @staticmethod
    def union(AF1, AF2):
        # Faz a união de dois autômatos finitos, em um autômato finito não-determinístico

        # AF1: instância de um autômato finito
        # AF2: instância de um autômato finito

        return NonDeterministic(AutomatoFinito.union(AF1, AF2))

    @staticmethod
    def intersection(AF1, AF2):
        # Faz a intersecção, por meio do produto cartesiano, de dois autômatos finitos, em um autômato finito não-determinístico

        # AF1: instância de um autômato finito
        # AF2: instância de um autômato finito

        return NonDeterministic(AutomatoFinito.intersection(AF1, AF2))

    @staticmethod
    def readFile(arquivo):
        # Lê um arquivo e retorna um autômato finito não-determinístico

        # arquivo: caminho do arquivo

        return NonDeterministic(AutomatoFinito.readFile(arquivo))
