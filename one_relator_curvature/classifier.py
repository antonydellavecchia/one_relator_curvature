class Classfier:
    def __init__(self, examples):
        """

        """
        self.example = examples

    def pre_process(self):
        self.passed = list(filter(lambda x: x.curvature <= 0, self.examples))
        self.failed = list(filter(lambda x: x.curvature <= 0, self.examples))

        self.labelled_data = list()
        
