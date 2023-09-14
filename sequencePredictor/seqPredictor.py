import pandas as pd
import math
import ast
import random 
########################## Test Sets #########################################
# POOOOOP
#sequence = [{'LH': 'G2'}, {'RH': 'K4'}]
#usableHolds = [{'I7': 7.0}, {'I8': 3.0}, {'A9': 6.5}, {'G11': 6.0}, {'F12': 4.0}, {'C14': 3.0}, {'E16': 7.5}, {'D18': 6.5}]
# REDLINE
sequence = [{'LH': 'F6'}, {'RH': 'H5'}]
usableHolds = [{'F8': 6.5}, {'J11':3.0},{'E13':3.0},{'C16':3.0},{'B18':3.0}]
# MB MASTERS OPEN 2
#sequence = [{'LH': 'B4'}, {'RH': 'E6'}]
#usableHolds = [{'F8':6.5},{'H10':3.0},{'G13':4.0},{'E13':3.0},{'G16':7.5},{'J18':7.5}]

##############################################################################
def getHolds(moves):
    ''' Returns the starting holds and usable holds '''
    startHolds = []
    usableHolds = []
    for hold in moves:
        diff = getDiffVals(hold['Hold Type'])
        if hold['IsStart']:
            startHolds.append(hold['Position'])
        else:
            usableHolds.append({hold['Position']:diff})
            
    if len(startHolds) == 1:
        startHolds = [{'RH':startHolds[0]},{'LH':startHolds[0]}]
    else: 
        startHold1 = startHolds[0]
        startHold2 = startHolds[1]
        # Checks which is left and which is right, assumes that start is not crossed.
        if startHold1 > startHold2:
            startHolds = [{'RH':startHold1},{'LH':startHold2}]
        else:
            startHolds = [{'LH':startHold1},{'RH':startHold2}]
    
    return (startHolds, usableHolds)

def getDiffVals(holdType):
    ''' Converts hold type to difficulty '''
    difficulties = {
            "Small Crimp": 9.0,
            "Medium Crimp": 7.5, 
            "Large Crimp": 6.5,
            "Pocket": 5.0,
            "Small Pocket": 9.0,
            "Jug": 3.0,
            "Small Pinch": 8.0,
            "Medium Pinch": 6.5,
            "Large Pinch": 4.0,
            "Slopy Pinch": 7.0,
            "Sloper": 7.5
        }
    return difficulties[holdType]
    
def getProblemNumber(problemName,df):
    ''' Gets the index related to the problem name '''
    return df.index[df['Name'] == problemName].tolist()

def getCoord(hold):
    ''' Converts A1 to 1,1 etc '''
    # Convert letter to column number
    x = ord(hold[0]) - ord('A') + 1
    # Convert number part to row number
    y = int(hold[1:])
    return (x, y)

def getDist(hold_A, hold_B):
    ''' Calculates the distance between holds (Euclidean distance) '''
    # This may need changing to centimeters if decide to go down the outdoor route
    holdA = getCoord(hold_A)
    holdB = getCoord(hold_B)
    squared_distances = [(p2 - p1) ** 2 for p1, p2 in zip(holdA, holdB)]
    sum_squared_distances = sum(squared_distances)
    distance = math.sqrt(sum_squared_distances)
    return distance

def getDiff(hold):
    return print(list(hold.values())[0])

def calcDiff(dist, diff):
    #distConst = 10
    #diffConst = 1
    #print(distConst)
    return (dist * distConst) + (diff * diffConst)

def setDistConst(val):
    global distConst
    distConst = val

def setDiffConst(val):
    global diffConst
    diffConst = val
    
def is_hold_to_left_or_right(hold_A, hold_B):
    ''' Checks if hold_A is to the left or right of hold_B '''
    coord_A = getCoord(hold_A)
    coord_B = getCoord(hold_B)
    
    # Compare x-coordinates of the holds
    if coord_A[0] < coord_B[0]:
        return "RH"
    elif coord_A[0] > coord_B[0]:
        return "LH"
    else:
        return "same"

