import csv
class Data(object):

    def __init__(self, filename):
        self.__num_columns = 0
        self.__columns = []
        self.__column_index_dict = {}
        self.__reader = None
        self.__handle = None
        self.__filename = filename

    def __del__(self):
        if self.__handle:
            self.__handle.close()

    def __iter__(self):
        return self

    def _make_field_dict(self, csv_row):

        place_dict = {}
        index = 0
        for item in csv_row:
            place_dict[item] = index
            index += 1
        return place_dict

    def open_csv(self):
        if self.__handle:
            self.__handle.close()
        self.__handle = open(self.__filename, "r")
        self.__reader = csv.reader(self.__handle)
        first_line = self.__reader.next()
        self.__column_index_dict = self._make_field_dict(first_line)
        self.__columns = first_line
        self.__num_columns = len(self.__columns)
        return self.__reader

    def _row_to_dict(self, row):
        return_dict = {}
        for x in range(self.__num_columns):
            return_dict[self.__columns[x]] = row[x] 
        return return_dict

    def next(self):
        return self._row_to_dict(self.__reader.next())

    def columns(self):
        self.open_csv()
        return self.__columns

    def all_values(self, key, target=None):
        self.open_csv()
        vals = []
        for row in self:
            if not target or row["Cover_Type"] == target:
                val = row[key]
                if val not in vals:
                    vals.append(val)
        return vals

    def train(self, model, target_keyname="Cover_Type"):
        self.open_csv()
        for row in data:
            target_value = row[target_keyname]
            model.learn(row, target_value)



if __name__ == "__main__":
    data = Data("train.csv")
    print data.columns()
    print data.all_values("Hillshade_9am")
    for x in ["1", "2", "3", "4", "5", "6"]:
        print x
        elevations = data.all_values("Elevation", x)
        print min(elevations)
        print max(elevations)

