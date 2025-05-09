'''
This modules defined each sample, their properties and their supported functions.
'''
class Sample:
    def __init__(self, name, mass=None, make_time=None):
        self.name = name
        self.mass = mass
        self.make_time = make_time
    
    def selfIntroduction(self):
        print(f'Hi I am {self.name}')

    