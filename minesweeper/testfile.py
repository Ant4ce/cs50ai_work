
 #1
        self.moves_made.add(cell) 
        #2
        self.mark_safe(cell)
        #3
        new_knowledge_cells = set() 
        

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i,j) in self.safes:
                        continue
                    if (i,j) in self.mines:
                        count -= 1
                        continue
                    new_knowledge_cells.add((i,j))

        current_sentence = Sentence(new_knowledge_cells, count)
        self.knowledge.append(current_sentence) 
        #4&5
        known_mines_set = set()
        known_safes_set = set()

        for sentence in self.knowledge:
            for x in sentence.known_mines():
                known_mines_set.add(x)
            for y in sentence.known_safes():
                known_safes_set.add(y)

        for cell in known_mines_set:
            self.mark_mine(cell)
        for cell in known_safes_set:
            self.mark_safe(cell)


        for each in self.knowledge:
            for every in self.knowledge:
                if each.cells < every.cells:
                    # adding new sentences based on inference
                    new_set = every.cells.difference(each.cells)
                    new_count = every.count - each.count
                    new_sentence = Sentence(new_set, new_count)
                    if new_sentence is not None and new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)

