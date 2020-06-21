import numpy as np
import pandas as pd
import os
import sys

class SyntaxAnalyzer:
  def __init__(self):
    self.stateStack = []  #스테이트가 담길 스택  
    self.inputStack = []  #input이 담길 스택
    self.startState = 0		#시작 스테이트
        
    self.inputResult =[] #텍스트 파일을 읽어올 리스트
    self.actionTable = 0 
    self.goToTable = 0
    self.cfgTable = 0
    
    self.setGrammarAndSLRTable()
    self.openFileAndGetText()
    self.SLRParcing()
        
  #모든 그래머와 slr Table의 정보를 읽어오기    
  def setGrammarAndSLRTable(self):
        
    # actionTable 읽기
    self.actionTable = pd.read_excel("./excel/actionTable.xlsx", 
                        sheet_name = 'Sheet1', 
                        na_values = 'NaN', 
                        thousands = ',', 
                        nrows = 88)
    
    # goToTable 읽기
    self.goToTable = pd.read_excel("./excel/goToTable.xlsx", # write your directory here
                        sheet_name = 'Sheet1', 
                        na_values = 'NaN', 
                        thousands = ',', 
                        nrows = 88)
    
    # cfgTable 읽기
    self.cfgTable = pd.read_excel("./excel/cfgTable.xlsx", # write your directory here
                        sheet_name = 'Sheet1', 
                        na_values = 'NaN', 
                        thousands = ',', 
                        nrows = 18)


  #lexical analyzer의 결과물을 읽어서 리스트에 넣는다
  def openFileAndGetText(self):
    try:
      f = open("./input.c.out", 'r', encoding = "utf-8")
      inputLine = f.readline()
      while True:
        
        inputLine = f.readline()
        inputLine=inputLine.split("\n")[0]
        
        if inputLine =="":           #더이상 문장이 없으면 반복문 탈출
          break
        elif inputLine != '"':
          lineNumber = inputLine.split(",")[1]
          tokenType = inputLine.split(",")[2]
          tokenInput = inputLine.split(",")[3]
          #인풋값 처리
          tokenType, tokenInput = tokenNameChange(tokenType,tokenInput)
          #에러 처리
          if(tokenType=="Error"):
            print("인풋 파일에 에러가 있습니다")
            break;
          
          #whitespace 부분 무시
          elif(tokenType!="Whitespace"):
            #하나씩 하나씩 추가
            self.inputResult.append({"lineNumber":lineNumber , "tokenType" : tokenType , "tokenInput" : tokenInput})
      f.close()
      #마지막 토큰 추가
      self.inputResult.append({"lineNumber":0 , "tokenType" : "$" , "tokenInput" : "$"})
    except FileNotFoundError:
      print("해당 파일명이 없습니다.")
      
  #SLR 파싱 부분
  def SLRParcing(self):
    #출발
    self.stateStack.append(self.startState)
    
    #현재 위치(Input result)
    pointer = 0
    topInput = 0
    
    #종료할때까지 반복
    while True :
      
      #다음 인풋 꺼내오기
      nextInput=self.inputResult[pointer]["tokenType"]
      #현재 스테이트
      topState = int(self.stateStack[-1])
      
      #처음일 경우 예외처리하고 처음 아니면 계속 제일 top 인풋 꺼내옴
      if(pointer!=0):
        topInput = self.inputStack[-1]
      
      #종료조건 1 : 올바른 코드일 조건 
      if(topInput == "CODE" and nextInput =="$"):
        print("옳은 코드입니다")
        break
      
      #엑션 테이블 룩업
      actionResult=self.actionTable[nextInput][topState]
      #종료조건 2 : 엑션테이블에 아무것도 없을 경우 NaN이 뜨기때문에 Nan은 float여서 이렇게 NaN인지 확인한다
      if(type(actionResult)==float):
        #에러 원인
        print("현재 스테이트: " + str(topState) + "에서 다음 인풋: " + nextInput + "으로 가는 엑션테이블이 없습니다" )
        #에러 위치
        print(str(self.inputResult[pointer]['lineNumber'])+ '번째 라인에 에러가 있습니다')
        break
      #엑션 테이블이 shift 일 경우
      elif(actionResult[0:1]=="S"):
        nextState=getNumFromS(actionResult)
        #스택에 스테이트와 인풋 추가
        self.stateStack.append(nextState)
        self.inputStack.append(nextInput)
        #포인터 한칸 움직임
        pointer = pointer + 1
      #엑션 테이블이 reduce 일 경우
      elif(actionResult[0:1]=="R"):
        num1, num2 = getNumFromR(actionResult)
        cfgResult=self.cfgTable[num2][num1-1]
        nextInput=self.cfgTable[0][num1-1]
        popNum=getPopNum(cfgResult)
        #reduce 되는 만큼 스택을 빼줌
        for i in range (0,popNum):
          self.stateStack.pop()
          self.inputStack.pop()
        topState = int(self.stateStack[-1])
        #goToTable 룩업
        goToResult=self.goToTable[nextInput][topState]
        nextState=int(goToResult.replace("STATE",""))
        #변환된 값 다시 스택에 넣어줌
        self.stateStack.append(nextState)
        self.inputStack.append(nextInput)
        

