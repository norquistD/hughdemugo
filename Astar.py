

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent # parent node
        self.position = position # (row, col)

        self.start_dist = 0 # distance from start node
        self.end_dist = 0 # distance from end node
        self.heuristic = 0 # total cost

    def __eq__(self, other):
        return self.position == other.position

class AStar:
    def __init__(self, matrix, start, end):
        self.matrix = matrix # 2D array
        self.start = start # (row, col)
        self.end = end # (row, col)
    
    def distance(self, a, b):
        # Manhattan distance
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbours(self, node):
        neighbours = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (node.position[0] + new_position[0], node.position[1] + new_position[1])
            if node_position[0] > (len(self.matrix) - 1) or node_position[0] < 0 or node_position[1] > (len(self.matrix[len(self.matrix)-1]) - 1) or node_position[1] < 0:
                continue
            if self.matrix[node_position[0]][node_position[1]] != 0:
                continue
            new_node = Node(node, node_position)
            neighbours.append(new_node)
    
        return neighbours
    
    def astar(self):
        open_nodes = []
        visited_nodes = []

        start_node = Node(None, self.start)
        start_node.start_dist = 0
        start_node.end_dist = self.distance(start_node.position, self.end)
        start_node.heuristic = start_node.end_dist

        history = []

        end_node = Node(None, self.end)

        open_nodes.append(start_node)

        while len(open_nodes) > 0: 
            best_node = min(open_nodes, key=lambda x: x.heuristic)
            open_nodes.remove(best_node)
            visited_nodes.append(best_node)

            if best_node == end_node: # found end node
                path = []
                current = best_node
                while current is not None: # backtrack to get path
                    path.append(current.position)
                    current = current.parent

                history.append(path)
                return path[::-1], history
            
            neighbours = self.get_neighbours(best_node)
            for neighbour in neighbours:
                if neighbour in visited_nodes:
                    continue

                neighbour.start_dist = best_node.start_dist + 1
                neighbour.end_dist = self.distance(neighbour.position, self.end)
                neighbour.heuristic = neighbour.start_dist + neighbour.end_dist


                for node in open_nodes:
                    if neighbour == node and neighbour.start_dist < node.start_dist:
                        node = neighbour
                
                if neighbour not in open_nodes:
                    #prepend
                    open_nodes.insert(0, neighbour)

            current_path = []
            current = best_node
            while current is not None:
                current_path.append(current.position)
                current = current.parent
            history.append(current_path)

            
        return None, history




