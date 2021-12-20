import csv
import time
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.
    """
    neighbours_for_x = neighbors_for_person(source) 
    frontier = QueueFrontier()
    print("the source is: "+ source)
    print("the target is: "+ target)
    
    node_list = []
    node_hist = []
    movie_people_seen = []
    action_start= 0

    #adding nodes to the queue to loop over.
    for every in neighbours_for_x:
        current_node = Node(state=every, parent=("",source),action= action_start)
        frontier.add(current_node)


    #loop until we have found a link otherwise return none if the queue is empty.   
    while True: 
        if frontier.empty():
            return None

        #getting item from queue, adding the removed item to list of seen nodes.
        node = frontier.remove()
        node_hist.append((node.state[0],node.state[1],node.parent[0],node.parent[1]))
        movie_people_seen.append((node.state[0],node.state[1]))

        if node.state[1] == target:
            print("link found")
            node_list.append(node.state)

            #creating the list of nodes we passed through from source to get to the target.
            for every in node_hist:
                if every[0] == node.parent[0] and every[1] == node.parent[1]:
                    node_list.append((every[0], every[1]))
                    node = Node(state=(every[0],every[1]), parent=(every[2],every[3]), action = action_start)
                    if every[3] == source:
                        break
                        
            #returning the list.
            return node_list[::-1]

        node_neighbours = neighbors_for_person(node.state[1])
        #looping over neighbours if we didn't find a connection to the target yet.
        for every in node_neighbours:
            if every not in movie_people_seen:
                #keeping track of the depth of our search.
                action_new_number = node.action + 1 
                node_current = Node(state = every, parent= node.state, action= action_new_number)
                frontier.add(node_current)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
