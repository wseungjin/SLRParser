from pandas import DataFrame
import sys

# 되는게 생길때 까지 계속읽는다
# 되는게 생긴 다음 안되는 부분이 나오면 다시돌아가서 되는 걸로 확정
class LexicalAnalyzer:
  def __init__(self, input, lineNumber):
    self.input = input
    self.tokens = []        # 파싱된 토큰
    self.start = 0			# 토큰의 시작
    self.current = 0		# 토큰의 끝
    self.line = lineNumber			# 라인

  def isDecimal(self, character):
    result = ord(character) - ord('0')
    if result>0 and result<10:
      return True
    else:
      return False

  def isDigit(self, character):
    result = ord(character) - ord('0')
    if result>=0 and result<10:
      return True
    else:
      return False
  def hiddenProblem(self, result):
    if(result[0]=="Integer" or result[0]=="FLOAT") and result[1][0]=='-' and len(self.tokens)>0 :   #hidden problem 해결
      # print("hidden문제 접근!", result)
      last_token = len(self.tokens)-1
      while(True):
        if last_token<0:
          return False
          
        if self.tokens[last_token][1]==' ':
          last_token = last_token - 1
          continue
        elif (self.tokens[last_token][0]=="Integer" or self.tokens[last_token][0]== "FLOAT"):   # -인숫자 앞에 숫자가 있다면 그것은 operator
          
          return True
        else:
          return False
      
    else:
      return False
  def getResult(self):
    stack = []
    check = False
    while(True):
      if self.current >= len(self.input):
        result = self.isMerged(stack)
        
        if check==True:
          if self.hiddenProblem(result):
            self.tokens.append(("Operator", ["-"]))
            self.tokens.append((result[0], result[1][1:]))
          else:
            self.tokens.append(result)
          break
        else:
          if len(stack)>0 and stack==['\n']:
            self.tokens.append(("Whitespace",['\n']))
          elif len(stack)>0 and stack!=['\n']:
            msg = "Error at:"+stack[0] + " line:"+str(self.line)
            self.tokens.clear()
            self.tokens.append(("Error", [msg]))
            return self.tokens
          
          break

      stack.append(self.input[self.current])
      self.current = self.current + 1

      result = self.isMerged(stack)



      if result[0] == "Error" or (result[0]=="wait" and not self.isDigit(self.input[self.current])):
        if check==False:  # 되는것을 하나도 찾지 못했다. 다시 스택에 집어넣으면서 찾아야한다.
          continue
        else:  # 끝났다! 다시 되돌아가서 확정시킨다.

          
          stack.pop()
          result = self.isMerged(stack)
          if result[0] =="Operator" and result[1][0]=='-' and self.input[self.current-1]=='0' and self.input[self.current]=='.':
            check=False
            stack.append(self.input[self.current-1])
            continue
          
          # if result[0]=="Integer" and self.isDigit(self.input[self.current-1]):
          #   self.tokens.append(("Error",self.line))
          # elif result[0]=="Integer" and self.isLetter(self.input[self.current-1]):
          #   self.tokens.append(("Error",self.line))

          if result[0]=="wait":
            check=False
            stack = []
          elif self.hiddenProblem(result):
            self.tokens.append(("Operator", ["-"]))
            self.tokens.append((result[0], result[1][1:]))
          else:
            self.tokens.append(self.isMerged(stack))

          self.start = self.current-1
          self.current = self.current -1
          stack = []
          check = False
      else:     #찾았다, 안되는 부분이 나올때까지 다시 반복한다.
        
        check = True
        continue
      
    if len(self.tokens)==0:
      return self.tokens
    else:
      return self.tokens


  def isMerged(self, stack):
    if self.isType(stack):
      return ("Type", stack)

    elif self.isSpecial(stack):
      return ("special statements", stack)

    elif self.isSignedInteger(stack):
      return ("Integer", stack)

    elif self.isBoolean(stack):
      return ("boolean", stack)

    elif self.isLiteralString(stack):
      print(stack)
      return ("LiteralString", stack)

    elif self.isFloating(stack) == "T6":
      return ("FLOAT", stack)

    elif self.isFloating(stack) == "T5" or self.isFloating(stack) == "T4" :
      return ("wait", stack)
    

    elif self.isIdentifier(stack):
      return ("ID", stack)
    
    elif self.isOperator(stack):
      return ("Operator", stack)

    elif self.isBitwise(stack):
      return ("Bitwise Operator", stack)
    
    elif self.isAssignment(stack):
      return ("ASSIGN", stack)
    
    elif self.isComparison(stack):
      return ("Comparison Operator", stack)
    
    elif self.isTerminating(stack):
      return ("terminating symbol", stack)
    
    elif self.isScope(stack):
      return ("scope symbol",stack )

    elif self.isIndication(stack):
      return ("indication symbol", stack)
    elif self.isSeparating(stack):
      return ("separating symbol", stack)
    elif self.isWhitespace(stack):
      return ("Whitespace", stack)

    else:
      msg = "Error at:"+stack[0] + " line:"+str(self.line)
      return ("Error", [msg])





  

  def isLetter(self, character):
    if ord(character)>=ord('a') and ord(character)<=ord('z'):
      return True
    elif ord(character)>=ord('A') and ord(character)<=ord('Z'):
      return True
    else:
      return False
