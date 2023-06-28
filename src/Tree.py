from Node import Node

class Tree:
  """
  Classe utilizada para representar árvores de derivação
  Atribs:
    nó raiz, da árvore
    último nó adicionado
    dicionário de nós folhas
  """

  def __init__(self):
    self.raiz = None
    self.ultimo = None
    self.dict = dict()

  """Imprime em tela toda a árvore"""
  def imprimirArvore(self):

    self.raiz.print()

  """Calcula a função FollowPos da árvore"""
  def followPos(self):


    """
      Retorna uma lista com os nós pertencentes à uma subárvore
      Parametro:
        nó raiz da subárvore
    """
    def iterarSubarvore(node):

      aux = [node]
      if node.left_child:
        aux += iterarSubarvore(node.left_child)
      if node.mid_child:
        aux += iterarSubarvore(node.mid_child)
      if node.right_child:
        aux += iterarSubarvore(node.right_child)
      return aux

    nodes = iterarSubarvore(self.raiz)
    
    count = 1
    for node in nodes:
      if node.ehFolha():
        node.index = count
        self.dict[count] = node.data_value
        count += 1

    follow_pos = dict()
    for node in nodes:
      if node.data_value == '*':
        for lp in node.lastPos():
          follow_pos[lp.index] = follow_pos.get(lp.index, []) + [fp.index for fp in node.firstPos()]
      elif node.data_value == '.':
        for lp in node.left_child.lastPos():
          follow_pos[lp.index] = follow_pos.get(lp.index, []) + [fp.index for fp in node.right_child.firstPos()]
      elif node.ehFolha():
        follow_pos[node.index] = follow_pos.get(node.index, []) + []
    
    return follow_pos


  """
    Insere um novo nodo na árvore
    Parametro:
      dado a ser inserido
  """
  def inserir(self, data):

    # Verifica se o novo dado a ser inserido é uma subárvore
    if isinstance(data, Tree):
      new_node = data.raiz
    else:
      new_node = Node(data)

    # Caso a árvore esteja vazia, insere o dado na raiz
    if not self.raiz:
      self.raiz = new_node
      self.ultimo = self.raiz
      return

    # Caso a raiz seja * e nenhum outro nodo tenha sido adicionado, insere o dado no filho do meio
    if self.raiz.data_value == '*' and self.raiz.ehFolha():
      new_node.parent_node = self.ultimo
      self.ultimo.mid_child = new_node
      self.ultimo = new_node
      return

    # Caso o último nodo inserido seja um operador e o novo dado a ser adicionado seja um terminal ou uma subárvore, o insere na esquerda
    if self.ultimo.ehOperador() and (not new_node.ehOperador() or isinstance(data, Tree)):
      new_node.parent_node = self.ultimo
      self.ultimo.left_child = new_node
      self.ultimo = new_node
      return
    
    # Caso o último dado inserido seja um terminal ou uma subárvore e o novo nodo seja um operador, realiza o balanceamento e insere
    if (not self.ultimo.ehOperador() or (self.ultimo.left_child or self.ultimo.mid_child)) and new_node.ehOperador():
      if self.ultimo.parent_node:
        new_node.parent_node = self.ultimo.parent_node
        if self.ultimo.parent_node.left_child:
          self.ultimo.parent_node.left_child = new_node
        else:
          self.ultimo.parent_node.mid_child = new_node
        self.ultimo.parent_node = new_node
      else:
        self.raiz = new_node
      new_node.right_child = self.ultimo
      self.ultimo = new_node
      return

    raise Exception('Expressão inválida!')