import time
import os

from AutomatoFinito import AutomatoFinito
from NonDeterministic import NonDeterministic
from Deterministic import Deterministic
from RegEx import RegEx
from Grammar import Grammar
from Menu import Menu

afs = dict()
grammars = dict()
arquivos = {'AFDS': [], 'AFNDS': [], 'Gramáticas': []}

""" opções do menu principal """
select_menu = Menu(
  ['Importar um autômato', 
   'Ler entrada', 
   'Realizar conversão NonDeterministic para Deterministic', 
   'Minimizar Automato Finito', 
   'União de Automatos Finitos', 
   'Interseção de Automatos Finitos', 
   'Converter RegEx para Deterministic',
   'Importar gramática',
   'Remover recursão à esquerda',
   'Fatorar uma gramática',
   'Ler entrada [preditivo LL(1)]',
   'Ler entrada [SLR(1)]'])

""" submenu para automatos finitos"""
def afsMenu(title='Selecione um autômato:'):
  if not arquivos['AFDS'] and not arquivos['AFNDS']:
    raise Exception('Não foi possível encontrar o autômato!')

  select_afs = Menu([y for x in arquivos.values() for y in x], title=title, submenu=True)
  (_, selected) = select_afs.select()

  return (False, False) if selected == 'Retornar' else (NonDeterministic(afs[selected]) if afs[selected].isNonDeterministic() else Deterministic(afs[selected]), selected)

""" submenu para gramaticas"""
def menuGramaticas(title='Selecione uma gramática:'):
  if not arquivos['Gramáticas']:
    raise Exception('Nenhuma gramática encontrado!')

  select_grammars = Menu(arquivos['Gramáticas'], title=title, submenu=True)
  (_, selected) = select_grammars.select()

  return (False, False) if selected == 'Retornar' else (grammars[selected], selected)

""" submenu de opcoes de arquivo para AF"""
def menuOpcoes(AutomatoFinito, title=''):
  options_menu = Menu(['Salvar como arquivo', 'Salvar como tabela de transições', 'Carregar'], title=title + ':\n\n' + AutomatoFinito.tableAutomata(), submenu=True)
  (n, selected) = options_menu.select()

  if selected == 'Retornar':
    return
  elif n == 3:
    arquivo = input(f'Nome do autômato [default={title}]: ') or title
    atualizarArquivos(AutomatoFinito, arquivo)
    return
  elif n == 1:
    AutomatoFinito.saveFile(input('\nNome do arquivo: '))
    print ('\n\033[92mArquivo salvo com sucesso!\033[0m')
  elif n == 2:
    AutomatoFinito.printFile(input('\nNome do arquivo: '))
    print ('\n\033[92mArquivo salvo com sucesso!\033[0m')
  time.sleep(1)
  
""" submenu de opcoes de arquivo para Gramaticas"""
def menuOpcoesGramaticas(grammar, title=''):
  options_menu = Menu(['Salvar como arquivo', 'Carregar'], title=title + ':\n\n' + grammar.toStr(), submenu=True)
  (n, selected) = options_menu.select()

  if selected == 'Retornar':
    return
  elif n == 2:
    arquivo = input(f'Nome do autômato [default={title}]: ') or title
    atualizarArquivos(grammar, arquivo)
    return
  elif n == 1:
    grammar.saveFile(input('\nNome do arquivo: '))
    print ('\n\033[92mArquivo salvo com sucesso!\033[0m')
  time.sleep(1)

def atualizarArquivos(object, object_name):
  if isinstance(object, AutomatoFinito):
    if object_name not in afs:
      arquivos['AFNDS'].append(object_name) if object.isNonDeterministic() else arquivos['AFDS'].append(object_name)
    afs[object_name] = object
  elif isinstance(object, Grammar):
    if object_name not in arquivos:
      arquivos['Gramáticas'].append(object_name)
    grammars[object_name] = object

  out = ''
  if arquivos['AFDS']:
    out += 'AFDS:\n'
    out += '\n'.join(arquivos['AFDS'])
  if arquivos['AFNDS']:
    out += '\n\n' if arquivos['AFDS'] else ''
    out += 'AFNDS:\n'
    out += '\n'.join(arquivos['AFNDS'])
  if arquivos['Gramáticas']:
    out += '\n\n' if arquivos['AFDS'] or arquivos['AFDS'] else ''
    out += 'Gramáticas:\n'
    out += '\n'.join(arquivos['Gramáticas'])
  select_menu.refreshTitle(out)

