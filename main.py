from threading import Condition, Thread
from time import sleep, time
from random import choice, randint
import numpy as np

util_time = 0
NUM_PERSONS = 300
NUM_BOXES = 5
genders = ['homem', 'mulher', 'não-binário']
counter_genders = [0, 0, 0]
queue = []
male_waiting_times = []
female_waiting_times = []
nonbinary_waiting_times = []


class Timer(Thread):
    def __init__(self, cv):
        Thread.__init__(self)
        self.condition = cv
        self.time = 0

    def run(self):
        print('Timer iniciado')
        while(True):
            # Espera alguém entrar no banheiro
            with(self.condition):
                while(bathroom.is_empty and qtd_persons < NUM_PERSONS):
                    self.condition.wait()

            # Há alguém no banheiro
            tempo_inicial = time()  # Momento que alguém entra
            # Espera o banheiro esvaziar
            with(self.condition):
                while((not bathroom.is_empty) and qtd_persons < NUM_PERSONS):
                    self.condition.wait()

            # Banheiro Vazio
            # Atualiza o tempo
            dif = time() - tempo_inicial
            self.time += dif
            # Checa se todos já utilizaram o banheiro
            if(qtd_persons == NUM_PERSONS):
                global util_time
                print('Timer encerrado')
                print('Tempo de Utilização: {0:.2f}s'.format(self.time))
                util_time = self.time
                break


class Person(Thread):
    def __init__(self, cv, gender, i):
        Thread.__init__(self)
        self.gender = gender
        self.condition = cv
        self.i = i

    def __str__(self):
        return 'Pessoa {} ({})'.format(self.id, self.gender)

    def run(self):
        global qtd_persons
        # Pessoa i chega para utilizar o banheiro
        s = 'Pessoa {} chegou (Gênero: {})\n-----'.format(self.i, self.gender)
        print(s)
        # Pessoa i entra na fila
        start_waiting_time = time()  # Momento que a pessoa i entra na fila
        queue.append(self)
        # Pessoa i entra no banheiro
        self.enter_bathroom()
        # Salva o tempo de espera
        if(self.gender == 'homem'):
            male_waiting_times.append(time() - start_waiting_time)
        elif(self.gender == 'mulher'):
            female_waiting_times.append(time() - start_waiting_time)
        else:
            nonbinary_waiting_times.append(time() - start_waiting_time)
        # Pessoa i utiliza o banheiro por 5 segundos
        print('Pessoa {} no banheiro\n-----'.format(self.i))
        sleep(5)
        # Pessoa i sai do Banheiro e vai embora
        self.leave_bathroom()
        print('Pessoa {} saiu do banheiro\n-----'.format(self.i))
        # Atualiza o contador de pessoas
        qtd_persons += 1

    def enter_bathroom(self):
        with(self.condition):
            while(True):
                # Se não for o primeiro da fila, dorme
                if(queue.index(self) > 0):
                    s = 'Pessoa {} não entrou por não ser o primeiro ' \
                        'da fila\n-----'.format(self.i)
                    print(s)
                    self.condition.wait()
                    continue

                # --- Person i é o primeiro da fila ---

                # Checa se o banheiro está cheio
                # Se estiver cheio, dorme
                if(bathroom.is_full):
                    s = 'Pessoa {} não entrou pois o banheiro estava cheio' \
                        '\n-----'.format(self.i)
                    print(s)
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
                    s = 'Pessoa {} não entrou pois outro gênero estava no ' \
                        'banheiro\n-----'.format(self.i)
                    print(s)
                    self.condition.wait()
                    continue

                # --- Person i possui todas as condições para entrar --
                break

        # Sai da fila e entra no banheiro
        queue.remove(self)
        bathroom.append(self)
        with(self.condition):
            self.condition.notify_all()

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


bathroom = Bathroom(num_boxes=NUM_BOXES)
qtd_persons = 0


def main():
    # Variável para controle de regiões críticas
    cv = Condition()

    # Inicialização da Contagem de Tempos
    t = Timer(cv)
    t.start()
    # For para criação de Threads
    tt = time()
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

    # Espera todas as threads encerrarem
    while(qtd_persons < NUM_PERSONS):
        pass

    with(cv):
        cv.notify_all()

    t.join()
    total_time = time() - tt
    print('Tempo total: {0:.2f}s'.format(total_time))
    usage_rate = 100 * (util_time / total_time)
    print('Taxa de Utilização: {0:.2f}%'.format(usage_rate))
    print('Número de usuários por gênero:')
    print('Homens: {}'.format(counter_genders[0]))
    print('Mulheres: {}'.format(counter_genders[1]))
    print('Não-binários: {}'.format(counter_genders[2]))
    print('Tempo médio de espera por gênero:')
    print('Homens: {0:.2f}s'.format(np.mean(male_waiting_times)))
    print('Mulheres: {0:.2f}s'.format(np.mean(female_waiting_times)))
    print('Não-binários: {0:.2f}s'.format(np.mean(nonbinary_waiting_times)))


if(__name__ == '__main__'):
    main()
