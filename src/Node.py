class Node:
  """
  Classe utilizada para instanciar nodos de uma árvore de derivação
  Atribs:
    valor do nodo
    filho esquerdo, do nodo
    filho direito, do nodo
    filho do meio, do nodo
    nodo pai do nodo atual
    índice do nodo folha
  """

  def __init__(self, data_value, left_child=None, right_child=None, mid_child=None, parent_node=None, index=0):


    self.data_value = data_value
    self.left_child = left_child
    self.right_child = right_child
    self.mid_child = mid_child
    self.parent_node = parent_node
    self.index = index

  """Responsavel por verificar se o nodo é uma folha"""
  def ehFolha(self):

    return not self.right_child and not self.left_child and not self.mid_child


  """Responsavel por verificar se o nodo é um operador"""
  def ehOperador(self):

    return self.data_value in ['*', '+', '.']

  """Responsavel por verificar se o nodo é anulável"""
  def ehAnulavel(self):

    if self.data_value in ['*', '&']:
      return True
    elif self.left_child and self.right_child:
      if self.data_value == '+':
        return self.left_child.ehAnulavel() or self.right_child.ehAnulavel()
      elif self.data_value == '.':
        return self.left_child.ehAnulavel() and self.right_child.ehAnulavel()
    return False
  
  """Retorna o conjunto FirstPos do nodo"""
  def firstPos(self):

    if self.data_value == '&':
      return []
    elif self.data_value == '*':
      return self.mid_child.firstPos()
    elif self.left_child and self.right_child:
      if self.data_value == '+':
        return self.left_child.firstPos() + self.right_child.firstPos()
      elif self.data_value == '.':
        return self.left_child.firstPos() + self.right_child.firstPos() if self.left_child.ehAnulavel() else self.left_child.firstPos()
    return [self]

  """Retorna o conjunto LastPos do nodo"""
  def lastPos(self):

    if self.data_value == '&':
      return []
    elif self.data_value == '*':
      return self.mid_child.lastPos()
    elif self.left_child and self.right_child:
      if self.data_value == '+':
        return self.left_child.lastPos() + self.right_child.lastPos()
      elif self.data_value == '.':
        return self.left_child.lastPos() + self.right_child.lastPos() if self.right_child.ehAnulavel() else self.right_child.lastPos()
    return [self]

  """Imprime em tela o nodo e seus filhos"""
  def print(self):
   
    print (self.data_value)
    if self.right_child:
      print ('Right: ', end='')
      self.right_child.print()
    if self.mid_child:
      print ('Middle: ', end='')
      self.mid_child.print()
    if self.left_child:
      print ('Left: ', end='')
      self.left_child.print()