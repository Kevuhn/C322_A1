import random
import heapq

def main():
    # For 24-puzzle, we'll use starting states that are more challenging
    # but still solvable within reasonable time
    
    goalState = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    
    # Define the movesets for 5x5 grid (24-puzzle)
    moves = {
        0: [1, 5],
        1: [0, 2, 6],
        2: [1, 3, 7],
        3: [2, 4, 8],
        4: [3, 9],
        5: [0, 6, 10],
        6: [1, 5, 7, 11],
        7: [2, 6, 8, 12],
        8: [3, 7, 9, 13],
        9: [4, 8, 14],
        10: [5, 11, 15],
        11: [6, 10, 12, 16],
        12: [7, 11, 13, 17],
        13: [8, 12, 14, 18],
        14: [9, 13, 19],
        15: [10, 16, 20],
        16: [11, 15, 17, 21],
        17: [12, 16, 18, 22],
        18: [13, 17, 19, 23],
        19: [14, 18, 24],
        20: [15, 21],
        21: [16, 20, 22],
        22: [17, 21, 23],
        23: [18, 22, 24],
        24: [19, 23]
    }

    def is_solvable(state):
        # count inversions ignoring 0
        arr = [n for n in state if n != 0]
        inversions = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
        blank_row = 5 - (state.index(0) // 5)  # row from bottom (1-indexed)
        # for odd grid (5x5): solvable if inversion count is even
        return inversions % 2 == 0
    
    # Generate 100 starting states by making more moves from the goal state
    generatedStates = set()
    while len(generatedStates) < 100:
        candidate = goalState.copy()
        for _ in range(random.randint(50, 80)):  # deeper scrambles
            zero = candidate.index(0)
            move = random.choice(moves[zero])
            candidate[zero], candidate[move] = candidate[move], candidate[zero]
        if is_solvable(candidate):
            generatedStates.add(tuple(candidate))

    print(len(generatedStates), "puzzles have been generated (challenging starting states - 100 puzzles)\n")
    print("Starting A* algorithm execution...")
    
    def h1(state): # h1: number of misplaced tiles (excluding the blank tile)
        misplaced = 0
        for i in range(25):
            if state[i] != 0 and state[i] != goalState[i]:
                misplaced += 1
        return misplaced 

    def h2(state): # h2: total Manhattan distance
        distance = 0
        for i in range(25):
            if state[i] != 0:
                x1, y1 = divmod(i, 5)
                x2, y2 = divmod(goalState.index(state[i]), 5)
                distance += abs(x1 - x2) + abs(y1 - y2)
        return distance

    def h3(state): # h3: Manhattan distance + linear conflicts
        manhattan = h2(state)
        linear_conflicts = 0

        # Row conflicts
        for row in range(5):
            row_tiles = []
            for col in range(5):
                val = state[row*5 + col]
                if val == 0:
                    continue
                gr, gc = divmod(goalState.index(val), 5)
                if gr == row:
                    row_tiles.append((val, col, gr, gc))
            
            for i in range(len(row_tiles)):
                for j in range(i+1, len(row_tiles)):
                    _, col_i, _, goal_col_i = row_tiles[i]
                    _, col_j, _, goal_col_j = row_tiles[j]
                    if goal_col_i > goal_col_j:
                        linear_conflicts += 1

        # Column conflicts
        for col in range(5):
            col_tiles = []
            for row in range(5):
                val = state[row*5 + col]
                if val == 0:
                    continue
                gr, gc = divmod(goalState.index(val), 5)
                if gc == col:
                    col_tiles.append((val, row, gr, gc))
            
            for i in range(len(col_tiles)):
                for j in range(i+1, len(col_tiles)):
                    _, row_i, goal_row_i, _ = col_tiles[i]
                    _, row_j, goal_row_j, _ = col_tiles[j]
                    if goal_row_i > goal_row_j:
                        linear_conflicts += 1

        return manhattan + 2 * linear_conflicts

    def get_neighbours(state):
        neighbours = []
        zero_idx = state.index(0)
        for move_pos in moves[zero_idx]:
            new_state = state.copy()
            new_state[zero_idx], new_state[move_pos] = new_state[move_pos], new_state[zero_idx]
            neighbours.append(new_state)
        return neighbours

    def a_star_algorithm(start_state, heuristic):
        priority = []
        heapq.heappush(priority, (0, start_state))
        parents = {}
        g_func = {tuple(start_state): 0}
        nodes_expanded = 0
        max_nodes = 500000  # Higher limit for more complex puzzles

        while priority and nodes_expanded < max_nodes:
            f, current = heapq.heappop(priority)
            nodes_expanded += 1

            if current == goalState:
                steps = 0
                while tuple(current) in parents:
                    current = parents[tuple(current)]
                    steps += 1
                return steps, nodes_expanded

            for neighbour in get_neighbours(current):
                poss_g = g_func[tuple(current)] + 1
                neighbour_t = tuple(neighbour)

                if neighbour_t not in g_func or poss_g < g_func[neighbour_t]:
                    parents[neighbour_t] = current
                    g_func[neighbour_t] = poss_g
                    f_func = poss_g + heuristic(neighbour)
                    heapq.heappush(priority, (f_func, neighbour))

        if nodes_expanded >= max_nodes:
            return 999999, nodes_expanded
        return

    # Solve puzzles
    results = []
    count = 1
    total_states = len(generatedStates)
    
    for state in generatedStates:
        print(f"Processing puzzle {count}/{total_states}...")
        state_list = list(state)

        steps_h1, nodes_h1 = a_star_algorithm(state_list, h1)
        steps_h2, nodes_h2 = a_star_algorithm(state_list, h2)
        steps_h3, nodes_h3 = a_star_algorithm(state_list, h3)

        results.append([count, steps_h1, nodes_h1, steps_h2, nodes_h2, steps_h3, nodes_h3])
        print(f"  Puzzle {count} completed: h1({steps_h1} steps, {nodes_h1} nodes), h2({steps_h2} steps, {nodes_h2} nodes), h3({steps_h3} steps, {nodes_h3} nodes)")
        count += 1

    print("\n" + "="*100)
    print("RESULTS TABLE FOR 24-PUZZLE (PART III) - 100 PUZZLES")
    print("="*100)
    print("{:<8} {:<12} {:<18} {:<12} {:<18} {:<12} {:<18}".format(
        "Puzzle", "Steps(h1)", "NodesExpanded(h1)", "Steps(h2)", "NodesExpanded(h2)", "Steps(h3)", "NodesExpanded(h3)"
    ))
    print("-" * 100)

    for row in results:
        print("{:<8} {:<12} {:<18} {:<12} {:<18} {:<12} {:<18}".format(*row))

    # Calculate and display statistics
    print("\n" + "="*80)
    print("STATISTICS FOR 24-PUZZLE (100 PUZZLES)")
    print("="*80)
    
    # Filter out failed solutions for statistics
    successful_results = [r for r in results if r[1] != 999999]
    
    if successful_results:
        avg_steps_h1 = sum(row[1] for row in successful_results) / len(successful_results)
        avg_nodes_h1 = sum(row[2] for row in successful_results) / len(successful_results)
        avg_steps_h2 = sum(row[3] for row in successful_results) / len(successful_results)
        avg_nodes_h2 = sum(row[4] for row in successful_results) / len(successful_results)
        avg_steps_h3 = sum(row[5] for row in successful_results) / len(successful_results)
        avg_nodes_h3 = sum(row[6] for row in successful_results) / len(successful_results)
        
        print(f"Average Steps - h1: {avg_steps_h1:.2f}, h2: {avg_steps_h2:.2f}, h3: {avg_steps_h3:.2f}")
        print(f"Average Nodes Expanded - h1: {avg_nodes_h1:.2f}, h2: {avg_nodes_h2:.2f}, h3: {avg_nodes_h3:.2f}")
        
        min_steps_h1 = min(row[1] for row in successful_results)
        max_steps_h1 = max(row[1] for row in successful_results)
        min_steps_h2 = min(row[3] for row in successful_results)
        max_steps_h2 = max(row[3] for row in successful_results)
        min_steps_h3 = min(row[5] for row in successful_results)
        max_steps_h3 = max(row[5] for row in successful_results)
        
        print(f"\nStep Range - h1: {min_steps_h1}-{max_steps_h1}, h2: {min_steps_h2}-{max_steps_h2}, h3: {min_steps_h3}-{max_steps_h3}")
        
        # Performance analysis
        print("\nPERFORMANCE ANALYSIS:")
        print("-" * 40)
        print("h1 (Misplaced Tiles): Simplest heuristic, generally expands more nodes")
        print("h2 (Manhattan Distance): More informed than h1, typically better performance")
        print("h3 (Manhattan + Linear Conflicts): Most informed heuristic, should show best performance")
        
        # Show which heuristic performed best
        if avg_nodes_h3 <= avg_nodes_h2 and avg_nodes_h3 <= avg_nodes_h1:
            print(f"\nBEST PERFORMING HEURISTIC: h3 (Manhattan + Linear Conflicts)")
            print(f"  - Expanded {avg_nodes_h3:.1f} nodes on average")
            print(f"  - {avg_nodes_h1/avg_nodes_h3:.1f}x better than h1")
            print(f"  - {avg_nodes_h2/avg_nodes_h3:.1f}x better than h2")
        elif avg_nodes_h2 <= avg_nodes_h1:
            print(f"\nBEST PERFORMING HEURISTIC: h2 (Manhattan Distance)")
            print(f"  - Expanded {avg_nodes_h2:.1f} nodes on average")
            print(f"  - {avg_nodes_h1/avg_nodes_h2:.1f}x better than h1")
        else:
            print(f"\nBEST PERFORMING HEURISTIC: h1 (Misplaced Tiles)")
            print(f"  - Expanded {avg_nodes_h1:.1f} nodes on average")
            
        print(f"\nSuccessfully solved {len(successful_results)}/{len(results)} puzzles")
        
        # Additional insights
        print("\nADDITIONAL INSIGHTS:")
        print("-" * 40)
        print("• The 24-puzzle has 25! approximately 1.55 x 10^25 possible states")
        print("• This makes it significantly more complex than the 8-puzzle (9! approximately 362,880 states)")
        print("• The computational complexity grows exponentially with puzzle size")
        print("• Heuristic quality becomes more critical as puzzle size increases")
        print("• Results based on 100 puzzles provide more statistically robust conclusions")
        
    else:
        print("No puzzles were successfully solved within the node limit.")
        print("This demonstrates the computational complexity of the 24-puzzle.")

if __name__ == "__main__":
    main()