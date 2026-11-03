
import os
import random
import sys
import neat
import pygame

# -------------------------------------------------------------
# 1. CONFIGURAÇÕES DO JOGO
# -------------------------------------------------------------

LARGURA = 400
ALTURA = 600
VELOCIDADE_JOGO = 60

pygame.init()

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Flappy Medieval - Inteligência Artificial")

RELOGIO = pygame.time.Clock()
FONTE = pygame.font.SysFont("Arial", 18, bold=True)

GERACAO = 0

# Cores medievais
CEU = (105, 170, 220)
PEDRA = (105, 105, 105)
PEDRA_CLARA = (145, 135, 115)
OURO = (220, 180, 60)
VERMELHO = (150, 35, 35)
VERDE = (55, 110, 55)
BRANCO = (255, 255, 255)
PRETO = (30, 30, 30)


# -------------------------------------------------------------
# 2. PERSONAGEM: CAVALEIRO VOADOR
# -------------------------------------------------------------

class Passaro:

    def __init__(self):
        self.x = 80
        self.y = ALTURA // 2
        self.velocidade = 0
        self.gravidade = 0.8
        self.pulo = -10.5

    def pular(self):
        self.velocidade = self.pulo

    def mover(self):
        self.velocidade += self.gravidade
        self.y += self.velocidade

    def desenhar(self, tela):

        # Corpo do personagem
        pygame.draw.circle(
            tela, OURO,
            (int(self.x), int(self.y)), 12
        )

        # Capacete
        pygame.draw.arc(
            tela, PEDRA,
            (self.x - 11, self.y - 15, 22, 20),
            0, 3.14, 5
        )

        # Olho
        pygame.draw.circle(
            tela, PRETO,
            (int(self.x + 5), int(self.y - 2)), 2
        )

        # Pluma vermelha
        pygame.draw.line(
            tela, VERMELHO,
            (int(self.x), int(self.y - 14)),
            (int(self.x + 5), int(self.y - 22)), 3
        )


# -------------------------------------------------------------
# 3. OBSTÁCULOS: TORRES DOS CASTELOS
# -------------------------------------------------------------

class Cano:

    def __init__(self, x):
        self.x = x
        self.largura = 65
        self.abertura = 150
        self.altura_abertura = random.randint(120, ALTURA - 200)
        self.velocidade = 4
        self.passou = False

    def mover(self):
        self.x -= self.velocidade

    def desenhar(self, tela):

        limite_superior = self.altura_abertura - self.abertura // 2
        limite_inferior = self.altura_abertura + self.abertura // 2

        # Torre superior
        pygame.draw.rect(
            tela, PEDRA,
            (self.x, 0, self.largura, limite_superior)
        )

        # Detalhes da torre superior
        pygame.draw.rect(
            tela, PEDRA_CLARA,
            (self.x - 5, limite_superior - 15, self.largura + 10, 15)
        )

        # Torre inferior
        pygame.draw.rect(
            tela, PEDRA,
            (self.x, limite_inferior, self.largura, ALTURA)
        )

        # Base da torre inferior
        pygame.draw.rect(
            tela, PEDRA_CLARA,
            (self.x - 5, limite_inferior, self.largura + 10, 15)
        )

        # Bandeiras medievais
        pygame.draw.rect(
            tela, VERMELHO,
            (self.x + 15, limite_superior - 50, 25, 35)
        )

        pygame.draw.polygon(
            tela, OURO,
            [
                (self.x + 15, limite_superior - 15),
                (self.x + 40, limite_superior - 15),
                (self.x + 27, limite_superior - 5)
            ]
        )

    def colidiu(self, passaro):

        limite_superior = self.altura_abertura - self.abertura // 2
        limite_inferior = self.altura_abertura + self.abertura // 2

        if (
            self.x < passaro.x + 12
            and self.x + self.largura > passaro.x - 12
        ):

            if (
                passaro.y - 12 < limite_superior
                or passaro.y + 12 > limite_inferior
            ):
                return True

        return False


# -------------------------------------------------------------
# 4. CENÁRIO MEDIEVAL
# -------------------------------------------------------------

