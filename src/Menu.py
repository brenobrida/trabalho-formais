import readline

class Menu:
    def __init__(self, options, title='', submenu=False):
        self.options = options + (['Sair'] if not submenu else ['Retornar'])
        self.title = title

    def append(self, item):
        self.options.pop()  # Remove 'Sair' or 'Retornar'
        if isinstance(item, list):
            self.options.extend(item)
        else:
            self.options.append(item)
        self.options.append('Sair' if 'Retornar' not in self.options else 'Retornar')

    def remove(self, item):
        if item in self.options and item not in ('Sair', 'Retornar'):
            self.options.remove(item)

    def print_menu(self):
        print(self.title)
        for i, option in enumerate(self.options):
            print(f"{i+1}. {option}")

    def refreshTitle(self, new_title):
        self.title = new_title

    def select(self):
        self.print_menu()
        choice = input("Escolha uma opção: ")
        return int(choice), self.options[int(choice) - 1] # Retorna a escolha do usuário e a opção selecionada
