
CLEARANCE = 0
STONE = 1
FISH = 2
SHRIMP = 3

class LifeGame(object):
    """
    Class for Game life
    """
    table = []

    def __init__(self, table: list[list[int]] ):
        self.table = table # todo: сделать проверку на корректность

    def __get_count_of(self, i: int, j: int, type: int) -> int:
        count = 0
        for cur_i in range(max(i - 1, 0), min(i + 2, len(self.table))):
            for cur_j in range(max(j - 1, 0), min(j + 2, len(self.table[cur_i]))):
                count += 1 if self.table[cur_i][cur_j] == type  else 0
        return count - (1 if self.table[i][j] == type else 0)

    def get_next_generation(self) -> list[list[int]]:
        new_table = []
        for i in range(len(self.table)):
            new_line = []
            for j in range(len(self.table[i])):
                if self.table[i][j] == CLEARANCE:
                    if  self.__get_count_of(i, j, FISH) == 3:
                        new_line.append(FISH)
                    elif self.__get_count_of(i, j, SHRIMP) == 3:
                        new_line.append(SHRIMP)
                    else:
                        new_line.append(CLEARANCE)
                elif self.table[i][j] == STONE:
                    new_line.append(STONE)
                elif self.table[i][j] == FISH:
                    if 3 >= self.__get_count_of(i, j, FISH) >=2:
                        new_line.append(FISH)
                    else:
                        new_line.append(CLEARANCE)
                elif self.table[i][j] == SHRIMP:
                    if 3 >= self.__get_count_of(i, j, SHRIMP) >= 2:
                        new_line.append(SHRIMP)
                    else:
                        new_line.append(CLEARANCE)
            new_table.append(new_line)
        self.table = new_table
        return self.table
