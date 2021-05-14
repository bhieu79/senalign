from abc import abstractmethod


class Comparable:

    @abstractmethod
    def cmp(self, element1, element2):
        pass
