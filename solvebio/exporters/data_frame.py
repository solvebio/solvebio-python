import pandas as pd


class DataFrameExporter(object):
    """
    This class includes helper functions to change data
    formats between SolveBio Queries and Pandas DataFrames.
    For more information visit http://pandas.pydata.org.
    """

    def __init__(self, query):
        self.query = query

    def convertNestedDictToDF(self, nestedDict):
        result = {}

        # Query results are python dictionaries.
        for k, v in nestedDict.iteritems():
            # The function will create a DataFrame
            # with separate columns for each
            # key and subkey pair.
            if type(v) is dict:
                for x, y in v.iteritems():
                    result[(str(k), str(x))] = [y]
            elif type(v) is list:
                if len(v) == 1:
                    # Value is list with one dictionary.
                    if type(v[0]) is dict:
                        for item in v:
                            if type(item) is dict:
                                for m, n in item.iteritems():
                                    if n is not None:
                                        result[(str(k), str(m))] = [''.join(n)]
                    # Value is list with one non-dict value.
                    else:
                        result[(k)] = v
                else:
                    # Value is list of  dictionaries.
                    if type(v[0]) is dict:
                        end = ''
                        count = 0
                        for item in v:
                            sub_end = []
                            for m, n in item.iteritems():
                                if type(n) is list:
                                    n = ', '.join(n)
                                sub_end.append(str(m) + ': ' + str(n))
                            end += ', '.join(sub_end) + '\r\n'
                            count += 1
                        result[(str(k), '*nested*')] = [end]
                    # Value is list of length greater than 1.
                    else:
                        result[(k)] = [', '.join(str(elem) for elem in v)]
            else:
                result[(k)] = [v]
        df = pd.DataFrame(result)
        return df

    def export(self):
        # Function takes SolveBio query as
        # argument and returns pandas DataFrame object.
        frames = []

        for q in self.query:
            frames.append(self.convertNestedDictToDF(q))

        df = pd.concat(frames)
        df.index = range(len(self.query))
        columns = df.columns
        correct = []
        for x in range(0, len(columns)):
            if type(columns[x]) is tuple:
                correct.append(', '.join(columns[x]))
            else:
                correct.append(columns[x])
        df.columns = correct
        return df
