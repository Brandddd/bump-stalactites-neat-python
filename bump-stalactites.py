"""
    * Bump Stalatites con Neat, (Redes neuronales)
"""

# * Declaración de librerías
import pygame
import random
import os
import neat

pygame.font.init()

# * Variables usadas
WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("Console", 50, bold=True)
END_FONT = pygame.font.SysFont("Console", 70, bold=True)
DRAW_LINES = False

# * Ventana principal
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Bump Stactite")

# * Llamado de imágenes
pipe_img = pygame.transform.scale2x(pygame.image.load(
    os.path.join("imgs", "pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(
    os.path.join("imgs", "bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(
    os.path.join("imgs", "bird" + str(x) + ".png"))) for x in range(1, 4)]
base_img = pygame.transform.scale2x(pygame.image.load(
    os.path.join("imgs", "base.png")).convert_alpha())

gen = 0

# * Clase donde se declara la nave


class Bird:
    """
        * Clase Bird que representa el juego
    """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
            * Inicializando el objeto: 
        """
        self.x = x
        self.y = y
        self.tilt = 0  # Inclinación de la nave.
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
            * Hace que la nave salte.
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
            * Movimientos de la nave
        """
        self.tick_count += 1

        # * Ir hacia abajo:
        displacement = self.vel*(self.tick_count) + 0.5 * \
            (3)*(self.tick_count)**2  # * Calcula el desplazamiento.

        # * Velocidad:
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # La inclina hacia arriba
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # Si no, la inclina hacia abajo
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
            * Dibujo del la nave (HitBox)
        """

        # * Inclinacion de la nave
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
            * Obtiene una superficie la imagen y la adapta a la hit box
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
        * Clase Pipe: 
        * Objeto tipo Pipa o estalactita. 
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
            * Inicialización del objeto
        """
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
            * Esta función, establece la altura de la Estalactita desde la parte más abajo de la pantalla
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
            * Mueve la Estalactita en función de la velocidad. 
            TODO : Incluir nivel de mas velocidad acorde a la puntuación.
        """
        self.x -= self.VEL * 1.5

    def draw(self, win):
        """
            * Dibuja la parte de arriba y de abajo de la Estalactita
        """
        # Dibuja pipa de arriba.
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # Dibuja pipa de abajo.
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        """
            * Función de colisión.
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False


class Base:
    """
        * Representa el movimiento de la base de abajo (Especie de superficie marciana)
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
            * Inicialización del objeto. 
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
            * Movimiento del piso.
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
            * Dibujando la Hitbox de la superficie.
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
        * Organización de la superficie con respecto a la pantalla. 
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
        * Dibujando la pantalla para el la ventana principal main_game loop
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # ? 
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height(
                )/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255, 0, 0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height(
                )/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # * Dibuja la hb de la nave en pantalla. 
        bird.draw(win)

    # * Texto generaciones
    score_label = STAT_FONT.render("Generación: " + str(gen), 1, (0, 0, 0))
    win.blit(score_label, (10, 10))

    # * Texto de los que aun quedan vivos. 
    score_label = STAT_FONT.render(
        "Sobrevivientes: " + str(len(birds)), 1, (0, 0, 0))
    win.blit(score_label, (10, 50))

    # * Puntuación 
    score_label = STAT_FONT.render("Puntaje: " + str(score), 1, (0, 0, 0))
    win.blit(score_label, (10, 90))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
        * Ejecuta la simulacion de la población de naves y establece
        * su Fitness basado en la distancia que ellos alcanzan dentro del juego.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            # determine whether to use the first or second
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                # pipe on the screen for neural network input
                pipe_ind = 1

        # give each bird a fitness of 0.1 for each frame it stays alive
        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(
                bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
            if output[0] > 0.5:
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # break if score gets large enough
        if score > 200:
            print(" Felicidades, ha aprendido satisfactoriamente. ")
            break


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 12)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
