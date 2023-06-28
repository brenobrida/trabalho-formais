from AutomatoFinito import AutomatoFinito


class Deterministic(AutomatoFinito):
    # Uma classe usada para representar autômatos finitos determinísticos

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

        if super().isNonDeterministic():
            raise Exception("O autômato é não-determinístico!")

    def readEntry(self, input):
        # Verifica se o autômato reconhece determinada cadeia de entrada

        # input: cadeia de caracteres de entrada

        cs = [self.initial]
        for t in input:
            cs = [x for state in cs for x in self.nextState(state, t)]

        return any([x in self.final for x in cs])

    @staticmethod
    def union(AF1, AF2):
        # Faz a união de dois autômatos finitos, em um autômato finito determinístico

        # AF1: instância de um autômato finito
        # AF2: instância de um autômato finito

        from NonDeterministic import NonDeterministic

        return NonDeterministic.union(AF1, AF2).toDeterministic()

    @staticmethod
    def intersection(AF1, AF2):
        # Faz a intersecção, por meio do produto cartesiano, de dois autômatos finitos, em um autômato finito determinístico

        # AF1: instância de um autômato finito
        # AF2: instância de um autômato finito

        from NonDeterministic import NonDeterministic

        return NonDeterministic.intersection(AF1, AF2).toDeterministic()

    @staticmethod
    def readFile(arquivo):
        # Lê um arquivo e retorna um autômato finito determinístico

        # arquivo: caminho do arquivo

        return Deterministic(AutomatoFinito.readFile(arquivo))
