from threading import Thread
from random import choice

genders = ['male', 'female', 'non-binary']


class Person(Thread):
    def __init__(self, i):
        Thread.__init__(self)
        self.gender = choice(genders)
        self.i = i

    def run(self):
        print("{} - {}".format(self.i, self.gender))


def main():
    for i in range(10):
        p = Person(i)
        p.start()


if(__name__ == '__main__'):
    main()
