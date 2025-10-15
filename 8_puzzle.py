import random
import heapq
#from functions import *
def main():
    # Randomly generate 100 reachable states for 8_puzzle
    goalState = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    puzzleState = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    generatedStates = set()

    while len(generatedStates) < 100: #loop until 100 states are in set
        random.shuffle(puzzleState) #generate random states
        disorder_parameter = 0 #Reset DP to 0

        for i in range(len(puzzleState)):
            for j in range(i + 1, len(puzzleState)):
                if puzzleState[j] != 0 and puzzleState[i] != 0: #make sure to ignore the blank space
                    if puzzleState[j] < puzzleState[i]: #checks for disorder pairs
                        disorder_parameter += 1

        if disorder_parameter % 2 == 0: #check if puzzle is solveable (if dp is even then solveable)
            # convert list to tuple (list is unhashable, tuple is hashable) (when taking puzzle from set remember to convert back to list)
            generatedStates.add(tuple(puzzleState)) #add to generatedStates

    print(len(generatedStates), "puzzles have been generated\n")

    # Define the movesets and h1 and h2
    moves = {
        0: [1, 3],
        1: [0, 2, 4],
        2: [1, 5],
        3: [0, 4, 6],
        4: [1, 3, 5, 7],
        5: [2, 4, 8],
        6: [3, 7],
        7: [4, 6, 8],
        8: [5, 7]
    } # each line indicates the position index of the blank tile and its possible moves
    # for example: if the blank is in position 0 (top left corner) it can only move to the right [index 1] or down [index 3]

    def h1(state): # h1: number of misplaced tiles (excluding the blank tile)
        misplaced = 0  # counter for misplaced tiles
        for i in range(9):  # loop through all 9 positions
            if state[i] != 0 and state[i] != goalState[i]:  # ignore blank and count wrong tiles
                misplaced += 1  # increase counter
        return misplaced 

    def h2(state): # h2: total Manhattan distance (sum of distances of tiles from goal position)
        distance = 0
        for i in range(9):
            if state[i] != 0: # ignore the blank tile
                x1, y1 = divmod(i, 3) # get the current tile (row, col)
                x2, y2 = divmod(goalState.index(state[i]), 3) # get the goal (row, col)
                distance += abs(x1 - x2) + abs(y1 - y2) # add the tile's distance to goal
        return distance

    def h3(state): # h3: Manhattan distance + 2 * number of linear conflicts (adds extra penalty if two tiles are blocking each other in the same row/column.)
        manhattan = h2(state)
        linear_conflicts = 0

        # Row conflicts
        for row in range(3):
            # tiles in this row (value, current_col, goal_row, goal_col)
            row_tiles = []
            for col in range(3):
                val = state[row*3 + col]
                if val == 0:
                    continue # ignore blank tile
                gr, gc = divmod(goalState.index(val), 3)
                if gr == row:  # only consider tiles whose goal is in this row
                    row_tiles.append((val, col, gr, gc))
            # compare tiles in this row
            for i in range(len(row_tiles)):
                for j in range(i+1, len(row_tiles)):
                    # If tile i and j are reversed (goal_col_i > goal_col_j),
                    # it means they are in linear conflict.
                    _, col_i, _, goal_col_i = row_tiles[i]
                    _, col_j, _, goal_col_j = row_tiles[j]
                    if goal_col_i > goal_col_j:
                        linear_conflicts += 1

        # Column conflicts, same logic as row conflicts
        for col in range(3):
            col_tiles = []
            for row in range(3):
                val = state[row*3 + col]
                if val == 0:
                    continue
                gr, gc = divmod(goalState.index(val), 3)
                if gc == col:
                    col_tiles.append((val, row, gr, gc))
            for i in range(len(col_tiles)):
                for j in range(i+1, len(col_tiles)):
                    _, row_i, goal_row_i, _ = col_tiles[i]
                    _, row_j, goal_row_j, _ = col_tiles[j]
                    if goal_row_i > goal_row_j:
                        linear_conflicts += 1

        return manhattan + 2 * linear_conflicts

    def get_neighbours(state): # get the next states by moving the blank tile
        neighbours = []
        zero_idx = state.index(0) # find blank tile
        for move_pos in moves[zero_idx]:
            new_state = state.copy() # make copt of state
            new_state[zero_idx], new_state[move_pos] = new_state[move_pos], new_state[zero_idx] # swap blank tile with the target position
            neighbours.append(new_state) # add to neighbours list
        return neighbours


    # Implement the A* Algorithm
    def a_star_algorithm(start_state, heuristic):
        priority = [] # min heap (priority queue)
        heapq.heappush(priority, (0, start_state)) # push function: f(n) = g(n) + h(n) and start at g = 0
        parents = {}
        g_func = {tuple(start_state): 0} # g(n): cost to reach node from the start node
        nodes_expanded = 0

        while priority: # loop until there are no more nodes
            f, current = heapq.heappop(priority) # get the node with lowest f
            nodes_expanded += 1 # increase expanded nodes counter

            if current == goalState: # if the goal is reached we need to get the path length by tracing the parent nodes back
                steps = 0
                while tuple(current) in parents:
                    current = parents[tuple(current)]
                    steps += 1
                return steps, nodes_expanded

            for neighbour in get_neighbours(current): # find all next valid moves
                poss_g = g_func[tuple(current)] + 1 # the cost from start to neighbour
                neighbour_t = tuple(neighbour) # convert neighbour to tuple

                if neighbour_t not in g_func or poss_g < g_func[neighbour_t]: # if the neighbour hasn't been visited or there is a shorter path found
                    parents[neighbour_t] = current # record the path
                    g_func[neighbour_t] = poss_g # update the cost
                    f_func = poss_g + heuristic(neighbour) # this is f(n) = g(n) + h(n)
                    heapq.heappush(priority, (f_func, neighbour)) # push to the priority queue

        return

    # store results in a list
    results = []
    count = 1
    for state in generatedStates:
        state_list = list(state)

        steps_h1, nodes_h1 = a_star_algorithm(state_list, h1)
        steps_h2, nodes_h2 = a_star_algorithm(state_list, h2)
        steps_h3, nodes_h3 = a_star_algorithm(state_list, h3)

        results.append([count, steps_h1, nodes_h1, steps_h2, nodes_h2, steps_h3, nodes_h3])
        count += 1

    print("{:<8} {:<12} {:<18} {:<12} {:<18} {:<12} {:<18}".format(
        "Puzzle", "Steps(h1)", "NodesExpanded(h1)", "Steps(h2)", "NodesExpanded(h2)", "Steps(h3)", "NodesExpanded(h3)"
    ))
    print("")

    for row in results:
        print("{:<8} {:<12} {:<18} {:<12} {:<18} {:<12} {:<18}".format(*row))

if __name__ == "__main__":
    main()