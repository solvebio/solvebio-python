import solvebio


class CSVExporter(object):
    """
    This class includes helper functions to export
    a SolveBio Query object to a CSV file.
    """

    def __init__(self, query, filename):
        self.query = query
        self.filename = filename

    def export(self):
        if isinstance(self.query, solvebio.Query):
            return self.query.to_data_frame().to_csv(self.filename)