def calcSequence(sequence, usableHolds, last_hand):
    startingUsableHolds = usableHolds[:]
    startingHolds = sequence[:]
    cross_over = 0  # Count cross-overs
    consecutive_cross_overs = 0  # Counter for consecutive cross-overs
    totalCrossOvers = 0
    maxSpan = 8 # Climbers max reach

    while True:
        min_diff = float('inf')  # Initialize min_diff to positive infinity
        best_hold = None
        best_hand = None

        for hold in sequence:
            hand = list(hold.keys())[0]
            currHold = hold[hand]
    
            for usableHold in usableHolds:
                hold_loc = list(usableHold.keys())[0]
                hold_diff = list(usableHold.values())[0]

                distance = getDist(currHold, hold_loc)
                hold_difficulty = calcDiff(distance, hold_diff)

                # Check if the hold is intended as a foot hold (lower than the current hold)
                if getCoord(hold_loc)[1] <= getCoord(currHold)[1]:
                    hold_difficulty += 100

                # Check if reaching hold exceeds the max span
                currHands = [list(item.values())[0] for item in sequence[-2:]]
                for position in currHands:
                    if getDist(position,hold_loc) >= maxSpan:
                        hold_difficulty += 100 # Make moving out of span impossible
                
                if hand != last_hand:  # Prioritize choosing a hold for the other hand
                    if hold_difficulty < min_diff:
                        min_diff = hold_difficulty
                        best_hold = hold_loc
                        best_hand = hand

        if not best_hold:
            # If no holds are available for the other hand, choose any hold
            for usableHold in usableHolds:
                hold_loc = list(usableHold.keys())[0]
                hold_diff = list(usableHold.values())[0]

                # Check if the hold is intended as a foot hold (lower than the current hold)
                if getCoord(hold_loc)[1] < getCoord(sequence[-1][best_hand])[1]:
                    continue

                if hold_diff < min_diff:
                    min_diff = hold_diff
                    best_hold = hold_loc
                    best_hand = list(usableHold.keys())[0]

        # Append the best hold to the sequence with the hand as the key
        sequence.append({best_hand: best_hold})
        usableHolds = [hold for hold in usableHolds if best_hold not in hold]

        # Check for cross-overs
        cross_over = 0  # Reset cross-over counter
        for i in range(1, len(sequence)):
            prev_hand = list(sequence[i - 1].keys())[0]
            prev_hold = sequence[i - 1][prev_hand]

            curr_hand = list(sequence[i].keys())[0]
            curr_hold = sequence[i][curr_hand]

            # Check for cross-over only if holds are intended for the other hand
            if curr_hand != last_hand:
                #print('true')
                if is_hold_to_left_or_right(prev_hold, curr_hold) != curr_hand:
                    cross_over += 1
                    totalCrossOvers +=1
                else:
                    #print('test')
                    if cross_over != 0:
                        cross_over -= 1

        if cross_over >= 2:
            #print('true')
            consecutive_cross_overs += 1
            return calcSequence(startingHolds,startingUsableHolds,'RH')

        last_hand = best_hand  # Update the last hand used

        if '18' in best_hold:
            break  # Break the loop if '18' is found and added to the sequence
    '''
    print("Final sequence:")
    print(sequence)
    print("Number of cross-overs:", cross_over)
    print("Consecutive cross-overs:", consecutive_cross_overs)
    print("Total Crossovers:", totalCrossOvers)
    '''
    return sequence


def convertSeq(sequence):
    ''' Converts sequence to {(hold1,hold2,distance,holdType),...,(distance,holdType)} '''
    pass
    
