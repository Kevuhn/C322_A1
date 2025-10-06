import random


goalState = [0, 1, 2, 3, 4, 5, 6, 7, 8]
puzzleState = [0, 1, 2, 3, 4, 5, 6, 7, 8]

generatedStates = set()

while len(generatedStates) != 100: #loop until 100 states are in set
    random.shuffle(puzzleState) #generate random states
    disorderParameter = 0 #Reset DP to 0

    for i in range(len(puzzleState)):
        for j in range(i, len(puzzleState)):
            if puzzleState[j] != 0 and puzzleState[i] != 0: #make sure to ignore the blank space
                if puzzleState[j] < puzzleState[i]: #checks for disorder pairs
                    disorderParameter += 1

    if (disorderParameter % 2) == 0: #check if puzzle is solveable (if dp is even then solveable)
        if tuple(puzzleState) not in generatedStates: #convert list to tuple (list is unhashable, tuple is hashable) (when taking puzzle from set remember to convert back to list)
            generatedStates.add(tuple(puzzleState)) #add to generatedStates

print(len(generatedStates))