def desenhar_cenario():

    TELA.fill(CEU)

    # Sol
    pygame.draw.circle(TELA, OURO, (330, 90), 35)

    # Montanhas
    pygame.draw.polygon(
        TELA, (100, 130, 110),
        [(0, 400), (100, 230), (210, 400)]
    )

    pygame.draw.polygon(
        TELA, (80, 115, 95),
        [(170, 400), (290, 250), (400, 400)]
    )

    # Castelo ao fundo
    pygame.draw.rect(
        TELA, PEDRA_CLARA,
        (280, 310, 100, 150)
    )

    pygame.draw.rect(
        TELA, PEDRA,
        (300, 270, 30, 80)
    )

    pygame.draw.rect(
        TELA, PEDRA,
        (345, 270, 30, 80)
    )

    # Chão de pedra
    pygame.draw.rect(
        TELA, VERDE,
        (0, ALTURA - 35, LARGURA, 35)
    )

    pygame.draw.rect(
        TELA, PEDRA,
        (0, ALTURA - 20, LARGURA, 20)
    )


# -------------------------------------------------------------
# 5. TREINAMENTO DA INTELIGÊNCIA ARTIFICIAL
# -------------------------------------------------------------

def eval_genomes(genomes, config):

    global GERACAO
    GERACAO += 1

    redes = []
    genomas = []
    personagens = []

    for genome_id, genome in genomes:

        genome.fitness = 0

        rede = neat.nn.FeedForwardNetwork.create(
            genome, config
        )

        redes.append(rede)
        personagens.append(Passaro())
        genomas.append(genome)

    torres = [Cano(LARGURA + 100)]
    pontuacao = 0

    rodando = True

    while rodando and len(personagens) > 0:

        RELOGIO.tick(VELOCIDADE_JOGO)

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        indice_torre = 0

        if (
            len(torres) > 1
            and personagens[0].x > torres[0].x + torres[0].largura
        ):
            indice_torre = 1

        for i, personagem in enumerate(personagens):

            genomas[i].fitness += 0.1

            personagem.mover()

            distancia = (
                torres[indice_torre].x - personagem.x
            ) / LARGURA

            altura_torre = (
                torres[indice_torre].altura_abertura / ALTURA
            )

            altura_personagem = personagem.y / ALTURA

            resultado = redes[i].activate(
                (distancia, altura_torre, altura_personagem)
            )

            if resultado[0] > 0.5:
                personagem.pular()

        torres_remover = []
        adicionar_torre = False

        for torre in torres:

            torre.mover()

            for i in range(len(personagens) - 1, -1, -1):

                personagem = personagens[i]

                if (
                    torre.colidiu(personagem)
                    or personagem.y >= ALTURA - 20
                    or personagem.y <= 0
                ):

                    genomas[i].fitness -= 1

                    personagens.pop(i)
                    redes.pop(i)
                    genomas.pop(i)

            if torre.x + torre.largura < 0:
                torres_remover.append(torre)

            if not torre.passou and torre.x < 80:

                torre.passou = True
                adicionar_torre = True

        if adicionar_torre:

            pontuacao += 1

            for genoma in genomas:
                genoma.fitness += 5.0

            torres.append(Cano(LARGURA))

        for torre in torres_remover:
            torres.remove(torre)

        # -----------------------------------------------------
        # 6. DESENHO DA INTERFACE
        # -----------------------------------------------------

        desenhar_cenario()

        for torre in torres:
            torre.desenhar(TELA)

        for personagem in personagens:
            personagem.desenhar(TELA)

        # Painel de informações
        textos = [
            f"Geracao: {GERACAO}",
            f"Vivos: {len(personagens)}",
            f"Reinos: {pontuacao}"
        ]

        for indice, texto in enumerate(textos):

            imagem = FONTE.render(
                texto, True, BRANCO
            )

            TELA.blit(imagem, (10, 10 + indice * 25))

        pygame.display.flip()


# -------------------------------------------------------------
# 7. INICIALIZAÇÃO DO NEAT
# -------------------------------------------------------------

def run(config_path):

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    populacao = neat.Population(config)

    populacao.add_reporter(
        neat.StdOutReporter(True)
    )

    estatisticas = neat.StatisticsReporter()

    populacao.add_reporter(estatisticas)

    print("Iniciando o treinamento medieval...")

    populacao.run(eval_genomes, 50)


# -------------------------------------------------------------
# 8. EXECUÇÃO
# -------------------------------------------------------------

if __name__ == "__main__":

    diretorio = os.path.dirname(__file__)

    caminho_config = os.path.join(
        diretorio,
        "config-feedforward.txt"
    )

    run(caminho_config)