def main():
    df = pd.read_csv('Moonboard_Problems2_WithNames.csv')
    global usableHolds  # Use the global variable
    global sequence
    last_hand = 'LH'  # Initialize the last hand used to 'RH'
    # Initialise weights as equal
    setDiffConst(1)
    setDistConst(1)
    #calcSequence(sequence, usableHolds, last_hand)
    #print(df.loc[0, 'Moves'])
    problemName = 'WALK LIKE AN EGYPTIAN'
    testSet = [
    'POOOOOP', 'PATRICK YOU FOOL', 'GÄMSE #20', 'EASY FOR JACK', 'GOTIME',
    'RIGHT SIDE HEAT', 'VANS OFF THE WALL', 'GET STRONG OR DIE TRYING', 'LEFTY FLEX',
    'YELLOW GREY WOOD', 'GO BIGG', '7MOVES TO VICTORY', 'COMP-STYLE', '223345',
    'ROBS FIRST SET', 'NOT DIAGONAL', 'NIGHT FALL', 'FUN IF YOU\'RE SHORT', 'MATTHEW\'S CLIMB',
    'INDURANCE ONE']
    
    test_set_sequences = {
    'POOOOOP': [{'LH': 'G2'}, {'RH': 'K4'}, {'LH': 'I7'}, {'RH': 'I8'}, {'LH': 'G11'}, {'RH': 'F12'}, {'LH': 'C14'}, {'RH': 'E16'}, {'LH': 'D18'}],
    'PATRICK YOU FOOL': [{'LH': 'B3'}, {'RH': 'B4'}, {'RH': 'E6'}, {'LH': 'B8'}, {'RH': 'E11'}, {'LH': 'F12'}, {'RH': 'J13'}, {'LH': 'G16'}, {'RH': 'H18'}],
    'GÄMSE #20': [{'LH': 'F2'}, {'RH': 'G3'}, {'LH': 'G6'}, {'RH': 'H10'}, {'LH': 'C13'}, {'RH': 'D17'}, {'LH': 'A18'}],
    'GOTIME': [{'RH': 'F5'}, {'LH': 'F5'}, {'LH': 'C7'}, {'RH': 'G10'}, {'LH': 'C10'}, {'RH': 'D15'}, {'LH': 'A18'}],
    'RIGHT SIDE HEAT': [{'RH': 'F5'}, {'LH': 'F5'}, {'RH': 'I8'}, {'LH': 'H10'}, {'RH': 'K13'}, {'LH': 'I16'}, {'RH': 'K17'}, {'LH': 'H18'}],
    'VANS OFF THE WALL': [{'LH': 'I2'}, {'RH': 'K3'}, {'RH': 'I7'}, {'LH': 'F12'}, {'RH': 'E14'}, {'LH': 'B18'}],
    'GET STRONG OR DIE TRYING': [{'LH': 'D5'}, {'RH': 'H3'}, {'RH': 'G8'}, {'LH': 'E12'}, {'RH': 'J13'}, {'LH': 'J15'}, {'RH': 'H18'}],
    'LEFTY FLEX': [{'LH': 'B3'}, {'RH': 'F5'}, {'LH': 'B8'}, {'RH': 'E7'}, {'RH': 'F11'}, {'LH': 'C13'}, {'RH': 'D15'}, {'LH': 'A18'}],
    'YELLOW GREY WOOD': [{'LH': 'C4'}, {'RH': 'C4'}, {'LH': 'B8'}, {'RH': 'G9'}, {'LH': 'D11'}, {'RH': 'G14'}, {'LH': 'H16'}, {'RH': 'K18'}],
    'GO BIGG': [{'LH': 'B3'}, {'RH': 'F5'}, {'LH': 'D10'}, {'RH': 'J11'}, {'LH': 'I16'}, {'RH': 'J18'}],
    '7MOVES TO VICTORY': [{'LH': 'G4'}, {'RH': 'I5'}, {'LH': 'F7'}, {'RH': 'J11'}, {'LH': 'F10'}, {'RH': 'E14'}, {'LH': 'F15'}, {'RH': 'H18'}],
    'COMP-STYLE': [{'RH': 'A5'},{'LH': 'F3'}, {'LH': 'I8'}, {'RH': 'J8'}, {'LH': 'H11'}, {'RH': 'G14'}, {'LH': 'D18'}],
    '223345': [{'LH': 'D6'}, {'RH': 'G6'}, {'LH': 'F8'}, {'RH': 'H11'}, {'LH': 'D10'}, {'RH': 'G14'}, {'LH': 'F18'}],
    'ROBS FIRST SET': [{'LH': 'E3'}, {'RH': 'H5'}, {'LH': 'F8'}, {'RH': 'I8'}, {'LH': 'H11'}, {'RH': 'K11'}, {'RH': 'K15'}, {'LH': 'I16'}, {'RH': 'H18'}],
    'NOT DIAGONAL': [{'LH': 'B4'}, {'RH': 'B4'}, {'RH': 'E6'}, {'LH': 'C10'}, {'RH': 'G13'}, {'LH': 'F16'}, {'RH': 'H18'}],
    'NIGHT FALL': [{'LH': 'C4'}, {'RH': 'C4'}, {'LH': 'B9'}, {'RH': 'D12'}, {'LH': 'A15'}, {'RH': 'F18'}],
    'FUN IF YOU\'RE SHORT': [{'LH': 'E3'}, {'RH': 'H5'}, {'LH': 'F8'}, {'RH': 'J11'}, {'LH': 'E13'}, {'RH': 'F18'}],
    'MATTHEW\'S CLIMB': [{'LH': 'E3'}, {'RH': 'H5'}, {'LH': 'E8'}, {'RH': 'I10'}, {'LH': 'F12'}, {'RH': 'E14'}, {'LH': 'B16'}, {'RH': 'B18'}],
    'INDURANCE ONE': [{'LH': 'F4'}, {'RH': 'F4'}, {'RH': 'E8'}, {'LH': 'D9'}, {'RH': 'E11'}, {'LH': 'C13'}, {'RH': 'D15'}, {'LH': 'D17'}, {'RH': 'G17'}, {'LH': 'H17'}]}
    num_matches = 0
    iterations = 0
    epoch = 1
    bestDiff = None
    bestDist = None
    bestMatches = 0
    '''
    for i in range(epoch):
        
        #diff = random.uniform(0.1,10)
        #dist = random.uniform(0.1,10)
        
        setDiffConst(1)
        setDistConst(10)
        #setDiffConst(diff)
        #setDistConst(dist)
        num_matches = 0
        for problem in testSet:
            try:
                problemNumber = getProblemNumber(problem, df)
                moves = df.loc[problemNumber[0], 'Moves']
                holds = getHolds(ast.literal_eval(moves))
                startHolds = holds[0]
                usableHolds = holds[1]
                result_sequence = calcSequence(startHolds, usableHolds, last_hand)
        
                # Compare the calculated sequence to the test set sequence
                if result_sequence[2:] == test_set_sequences[problem][2:]:
                    #print(problem)
                    #print('result sequence: ',result_sequence)
                    #print('test sequence: ', test_set_sequences[problem])
                    num_matches += 1
                else:
                    print(problem)
                    print('result sequence: ',result_sequence)
                    print('test sequence: ', test_set_sequences[problem])
                iterations += 1

            except:
                continue
            
            if num_matches > bestMatches:
                bestMatches = num_matches
                bestDiff = diff
                bestDist = dist
            
            
        #print(num_matches)
        print(f"Number of matches: {num_matches}/{iterations}")
    #print(bestDiff,bestDist)
    #print(bestMatches)
    
    '''
    setDiffConst(1)
    setDistConst(10)
    problemNumber = getProblemNumber(problemName,df)
    moves = df.loc[problemNumber[0], 'Moves']
    #print(problemNumber[0])
    #oves = df.loc[0, 'Moves']
    #print(moves)
    holds = getHolds(ast.literal_eval(moves))
    startHolds = holds[0]
    usableHolds = holds[1]
    #print(usableHolds)
    #print(startHolds)
    print(calcSequence(startHolds, usableHolds, last_hand))
    
    
main()