#reduce 일경우 얼만큼 stack에서 빼올지 결정하는 함수
def getPopNum(string):
    #엡실론인경우 빼지 않는다
    if(string == "ε"):
      return 0
    #개수만큼 뺀다
    else :
      result=len(string.split(" "))
      return result
#엑셀 문자에서 스테이트 숫자만 가져옴
def getNumFromS(string):
  result=int(string.replace("S",""))
  return result

#엑셀 문자에서 스테이트 숫자만 가져옴  
def getNumFromR(string):
  string=string.replace("R","")
  string=string.replace("(","")
  string=string.replace(")","")
  string1,string2=string.split("-")
  if(string1[0:1]=="0"):
    return int(string1[1:2]),int(string2)
  else: 
    return int(string1),int(string2)     
            
#lexicail analyzer 결과값 이번 cfg에 맞게 처리 
def tokenNameChange(tokenType,tokenInput):
  if(tokenType=="Whitespace"):
    tokenType = "Whitespace"          
  elif(tokenType=="Type"):
    tokenType = "vtype"
  elif(tokenType=="Integer"):
    tokenType = "num"
  elif(tokenType=="FLOAT"):
    tokenType = "float"
  elif(tokenType=="LiteralString"):
    tokenInput=tokenInput.replace('"',"")
    tokenInput=tokenInput.replace("'","")
    tokenType = "literal"
  elif(tokenType=="ID"):
    tokenType = "id"
  elif(tokenType=="separating symbol"):
    tokenInput= ","
    tokenType = "comma" 
  elif(tokenInput == "+" or tokenInput == "-"):
    tokenType = "addsub"
  elif(tokenInput== "*" or tokenInput == "/"):
    tokenType = "multdiv"
  elif(tokenInput== "="):
    tokenType = "assign"
  elif(tokenInput== ">" or tokenInput == "<" or tokenInput == "<=" or tokenInput == ">="):
    tokenType = "comp"           
  elif(tokenInput== ";"):
    tokenType = "semi"      
  elif(tokenInput== "("):
    tokenType = "lparen"          
  elif(tokenInput== ")"):
    tokenType = "rparen"
  elif(tokenInput== "{"):
    tokenType = "lbrace"      
  elif(tokenInput== "}"):
    tokenType = "rbrace"          
  elif(tokenInput== "if"):
    tokenType = "if"     
  elif(tokenInput== "else"):
    tokenType = "else"     
  elif(tokenInput== "while"):
    tokenType = "while"   
  elif(tokenInput== "for"):
    tokenType = "for" 
  elif(tokenInput== "return"):
    tokenType = "return"  
          
  return tokenType, tokenInput

def main():  
  SyntaxAnalyzer()
if __name__ == '__main__':
  main()