#-----------------------------------------------------
  def isType(self, stack):   #1. 자료형
    state = 'T0'
    for i in stack:
      if i=='i' and state == 'T0':
        state = 'T1'
      elif i=='c' and state == 'T0':
        state = 'T2'
      elif i=='b' and state == 'T0':
        state = 'T3'
      elif i=='f' and state == 'T0':
        state = 'T4'
      elif i=='n' and state == 'T1':
        state = 'T5'
      elif i=='t' and state == 'T5':
        state = 'T13'
      elif i=='h' and state == 'T2':
        state = 'T6'
      elif i=='a' and state == 'T6':
        state = 'T9'
      elif i=='r' and state == 'T9':
        state = 'T13'
      elif i=='o' and state == 'T3':
        state = 'T7'
      elif i=='o' and state =='T7':
        state = 'T10'
      elif i== 'l' and state =='T10':
        state = 'T13'
      elif i== 'l' and state =='T4':
        state = 'T8'
      elif i== 'o' and state =='T8':
        state = 'T11'
      elif i== 'a' and state =='T11':
        state = 'T12'
      elif i== 't' and state =='T12':
        state = 'T13'
      else:
        state = 'false'
        break
    
    if state == 'T13':
      return True
    else:
      return False
    
  def isSignedInteger(self, stack): #2.부호있는 정수인지 판단
    state = 'T0'
    for i in stack:
      if i=='0' and state=='T0':
        state = 'T1'
      elif self.isDecimal(i) and state=='T0':
        state = 'T2'
      elif i=='-' and state =='T0':
        state = 'T3'
      elif self.isDigit(i) and state =='T2':
        state = 'T2'
      elif self.isDecimal(i) and state == 'T3':
        state = 'T2'
      else:
        state = 'false'
        break
    if state == 'T1' or state == 'T2':
      return True
    else:
      return False
    
  def isLiteralString(self, stack):   #3.문자열인지 판단
    state = 'T0'
    for i in stack:
      if (i=='''"''' or i== """'""") and state=="T0":
        state = 'T1'
      elif (i==' ' or self.isDigit(i) or self.isLetter(i)) and state=='T1':
        state = 'T1'
      elif (i=='''"''' or i== """'""") and state == "T1":
        state = 'T2'
      else:
        state = "false"
        break
    
    if state == 'T2':
      return True
    else:
      return False

  def isBoolean(self, stack): #4. 참 거짓인지 판단
    state = "T0"
    for i in stack:
      if i=='t' and state=='T0':
        state = 'T1'
      elif i=='r' and state == 'T1':
        state = 'T3'
      elif i=='u' and state == 'T3':
        state = 'T6'
      elif i=='f' and state == 'T0':
        state = 'T2'
      elif i=='a' and state == 'T2':
        state = 'T4'
      elif i=='l' and state == 'T4':
        state = 'T5'
      elif i=='s' and state == 'T5':
        state = 'T6'
      elif i=='e' and state == 'T6':
        state = 'T7'
      else:
        state = 'false'
        break
    
    if state == 'T7':
      return True
    else:
      return False
  def isFloating(self, stack):  #5. 부동소수
    state = "T0"
    for i in stack:
      if self.isDecimal(i) and state == 'T0':
        state = 'T1'
      elif self.isDigit(i) and state == 'T1':
        state = 'T1'
      elif i=='-' and state == 'T0':
        state = 'T2'
      elif self.isDecimal(i) and state == 'T2':
        state = 'T1'
      elif i=='0' and state =='T2':
        state = 'T3'
      elif i=='0' and state =='T0':
        state = 'T3'
      elif i=='.' and state == 'T1':
        state = 'T4'
      elif i=='.' and state == 'T3':
        state = 'T4'
      elif self.isDecimal(i) and state =='T4':
        state = 'T6'
      elif i=='0' and state == 'T4':
        state = 'T6'
      elif i=='0' and state == 'T5':
        state = 'T5'
      elif self.isDecimal(i) and state == 'T5':
        state = 'T6'
      elif i=='0' and state == 'T6':
        state = 'T5'
      elif self.isDecimal(i) and state == 'T6':
        state = 'T6'
      else:
        state = 'false'
        break
      
    if state == 'T6' :
      return "T6"
    elif state == 'T5' or state=='T4' :
      return "T5"
    else:
      return "False"
  
  def isIdentifier(self, stack):   #6. 변수와 함수의 이름
    state = 'T0'
    
    for i in stack:
      if (self.isLetter(i) or i=='_') and state == 'T0':
        state = 'T1'
      elif (self.isLetter(i) or self.isDigit(i) or i=='_') and state=='T1':
        state = 'T1'
      else:
        state = 'false'
        break
    
    if state == 'T1':
      return True
    else:
      return False

  def isSpecial(self, list):  #7. 특정 구문            !!!!!!!리스트를 문자열로 치환
    state = 'T0'
    stack = ''.join(list)
    if (stack == 'if' or stack == 'else' or stack == 'while' or stack=='for' or stack == 'return') and state=='T0':
      state = 'T1'
    else:
      state = 'false'
    
    if state == 'T1':
      return True
    else:
      return False
  
  def isOperator(self, stack): #8. 사칙연산
    state = 'T0'
    for i in stack:
      if i=='+' and state == 'T0':
        state = 'T1'
      elif i=='-' and state == 'T0':
        state = 'T1'
      elif i=='*' and state == 'T0':
        state = 'T1'
      elif i=='/' and state == 'T0':
        state = 'T1'
      else:
        state = 'false'
        break
    
    if state == 'T1':
      return True
    else:
      return False
  
  def isBitwise(self, stack): #9 비트연산자
    state = 'T0'
    for i in stack:
      if i=='<' and state =='T0':
        state = 'T1'
      elif i=='>' and state == 'T0':
        state = 'T3'
      elif (i=='&' or i=='|') and state == 'T0':
        state = 'T2'
      elif i=='<' and state =='T1':
        state = 'T2'
      elif i=='>' and state =='T3':
        state = 'T2'
      else:
        state = 'false'
        break
    
    if state == 'T2':
      return True
    else:
      return False

  def isAssignment(self, stack): #10 할당연산자
    state = 'T0'
    for i in stack:
      if i=='=' and state =='T0':
        state = 'T1'
      else:
        state = 'false'
        break

    if state == 'T1':
      return True
    else:
      return False\
  
  def isComparison(self, stack): #11 비교연산자
    state = 'T0'
    for i in stack:
      if (i=='<' or i=='>') and state=='T0':
        state = 'T1'
      elif (i=='!' or i=='=') and state == 'T0':
        state = 'T2'
      elif i=='a' and state == 'T0':
        state = 'T3'
      elif i=='=' and state == 'T1':
        state = 'T4'
      elif i=='=' and state == 'T2':
        state = 'T4'
      elif i=='n' and state == 'T3':
        state = 'T5'
      elif i=='d' and state == 'T5':
        state = 'T4'
      else:
        state = 'false'
        break
    
    if state == 'T1' or state == 'T4':
      return True
    else:
      return False
  
  def isTerminating(self, stack):  #12 문장 종결기호
    state = 'T0'
    for i in stack:
      if i==';' and state == 'T0':
        state = 'T1'
      else:
        state = 'false'
        break
    
    if state == 'T1':
      return True
    else:
      return False
    
  def isScope(self, stack):  #13 함수나 변수 범위
    state = 'T0'
    for i in stack:
      if (i=='{' or i== '}') and state == 'T0':
        state = 'T1'
      else:
        state = 'false'
    
    if state=='T1':
      return True
    else:
      return False
  
  def isIndication(self, stack):  #14 하나로 묶어주는 기호
    state = 'T0'
    for i in stack:
      if (i=='(' or i== ')') and state == 'T0':
        state = 'T1'
      else:
        state = 'false'
    
    if state=='T1':
      return True
    else:
      return False

  def isSeparating(self, stack): #15 함수의 인자들 구분해주는 기호
    state = 'T0'
    for i in stack:
      if i==',' and state == 'T0':
        state = 'T1'
      else:
        state = 'false'
        break
    
    if state == 'T1':
      return True
    else:
      return False

  def isWhitespace(self, stack): #16 띄어쓰기, 탭, 줄바꿈
    state = 'T0'
    for i in stack:
      if i=='\\' and state == 'T0':
        state = 'T1'
      elif i==' ' and state == 'T0':
        state = 'T2'
      elif (i=='t' or i=='n') and state =='T1':
        state = 'T2'
      else:
        state = 'false'
        break
    
    if state =='T2':
      return True
    else:
      return False



