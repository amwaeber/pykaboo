class DXFPoint:
    def __init__(self):
        self.items = []

    def add(self, coordinate, handle):
        self.items.append([coordinate, handle])

    def remove(self, index):
        try:
            del self.items[index]
        except IndexError as e:
            print(e)

    def coordinates(self):
        return [item[0] for item in self.items]

    def handles(self):
        return [item[0] for item in self.items]

