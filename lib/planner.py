from lib.logger import Log
class Action:
   
    STACK = "stack"
    UNSTACK = "unstack"
    PICKUP = "pickup"
    PUTDOWN = "putdown"
    SPACE = " "

    @staticmethod
    def getActions():
       
        return [Action.STACK,
                Action.UNSTACK,
                Action.PICKUP,
                Action.PUTDOWN]


class Predicate:
    
    ON = "on"
    CLEAR = "clear"
    ARM_EMPTY = "arm_empty"
    HOLDING = "holding"
    ON_TABLE = "on_table"
    SPACE = " "

    @staticmethod
    def getPredicates():
        
        return [Predicate.ON,
                Predicate.CLEAR,
                Predicate.ARM_EMPTY,
                Predicate.HOLDING,
                Predicate.ON_TABLE]


class Planner:
   
    def __init__(self, verbose=False):
        self.__actions = Action.getActions()
        self.__predicates = Predicate.getPredicates()
        self.__goalState = list()
        self.__startState = list()
        self.__currentStack = list()
        self.__planningStack = list()
        self.__plan = list()
        self.__sep = "^"
        self.__verbose = verbose

    def __preconditionsStack(self, b):
        
        self.__planningStack.append(''.join([Predicate.CLEAR, Predicate.SPACE, str(b)]))

    def __preconditionsUnStack(self, a,b):
       
        self.__planningStack.append(''.join([Predicate.ON, Predicate.SPACE, str(a), Predicate.SPACE, str(b)]))
        self.__planningStack.append(''.join([Predicate.CLEAR, Predicate.SPACE, str(a)]))

    def __preconditionsPickUp(self, a):
        
        self.__planningStack.append(''.join([Predicate.ARM_EMPTY]))
        self.__planningStack.append(''.join([Predicate.ON_TABLE, Predicate.SPACE, str(a)]))

    def __preconditionsPutDown(self, a):
       
        self.__planningStack.append(''.join([Predicate.HOLDING, Predicate.SPACE, str(a)]))

    def __actionOn(self, a,b):
       
        self.__planningStack.append(''.join([Action.STACK, Action.SPACE, str(a), Action.SPACE, str(b)]))
        self.__preconditionsStack(b)

    def __actionOnTable(self, a):
        
        self.__planningStack.append(''.join([Action.PUTDOWN, Action.SPACE, str(a)]))
        self.__preconditionsPutDown(a)

    def __actionClear(self, a):
       
        check = ''.join([Predicate.ON, Predicate.SPACE])
        temp = list()

        for predicate in self.__currentStack:
            if check in predicate:
                temp = predicate.split()

                if temp[2] == a:
                    break

        b = str(temp[1])
        self.__planningStack.append(''.join([Action.UNSTACK, Action.SPACE, str(b), Action.SPACE, str(a)]))
        self.__preconditionsUnStack(b, a)

    def __actionHolding(self, a):
        
        check = ''.join([Predicate.ON_TABLE, Predicate.SPACE, str(a)])

        if check in self.__currentStack:
            self.__planningStack.append(''.join([Action.PICKUP, Action.SPACE, str(a)]))
            self.__preconditionsPickUp(a)
            return

        check = ''.join([Predicate.ON, Predicate.SPACE])
        temp = list()

        for predicate in self.__currentStack:
            if check in predicate:
                temp = predicate.split()

                if temp[1] == a:
                    break
            else:
                return

        b = str(temp[2])
        self.__planningStack.append(''.join([Action.UNSTACK, Action.SPACE, str(b), Action.SPACE, str(a)]))
        self.__preconditionsUnStack(b, a)

    def __actionArmEmpty(self):
       
        Log.d(f"Arm is empty :: {self.__planningStack}")
        exit(1)

    def __effectStack(self, a, b):
       
        # self.__currentStack.remove(''.join([Predicate.HOLDING, Predicate.SPACE, str(x)]))
        self.__currentStack.remove(''.join([Predicate.CLEAR, Predicate.SPACE, str(b)]))

        self.__currentStack.append(''.join([Predicate.ON, Predicate.SPACE, str(a), Predicate.SPACE, str(b)]))
        self.__currentStack.append(''.join([Predicate.CLEAR, Predicate.SPACE, str(a)]))
        self.__currentStack.append(Predicate.ARM_EMPTY)

    def __effectUnStack(self, a, b):
        
        self.__currentStack.remove(''.join([Predicate.ON, Predicate.SPACE, str(a), Predicate.SPACE, str(b)]))
        # self.__currentStack.remove(Predicate.ARM_EMPTY)

        self.__currentStack.append(''.join([Predicate.HOLDING, Predicate.SPACE, str(a)]))
        self.__currentStack.append(''.join([Predicate.CLEAR, Predicate.SPACE, str(b)]))

    def __effectPickUp(self, a):
        
        self.__currentStack.remove(Predicate.ARM_EMPTY)
        self.__currentStack.remove(''.join([Predicate.ON_TABLE, Predicate.SPACE,Predicate.CLEAR,Predicate.SPACE, str(a)]))

        self.__currentStack.append(''.join([Predicate.HOLDING, Predicate.SPACE, str(a)]))

    def __effectPutDown(self, a):
        
        self.__currentStack.remove(''.join([Predicate.HOLDING, Predicate.SPACE, str(a)]))

        self.__currentStack.append(Predicate.ARM_EMPTY)
        self.__currentStack.append(''.join([Predicate.ON_TABLE, Predicate.SPACE, str(a)]))

    def getPlan(self, startState: str, goalState: str):
       
        self.__startState = startState.split(self.__sep)
        self.__goalState = goalState.split(self.__sep)
        self.__currentStack = self.__startState.copy()

        # creating the plan stack
        for predicate in self.__goalState:
            self.__planningStack.append(predicate)

        # running for the stack empty
        while len(self.__planningStack) > 0:
            if self.__verbose:
                Log.d(f"Planning Stack :: {self.__planningStack}")
                Log.d(f"Current Stack :: {self.__currentStack}")

            top = self.__planningStack.pop()
            temp = top.split()

            if temp[0] in self.__predicates:
                if top in self.__currentStack:
                    continue

                else:
                    # if it is a predicate
                    if temp[0] == Predicate.ON:
                        self.__actionOn(temp[1], temp[2])

                    elif temp[0] == Predicate.ON_TABLE:
                        self.__actionOnTable(temp[1])

                    elif temp[0] == Predicate.CLEAR:
                        self.__actionClear(temp[1])

                    elif temp[0] == Predicate.HOLDING:
                        self.__actionHolding(temp[1])

                    elif temp[0] == Predicate.ARM_EMPTY:
                        self.__actionArmEmpty()

            if temp[0] in self.__actions:
                # if it is an action
                if temp[0] == Action.STACK:
                    self.__effectStack(temp[1], temp[2])

                elif temp[0] == Action.UNSTACK:
                    self.__effectUnStack(temp[1], temp[2])

                elif temp[0] == Action.PICKUP:
                    self.__effectPickUp(temp[1])

                elif temp[0] == Action.PUTDOWN:
                    self.__effectPutDown(temp[1])

                # add processed action
                self.__plan.append(top)

        if self.__verbose:
            Log.d(f"Final stack :: {self.__currentStack}")

        return self.__plan
