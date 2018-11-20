from CymbolVisitor import CymbolVisitor
from CymbolParser import CymbolParser

class MyVisitor(CymbolVisitor):
   
   def __init__(self):
      self.var_valores = {}
      ##dicionario com valores das variaveis "fixas" locais
      self.var_valores_global = {}
      ##dicionario com valores das variaveis globais
      self.dentro_funcao = 0
      ##se esta dentro de uma funcao ou nao. Controle de variaveis
      ##globais
      self.var_temp_correspondecia = {}
      ##dicionario de correspondencia entra variaveis temporarias
      ##(e.g.,%1, %2), e variaveis "fixas", isto eh, com 
      ##nome (e.g., %x, %y)
      self.apelidos = {}
      ##usado para correspondencia de parametros da declaracao 
      ##de funcao e variaveis temporarias
      self.ids_iguais = {}
      ##caso de operacao com dois ids iguais
      self.chamada_funcao = 0
      ##associa funcoes a variaveis temporarias
      self.temp_atual = 0
      ##numero da variavel temporaria atual, pra nunca ser usada
      ##a mesma
      self.entrou_id = 0
      ##usado nas atribuicoes, pra saber se dentro de uma expressao
      ##hah um id, pois neste caso sao usadas variaveis temporarias
      self.temp_sinal = 0
      ##usado no caso de uma expressao com sinal antes, pois eh 
      ##preciso fazer uma subtracao de zero por esta expressao
      self.retornei = 0
      ##usado para caso de funcao ter ou nao retorno
      self.ass_vdl = 0
   
   def visitFuncDecl(self, ctx):
      print('define i32 @' + ctx.ID().getText(), end = '(') 
      lista_parametros = []
      try:
         ctx.paramTypeList().getText()
      except:
         self.temp_atual += 1
         print(') #0 {')
         print('   %' + str(self.temp_atual) + ' = alloca i32, align 4')
         print('   store i32 0, i32* %' + str(self.temp_atual) + ', align 4')
         self.temp_atual += 1
         pass
      else:
         lista_parametros = ctx.paramTypeList().getText().split(',')
         tamanho = len(lista_parametros)
      
         while tamanho > 1:
            print('i32, ', end = '')
            tamanho -= 1
      
         if len(lista_parametros) >= 1:
            print('i32', end = '')
            print(') #0 {')
            self.temp_atual = len(lista_parametros) + 1

            j = 0
            for parametro in lista_parametros:
               print('   %' + str(self.temp_atual) + ' = alloca i32, align 4')
               print('   store i32 %' + str(j) + ', i32* %' + str(self.temp_atual) + ', align 4')
               self.apelidos[parametro[3:]] = str(self.temp_atual)
               self.var_valores[parametro[3:]] = 5
               self.temp_atual += 1
               j += 1
         else:
            print(') #0 {')
      
      self.dentro_funcao = 1
      self.visit(ctx.block())
      self.temp_atual = 0
      self.dentro_funcao = 0

      if self.retornei == 0:
         print('   ret i32 0')

      print('}\n')
      self.var_valores = {}
      self.var_temp_correspondecia = {}
      self.apelidos = {}
      self.temp_atual = 0
      self.entrou_id = 0
      self.temp_sinal = 0
      self.retornei = 0

   def visitFunctionCallExpr(self, ctx):
      fun_list = []
      try:
         ctx.exprList().getText()
      except:
         print('   %' + str(self.temp_atual) + ' = call i32 @' + ctx.ID().getText() + '()')
         if ctx.ID().getText() in self.var_temp_correspondecia:
               self.ids_iguais[ctx.ID().getText()] = (self.var_temp_correspondecia[ctx.ID().getText()], self.temp_atual)
         self.var_temp_correspondecia[ctx.ID().getText()] = self.temp_atual
         self.temp_atual += 1
      else:
         i = 0
         while 1:
            try:
               x, y = self.visit(ctx.exprList().expr(i))
            except:
               break
            else:
               if self.temp_sinal == 1:
                  fun_list.append('%' + str(self.temp_atual - 1))
                  self.temp_sinal = 0
               else:
                  fun_list.append(str(x))
               i += 1
         
         print('   %' + str(self.temp_atual) + ' = call i32 @' + ctx.ID().getText() + '(', end = '')
         if ctx.ID().getText() in self.var_temp_correspondecia:
               self.ids_iguais[ctx.ID().getText()] = (self.var_temp_correspondecia[ctx.ID().getText()], self.temp_atual)
         self.var_temp_correspondecia[ctx.ID().getText()] = self.temp_atual
         self.temp_atual += 1

         tamanho = len(fun_list)
         #print(fun_list)
         j = 0

         while j < (tamanho - 1):
            print('i32 ' + fun_list[j], end = ', ')
            j += 1
         print('i32 ' + fun_list[j] + ')')

      self.temp_sinal = 1
      self.chamada_funcao = 1
      self.entrou_id = 0

      return 0, 0

   def visitVarDecl(self, ctx):

      if self.dentro_funcao == 0:
         try:
            ctx.expr().getText()
         except:
            self.var_valores_global[ctx.ID().getText()] = 5
            print('@' + ctx.ID().getText() + ' = global i32 ' + str(self.var_valores_global[ctx.ID().getText()]) + ', align 4')
         else:
            self.var_valores_global[ctx.ID().getText()], x = self.visit(ctx.expr())
            print('@' + ctx.ID().getText() + ' = global i32 ' + str(self.var_valores_global[ctx.ID().getText()]) + ', align 4')
      else:   
         print('   %' + ctx.ID().getText() + ' = alloca i32, align 4')
         
         try:
            ctx.expr().getText()
         except:
            self.var_valores[ctx.ID().getText()] = 5
         else:
            self.var_valores[ctx.ID().getText()], x = self.visit(ctx.expr())

            if self.entrou_id == 1:
               ##se entrou_id == 1, entao tem id na expr, e foi necessario usar variaveis temporarias
               print('   store i32 %' + str(self.temp_atual - 1) + ', i32* %' + ctx.ID().getText() + ', align 4')
               self.entrou_id = 0
            elif self.entrou_id == 0 and self.chamada_funcao == 1:
               ##se nao, chamada de funcao na expr
               print('   store i32 %' + str(self.temp_atual - 1) + ', i32* %' + ctx.ID().getText() + ', align 4')
               self.chamada_funcao = 0
            else:
               ##se nao, soh constantes na expr   
               print('   store i32 ' + str(self.var_valores[ctx.ID().getText()]) + ', i32* %' + ctx.ID().getText() + ', align 4')

      self.temp_sinal = 0
      self.ass_vdl = 1

   def visitReturnStat(self, ctx):
      self.temp_sinal = 0;
      self.chamada_funcao = 0;
      x, y = self.visit(ctx.expr())

      if self.temp_sinal == 1:
         ##se entrou_id == 1, entao tem id na expr, e foi necessario usar variaveis temporarias
         print('   ret i32 %' + str(self.temp_atual - 1))
         self.retornei = 1
         self.temp_sinal = 0
      elif self.temp_sinal == 0 and self.chamada_funcao == 1:
         ##chamada de funcao no retorno
         print('   ret i32 %' + str(self.temp_atual - 1))
         self.chamada_funcao = 0
         self.retornei = 1
      else:
         ##se nao soh foi constantes na expr
         print('   ret i32 ' + str(x))
         self.retornei = 1

      self.temp_sinal = 0

   def visitAssignStat(self, ctx):
      if ctx.ID().getText() in self.var_valores:
         self.var_valores[ctx.ID().getText()], x = self.visit(ctx.expr())
      else:
         self.var_valores_global[ctx.ID().getText()], x = self.visit(ctx.expr())

      if not(ctx.ID().getText() in self.apelidos):
         ##nao eh parametro de funcao
         if ctx.ID().getText() in self.var_valores:
            ##variavel local
            if self.entrou_id == 1:
               ##se entrou_id == 1, entao tem id na expr, e foi necessario usar variaveis temporarias
               print('   store i32 %' + str(self.temp_atual - 1) + ', i32* %' + ctx.ID().getText() + ', align 4')
               self.entrou_id = 0
            elif self.entrou_id == 0 and self.chamada_funcao == 1:
               ##chamada de funcao
               print('   store i32 %' + str(self.temp_atual - 1) + ', i32* %' + ctx.ID().getText() + ', align 4')
               self.chamada_funcao = 0
            else:
               ##soh constantes
               print('   store i32 ' + str(self.var_valores[ctx.ID().getText()]) + ', i32* %' + ctx.ID().getText() + ', align 4')
         else:
            ##variavel global
            if self.entrou_id == 1:
               ##se entrou_id == 1, entao tem id na expr, e foi necessario usar variaveis temporarias
               print('   store i32 %' + str(self.temp_atual - 1) + ', i32* @' + ctx.ID().getText() + ', align 4')
               self.entrou_id = 0
            elif self.entrou_id == 0 and self.chamada_funcao == 1:
               ##chamada de funcao
               print('   store i32 %' + str(self.temp_atual - 1) + ', i32* @' + ctx.ID().getText() + ', align 4')
               self.chamada_funcao = 0
            else:
               ##soh constantes
               print('   store i32 ' + str(self.var_valores_global[ctx.ID().getText()]) + ', i32* @' + ctx.ID().getText() + ', align 4')   
      else:   
         if self.entrou_id == 1:
            ##se entrou_id == 1, entao tem id na expr, e foi necessario usar variaveis temporarias
            print('   store i32 %' + str(self.temp_atual - 1) + ', i32* %' + self.apelidos[ctx.ID().getText()] + ', align 4')##mudei
            self.entrou_id = 0
         elif self.entrou_id == 0 and self.chamada_funcao == 1:
            ##chamada de funcao
            print('   store i32 %' + str(self.temp_atual - 1) + ', i32* %' + ctx.ID().getText() + ', align 4')
            self.chamada_funcao = 0
         else:
            ##se nao soh foi constantes na expr
            print('   store i32 ' + str(self.var_valores[ctx.ID().getText()]) + ', i32* %' + self.apelidos[ctx.ID().getText()] + ', align 4')  ##mudei
      
      self.temp_sinal = 0
      self.ass_vdl = 1

   def visitMulDivExpr(self, ctx):
      left, temp_left = self.visit(ctx.expr(0))
      right, temp_right = self.visit(ctx.expr(1))
      result = 0
      temp = -1

      try: 
         ctx.expr(0).ID() and ctx.expr(1).ID()
         ##alguem nao tem id?
      except :
         ##exp0 ou exp1 nao tem id!
         try:
            ctx.expr(0).ID()
            ##exp0 tem id?
         except :
            ##exp0 nao tem id!
            try:
               ctx.expr(1).ID()
               ##exp1 tem id?
            except :
            ##nem exp0 nem exp1 tem id!
               if (temp_left != -1) and (temp_right != -1):
                  ##ambas sao temporarias
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(temp_left) + ', %' + str(temp_right))
                     result = int(left) * int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(temp_left) + ', %' + str(temp_right))
                     result = int(left) / int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
               elif temp_left  != -1:
                  ##soh a esquerda eh temporaria
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(temp_left) + ', ' + str(right))
                     result = int(left) * int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(temp_left) + ', ' + str(right))
                     result = int(left) / int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
               elif temp_right  != -1:
                  ##soh a direira eh temporaria
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 ' + str(left) + ', %' + str(temp_right))
                     result = int(left) * int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 ' + str(left) + ', %' + str(temp_right))
                     result = int(left) / int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
               else :
                  ##ambas sao constantes
                  if ctx.op.type == CymbolParser.MUL:
                     result = int(left) * int(right)
                     temp = -1
                  else:
                     result = int(left) / int(right)
                     temp = -1
            else:
               ##soh exp1 tem id!
               if temp_left  != -1:
                  ##a da esquerda eh temporaria
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(temp_left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) * int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(temp_left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) / int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
               else:
                  ##a da esquerda eh constante
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 ' + str(left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) * int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 ' + str(left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) / int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
         else:
            ##exp0 tem id!
            try:
               ctx.expr(1).ID()
               ##eu sei que exp0 tem id... exp1 tem id?
            except :
               ##exp1 nao tem id!
               ##so exp0 tem id
               if temp_right != -1:
                  ##exp1 eh temporaria
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(temp_right))
                     result = int(left) * int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(temp_right))
                     result = int(left) / int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
               else:
                  ##exp1 eh constante
                  if ctx.op.type == CymbolParser.MUL:
                     print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', ' + str(right))
                     result = int(left) * int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', ' + str(right))
                     result = int(left) / int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
            else:
               ##exp1 tem id! entao os dois tem id!
               ##nunca entra aqui
               if ctx.op.type == CymbolParser.MUL:
                  print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                  result = int(left) * int(right)
                  temp = self.temp_atual;
                  self.temp_atual += 1
                  self.temp_sinal = 1
               else:
                  print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                  result = int(left) / int(right)
                  temp = self.temp_atual;
                  self.temp_atual += 1
                  self.temp_sinal = 1
      else:
         self.teste = 1
         ##ambos tem id
         if ctx.op.type == CymbolParser.MUL:
            if ctx.expr(0).ID().getText() == ctx.expr(1).ID().getText():
               print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(self.ids_iguais[ctx.expr(0).ID().getText()][0]) + ', %' + str(self.ids_iguais[ctx.expr(1).ID().getText()][1]))
               self.ids_iguais.pop(ctx.expr(0).ID().getText())
            else:
               print('   %' + str(self.temp_atual) + ' = mul nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
            result = int(left) * int(right)
            temp = self.temp_atual;
            self.temp_atual += 1
            self.temp_sinal = 1
         else:
            if ctx.expr(0).ID().getText() == ctx.expr(1).ID().getText():
               print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(self.ids_iguais[ctx.expr(0).ID().getText()][0]) + ', %' + str(self.ids_iguais[ctx.expr(1).ID().getText()][1]))
               self.ids_iguais.pop(ctx.expr(0).ID().getText())
            else:
               print('   %' + str(self.temp_atual) + ' = sdiv i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
            result = int(left) / int(right)
            temp = self.temp_atual;
            self.temp_atual += 1
            self.temp_sinal = 1

      return int(result), temp
   
   def visitAddSubExpr(self, ctx):
      left, temp_left = self.visit(ctx.expr(0))
      right, temp_right = self.visit(ctx.expr(1))
      result = 0
      temp = -1

      try: 
         ctx.expr(0).ID() and ctx.expr(1).ID()
         ##alguem nao tem id?
      except :
         ##exp0 ou exp1 nao tem id!
         try:
            ctx.expr(0).ID()
            ##exp0 tem id?
         except :
            ##exp0 nao tem id!
            try:
               ctx.expr(1).ID()
               ##exp1 tem id?
            except :
            ##nem exp0 nem exp1 tem id!
               if (temp_left != -1) and (temp_right != -1):
                  ##ambas sao temporarias
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(temp_left) + ', %' + str(temp_right))
                     result = int(left) + int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(temp_left) + ', %' + str(temp_right))
                     result = int(left) - int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
               elif temp_left  != -1:
                  ##soh a esquerda eh temporaria
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(temp_left) + ', ' + str(right))
                     result = int(left) + int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(temp_left) + ', ' + str(right))
                     result = int(left) - int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
               elif temp_right  != -1:
                  ##soh a direira eh temporaria
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 ' + str(left) + ', %' + str(temp_right))
                     result = int(left) + int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 ' + str(left) + ', %' + str(temp_right))
                     result = int(left) - int(right)
                     temp = self.temp_atual
                     self.temp_atual += 1
                     self.temp_sinal = 1
               else :
                  ##ambas sao constantes
                  if ctx.op.type == CymbolParser.PLUS:
                     result = int(left) + int(right)
                     temp = -1
                  else:
                     result = int(left) - int(right)
                     temp = -1
            else:
               ##soh exp1 tem id!
               if temp_left  != -1:
                  ##a da esquerda eh temporaria
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(temp_left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) + int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(temp_left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) - int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
               else:
                  ##a da esquerda eh constante
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 ' + str(left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) + int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 ' + str(left) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                     result = int(left) - int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
         else:
            ##exp0 tem id!
            try:
               ctx.expr(1).ID()
               ##eu sei que exp0 tem id... exp1 tem id?
            except :
               ##exp1 nao tem id!
               ##so exp0 tem id
               if temp_right != -1:
                  ##exp1 eh temporaria
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(temp_right))
                     result = int(left) + int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(temp_right))
                     result = int(left) - int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
               else:
                  ##exp1 eh constante
                  if ctx.op.type == CymbolParser.PLUS:
                     print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', ' + str(right))
                     result = int(left) + int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
                  else:
                     print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', ' + str(right))
                     result = int(left) - int(right)
                     temp = self.temp_atual;
                     self.temp_atual += 1
                     self.temp_sinal = 1
            else:
               ##exp1 tem id! entao os dois tem id!
               ##porem nunca entra aqui, pois se os dois tem id
               ##o primeiro try ja pega
               if ctx.op.type == CymbolParser.PLUS:
                  print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                  result = int(left) + int(right)
                  temp = self.temp_atual;
                  self.temp_atual += 1
                  self.temp_sinal = 1
               else:
                  print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
                  result = int(left) - int(right)
                  temp = self.temp_atual;
                  self.temp_atual += 1
                  self.temp_sinal = 1
      else:
         if ctx.op.type == CymbolParser.PLUS:
            if ctx.expr(0).ID().getText() == ctx.expr(1).ID().getText():
               print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(self.ids_iguais[ctx.expr(0).ID().getText()][0]) + ', %' + str(self.ids_iguais[ctx.expr(1).ID().getText()][1]))
               self.ids_iguais.pop(ctx.expr(0).ID().getText())
            else:
               print('   %' + str(self.temp_atual) + ' = add nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
            result = int(left) + int(right)
            temp = self.temp_atual;
            self.temp_atual += 1
            self.temp_sinal = 1
         else:
            if ctx.expr(0).ID().getText() == ctx.expr(1).ID().getText():
               print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(self.ids_iguais[ctx.expr(0).ID().getText()][0]) + ', %' + str(self.ids_iguais[ctx.expr(1).ID().getText()][1]))
               self.ids_iguais.pop(ctx.expr(0).ID().getText())
            else:
               print('   %' + str(self.temp_atual) + ' = sub nsw i32 %' + str(self.var_temp_correspondecia[ctx.expr(0).ID().getText()]) + ', %' + str(self.var_temp_correspondecia[ctx.expr(1).ID().getText()]))
            result = int(left) - int(right)
            temp = self.temp_atual;
            self.temp_atual += 1
            self.temp_sinal = 1

      return result, temp
   
   def visitIntExpr(self, ctx):
      ##close
      return ctx.INT().getText(), -1

   def visitVarIdExpr(self, ctx):
      self.entrou_id = 1

      if not(ctx.ID().getText() in self.apelidos):
         if ctx.ID().getText() in self.var_valores:
            print('   %' + str(self.temp_atual) + ' = load i32, i32* %' + ctx.ID().getText() + ', align 4')
            if ctx.ID().getText() in self.var_temp_correspondecia:
               self.ids_iguais[ctx.ID().getText()] = (self.var_temp_correspondecia[ctx.ID().getText()], self.temp_atual)
            self.var_temp_correspondecia[ctx.ID().getText()] = self.temp_atual
            self.temp_atual += 1
            self.temp_sinal = 1
            return str(self.var_valores[ctx.ID().getText()]), -1
         else:
            print('   %' + str(self.temp_atual) + ' = load i32, i32* @' + ctx.ID().getText() + ', align 4')
            self.var_temp_correspondecia[ctx.ID().getText()] = self.temp_atual
            self.temp_atual += 1
            self.temp_sinal = 1
            return str(self.var_valores_global[ctx.ID().getText()]), -1
      else:
         print('   %' + str(self.temp_atual) + ' = load i32, i32* %' + self.apelidos[ctx.ID().getText()] + ', align 4')
         self.var_temp_correspondecia[ctx.ID().getText()] = self.temp_atual
         self.temp_atual += 1
         self.temp_sinal = 1
         return str(self.var_valores[ctx.ID().getText()]), -1

   def visitSignedExpr(self, ctx):
      x, y = self.visit(ctx.expr())

      if self.temp_sinal == 1:
         if ctx.op.type == CymbolParser.PLUS:
            self.temp_sinal = 0
            return str(x), y
         else: 
            print('   %' + str(self.temp_atual) + ' = sub nsw i32 0, %' + str(self.temp_atual - 1))
            self.temp_atual += 1
            self.temp_sinal = 0
            return '-' + str(x), y
      else:
         if ctx.op.type == CymbolParser.PLUS:
            self.temp_sinal = 0
            return str(x), y
         else: 
            self.temp_sinal = 0
            return '-' + str(x), y

   def visitParenExpr(self, ctx):
      ##close
      return self.visit(ctx.expr())