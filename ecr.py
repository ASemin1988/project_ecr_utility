
class ECR:
    def __init__(self, driver):
        self.dto10 = driver
        self.configuration = self.dto10.get_cofiguration()
        self.platform = self.dto10.get_platform()