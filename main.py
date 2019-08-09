from threading import Condition, Thread
from time import sleep, time
from random import choice, randint


class Timer(Thread):
    def __init__(self, cv):
        Thread.__init__(self)
        self.condition = cv
        self.time = 0

    def run(self):
        print('Timer started')
        while(True):
            with(self.condition):
                while(bathroom.is_empty and qtd_persons != NUM_PERSONS):
                    self.condition.wait()

            # Há alguém no banheiro
            tempo_inicial = time()
            # Espera o banheiro esvaziar
            with(self.condition):
                while(not bathroom.is_empty and qtd_persons != NUM_PERSONS):
                    self.condition.wait()

            # Banheiro Vazio
            # Atualiza o tempo
            self.time += (time() - tempo_inicial)
            # Checa se todos já utilizaram o banheiro
            if(qtd_persons == NUM_PERSONS):
                print('Timer finished')
                print('Time: {}'.format(self.time))
                break


class Person(Thread):
    def __init__(self, cv, gender, i):
        Thread.__init__(self)
        self.gender = gender
        self.condition = cv
        self.i = i

    def __str__(self):
        return 'Person {} ({})'.format(self.id, self.gender)

    def run(self):
        global qtd_persons
        # Pessoa i chega para utilizar o banheiro
        s = 'Person {} arrives (Gender: {})\n-----'.format(self.i, self.gender)
        print(s)
        # Pessoa i entra na fila
        queue.append(self)
        # Pessoa i entra no banheiro
        self.enter_bathroom()
        # Pessoa i utiliza o banheiro por 5 segundos
        print('Person {} in the bathroom\n-----'.format(self.i))
        sleep(5)
        # Pessoa i sai do Banheiro e vai embora
        self.leave_bathroom()
        print('Person {} leaves the bathroom\n-----'.format(self.i))
        # Atualiza o contador de pessoas
        qtd_persons += 1

    def enter_bathroom(self):
        with(self.condition):
            while(True):
                # Se não for o primeiro da fila, dorme
                if(queue.index(self) > 0):
                    self.condition.wait()
                    continue

                # --- Person i é o primeiro da fila ---

                # Checa se o banheiro está cheio
                # Se estiver cheio, dorme
                if(bathroom.is_full):
                    self.condition.wait()
                    continue

                # --- Banheiro possui vagas ---

                # Checa se o banheiro está vazio
                # Se sim, entra
                if(bathroom.is_empty):
                    break

                # --- Banheiro não está vazio ---

                # Checa o "gênero do banheiro"
                if(bathroom.gender != self.gender):
                    self.condition.wait()
                    continue

                # --- Person i possui todas as condições para entrar --
                break

        # Sai da fila e entra no banheiro
        queue.remove(self)
        bathroom.append(self)

    def leave_bathroom(self):
        with(self.condition):
            bathroom.remove(self)
            self.condition.notify_all()


class Bathroom:
    def __init__(self, num_boxes):
        self.persons = []
        self.boxes = num_boxes

    @property
    def gender(self):
        try:
            return self.persons[0].gender
        except IndexError:
            return None

    def append(self, p):
        self.persons.append(p)

    def remove(self, p):
        self.persons.remove(p)

    @property
    def is_full(self):
        return len(self.persons) == self.boxes

    @property
    def is_empty(self):
        return len(self.persons) == 0


genders = ['male', 'female', 'non-binary']
counter_genders = [0, 0, 0]
NUM_PERSONS = 9
NUM_BOXES = 2
bathroom = Bathroom(num_boxes=NUM_BOXES)
queue = []
qtd_persons = 0


def main():
    # Variável para controle de regiões críticas
    cv = Condition()

    # Inicialização da Contagem de Tempos
    t = Timer(cv)
    t.start()
    # For para criação de Threads
    for i in range(NUM_PERSONS):
        # Escolhendo aleatoriamente um gênero válido
        flag = False
        while(not flag):
            gender = choice(genders)
            # Controle para gerar os gêneros de forma bem distribuida
            if(counter_genders[genders.index(gender)] < (NUM_PERSONS / 3)):
                flag = True
                counter_genders[genders.index(gender)] += 1
        # Criando e iniciando as Threads
        p = Person(cv, gender, i + 1)
        p.start()
        # Espera entre 1 e 7 segundos para chegar outra pessoa
        sleep(randint(1, 7))


if(__name__ == '__main__'):
    main()