def opcao1():
  arquivo = input('\nCaminho do arquivo: ')
  automato = AutomatoFinito.readFile(arquivo)

  atualizarArquivos(automato, arquivo)

def opcao2():
  (AutomatoFinito, _) = afsMenu()

  if AutomatoFinito:
    read = input('\nEntrada: ')

    print ('\n\033[92mEntrada válida!\033[0m' if AutomatoFinito.readEntry(read) else '\n\033[91mEntrada inválida!\033[0m')
    time.sleep(1)

def opcao3():
  if not arquivos['AFNDS']:
    raise Exception('Nenhum autômato finito não-determinístico encontrado!')

  select_afs = Menu(arquivos['AFNDS'], submenu=True)
  (_, selected) = select_afs.select()

  if selected != 'Retornar':
    AutomatoFinito = NonDeterministic(afs[selected]).toDeterministic()
    menuOpcoes(AutomatoFinito=AutomatoFinito, title=f'AFNDtoAFD({selected})')

def opcao4():
  (AutomatoFinito, selected) = afsMenu()

  if AutomatoFinito:
    AutomatoFinito = AutomatoFinito.minimize(AutomatoFinito)

    menuOpcoes(AutomatoFinito=AutomatoFinito, title=f'AutomatoFinito Mínimo({selected})')

def opcao5():
  (af1, selected1) = afsMenu()

  if af1:
    (af2, selected2) = afsMenu(title='\033[94mAF selecionado: ' + selected1 + '\033[0m')

    if af2:
      AutomatoFinito = AutomatoFinito.union(af1, af2)
      menuOpcoes(AutomatoFinito=AutomatoFinito, title=f'União({selected1}, {selected2})')

def opcao6():
  (af1, selected1) = afsMenu()

  if af1:
    (af2, selected2) = afsMenu(title='\033[94mAF selecionado: ' + selected1 + '\033[0m')

    if af2:
      AutomatoFinito = AutomatoFinito.intersection(af1, af2)
      menuOpcoes(AutomatoFinito=AutomatoFinito, title=f'Interseção({selected1}, {selected2})')

def opcao7():
  os.system('cls||clear')
  read = input('Expressão regular: ')

  AutomatoFinito = RegEx(read).toAF()
  menuOpcoes(AutomatoFinito=AutomatoFinito, title=f'RegExtoAF({read})')

def opcao8():
  arquivo = input('\nCaminho do arquivo: ')
  grammar = Grammar.readFile(arquivo)

  atualizarArquivos(grammar, arquivo)

def opcao9():
  (grammar, selected) = menuGramaticas()

  if grammar:
    grammar = Grammar.removeLeftRecursion(grammar)
    menuOpcoesGramaticas(grammar=grammar, title=f'NonRecursive({selected})')

def opcao10():
  (grammar, selected) = menuGramaticas()

  if grammar:
    grammar = Grammar.factorate(grammar)
    menuOpcoesGramaticas(grammar=grammar, title=f'Factorate({selected})')

def opcao11():
  (grammar, _) = menuGramaticas()

  if grammar:
    read = input('\nEntrada: ')

    print ('\n\033[92mEntrada válida!\033[0m' if grammar.readInputLL(read) else '\n\033[91mEntrada inválida!\033[0m')
    time.sleep(1)

def opcao12():
  (grammar, _) = menuGramaticas()

  if grammar:
    read = input('\nEntrada: ')

    print ('\n\033[92mEntrada válida!\033[0m' if grammar.readInputSLR(read) else '\n\033[91mEntrada inválida!\033[0m')
    time.sleep(1)

while True:
  (op, _) = select_menu.select()

  try:
    if op == 1:
      opcao1()
    elif op == 2:
      opcao2()
    elif op == 3:
      opcao3()
    elif op == 4:
      opcao4()
    elif op == 5:
      opcao5()
    elif op == 6:
      opcao6()
    elif op == 7:
      opcao7()
    elif op == 8:
      opcao8()
    elif op == 9:
      opcao9()
    elif op == 10:
      opcao10()
    elif op == 11:
      opcao11()
    elif op == 12:
      opcao12()
    elif op == 13:
      break
  except Exception as e:
    print ('\n\033[91m' + str(e) + '\033[0m')
    time.sleep(1)