try:
  f = open("./input.c", 'rt', encoding = "utf-8")
  lineNumber = 1
  resultColumn1 = []      # 토큰의 타입을 담는 배열
  resultColumn2 = []      # 토큰의 input을 담는 배열
  lineColumn = []
  errorLine = 0        #에러가 생겼는지 확인
  while True:
    
    inputLine = f.readline()
    if inputLine =="":           #더이상 문장이 없으면 반복문 탈출
      
      break
    result = LexicalAnalyzer(inputLine, lineNumber).getResult()
    for i in range(len(result)):
      resultColumn1.append(result[i][0])
      lineColumn.append(lineNumber)
      if result[i][0] == "Error":   
        errorLine = lineNumber
        resultColumn2.append(''.join(result[i][1]))
      else:
        if result[i][0] == "LiteralString":
          print("원하는값: ", ''.join(result[i][1]))
        resultColumn2.append(''.join(result[i][1]))
      
    lineNumber = lineNumber+1
  
  data = {"Line Number": lineColumn,"Token Type": resultColumn1, "Token Input":resultColumn2}
  df = DataFrame(data)
  print(df)
  df.to_csv("./input.c"+".out",encoding='utf-8')
  print("Output파일이 완성되었습니다. 파일명: input.c.out")
  f.close()


except FileNotFoundError:
  
  print("해당 파일명이 없습니다.")






