import pandas as pd
import math
import ast

def loadHoldTypesFromCSV(csv_filename):
    ''' Load hold types from a CSV file into a dictionary '''
    hold_types_dict = {}
    try:
        hold_types_df = pd.read_csv(csv_filename)
        for index, row in hold_types_df.iterrows():
            position = row['Hold']
            hold_type = row['Type']
            hold_types_dict[position] = hold_type
    except Exception as e:
        print(f"Error loading hold types: {str(e)}")
    return hold_types_dict

def getHolds(holds):
    ''' Returns the starting holds and usable holds '''
    startHolds = []
    usableHolds = []
    
    for hold in holds[1]:  # Iterate through the "rest of the holds" list
        hold_type = hold.get('Hold Type', None)
        if hold_type:
            diff = getDiffVals(hold_type)
            position = hold.get('Position', None)
            if position:
                usableHolds.append({position: diff})
    
    for hold in holds[0]:  # Iterate through the "start holds" list
        position = hold.get('Position', None)
        if position:
            startHolds.append(position)

    if len(startHolds) == 1:
        startHolds = [{'RH': startHolds[0]}, {'LH': startHolds[0]}]
    else:
        startHold1 = startHolds[0]
        startHold2 = startHolds[1]
        # Checks which is left and which is right, assumes that start is not crossed.
        if startHold1 > startHold2:
            startHolds = [{'RH': startHold1}, {'LH': startHold2}]
        else:
            startHolds = [{'LH': startHold1}, {'RH': startHold2}]

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

def calcDiff(dist, diff):
    distConst = 10
    diffConst = 1
    return (dist * distConst) + (diff * diffConst)

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
    maxSpan = 8  # Climbers max reach

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
                    if getDist(position, hold_loc) >= maxSpan:
                        hold_difficulty += 100  # Make moving out of span impossible

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
                if is_hold_to_left_or_right(prev_hold, curr_hold) != curr_hand:
                    cross_over += 1
                    totalCrossOvers += 1
                else:
                    if cross_over != 0:
                        cross_over -= 1

        if cross_over >= 2:
            consecutive_cross_overs += 1
            return calcSequence(startingHolds, startingUsableHolds, 'RH')

        last_hand = best_hand  # Update the last hand used

        if '18' in best_hold:
            break  # Break the loop if '18' is found and added to the sequence

    return sequence

def convertSeq(sequence, holdTypes):
    ''' Converts sequence to {(hold1, hold2, distance, holdType), ..., (hold1, hold2, distance, holdType)} '''
    moves = []
    for i in range(len(sequence) - 2):
        hold_A = list(sequence[i].values())[0]
        hold_B = list(sequence[i + 1].values())[0]
        hold_C = list(sequence[i + 2].values())[0]
        dist = getDist(hold_A, hold_C)

        # Look up hold types using hold positions
        holdType_A = holdTypes.get(hold_A, 'Unknown')
        holdType_B = holdTypes.get(hold_B, 'Unknown')
        holdType_C = holdTypes.get(hold_C, 'Unknown')

        move = (holdType_A, holdType_B, holdType_C, dist)
        moves.append(move)
    return moves
    
def main(holds,year):
    if year == '2016':
        holdTypes = loadHoldTypesFromCSV('holdType2016.csv')
    else:
        holdTypes = loadHoldTypesFromCSV('holdType2017.csv')
    '''
    holds = [[{'Position':'F6'},
              {'Position':'H5'}],
             [{'Position':'F8'},
              {'Position':'J11'},
              {'Position':'E13'},
              {'Position':'C16'},
              {'Position':'B18'}]]
    '''
    for hold in holds[0]:
        position = hold['Position']
        hold_type = holdTypes.get(position, 'Unknown')  # Get the hold type or 'Unknown' if not found
        hold['Hold Type'] = hold_type  # Assign the hold type to the hold

    for hold in holds[1]:
        position = hold['Position']
        hold_type = holdTypes.get(position, 'Unknown')  # Get the hold type or 'Unknown' if not found
        hold['Hold Type'] = hold_type  # Assign the hold type to the hold
        
    # Split the holds into startHolds and usableHolds
    startHolds, usableHolds = getHolds(holds)

    # Initialize the last_hand
    last_hand = 'LH'

    # Calculate the sequence
    sequence = calcSequence(startHolds, usableHolds, last_hand)

    moves = convertSeq(sequence,holdTypes)
    return moves
    

if __name__ == "__main__":
    main()
