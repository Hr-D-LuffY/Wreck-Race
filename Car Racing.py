from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random,time

def Pixel_Draw(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()

class MidpointLine:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        zone = self.findZone(self.x1, self.y1, self.x2, self.y2)  # Find the zone of the line
        x1_z0, y1_z0 = self.con_TO_0(self.x1, self.y1, zone)  # Convert the coordinates to zone 0
        x2_z0, y2_z0 = self.con_TO_0(self.x2, self.y2, zone)

        dx = x2_z0 - x1_z0
        dy = y2_z0 - y1_z0
        d = 2 * dy - dx
        d_E = 2 * dy
        d_NE = 2 * (dy - dx)

        if x1_z0 > x2_z0:  # If the initial x-point is greater than the final x-point, swap them due to loop structure
            x1_z0, x2_z0 = x2_z0, x1_z0
            y1_z0, y2_z0 = y2_z0, y1_z0

        x, y = x1_z0, y1_z0
        while x <= x2_z0:  # Going only from initial x-point to final one, as final y-point will be reached automatically
            orig_x, orig_y = self.con_FROM_0(x, y, zone)  
            Pixel_Draw(orig_x, orig_y)  
            if d > 0:
                y += 1
                d += d_NE  
            else:
                d += d_E 
            x += 1

    def con_TO_0(self, x, y, zone):
        conversions = [
            (x, y), (y, x), (y, -x), (-x, y),
            (-x, -y), (-y, -x), (-y, x), (x, -y)
        ]
        return conversions[zone]


    def con_FROM_0(self, x, y, zone):
        conversions = [
            (x, y), (y, x), (-y, x), (-x, y),
            (-x, -y), (-y, -x), (y, -x), (x, -y)
        ]
        return conversions[zone]

    def findZone(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) >= abs(dy):
            if dx >= 0 and dy >= 0:
                return 0
            elif dx >= 0 and dy < 0:
                return 7
            elif dx < 0 and dy >= 0:
                return 3
            else:
                return 4
        else:
            if dx >= 0 and dy >= 0:
                return 1
            elif dx >= 0 and dy < 0:
                return 6
            elif dx < 0 and dy >= 0:
                return 2
            else:
                return 5

# Midpoint Circle Drawing Algorithm
class MidpointCircle:
    def __init__(self, x_center, y_center, radius, half = False):
        self.x_center = x_center
        self.y_center = y_center
        self.radius = radius
        self.half = half

        x = 0
        y = radius
        d = 1 - radius

        self.draw_circle_symmetric_points(self.x_center, self.y_center, x, y, False)  # Draw the first point and its reflections

        while x < y:
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * x - 2 * y + 5
                y -= 1
            x += 1
            self.draw_circle_symmetric_points(self.x_center, self.y_center, x, y, self.half)  # Once a point is found, draw all its reflections

    def draw_circle_symmetric_points(self, x_center, y_center, x, y, half):
        # Takes a certain pixel and draws all the reflections in all zones simultaneously
        if not half:  # Drawing all the points except the zone 0 ones for half circle
            Pixel_Draw(int(x_center + y), int(y_center + x))  # Zone - 0 (y, x)
        Pixel_Draw(int(x_center + x), int(y_center + y))  # Zone - 1 (x, y)
        Pixel_Draw(int(x_center - x), int(y_center + y))  # Zone - 2 (-x, y)
        Pixel_Draw(int(x_center - y), int(y_center + x))  # Zone - 3 (-y, x)
        Pixel_Draw(int(x_center - y), int(y_center - x))  # Zone - 4 (-y, -x)
        Pixel_Draw(int(x_center - x), int(y_center - y))  # Zone - 5 (-x, -y)
        Pixel_Draw(int(x_center + x), int(y_center - y))  # Zone - 6 (x, -y)
        Pixel_Draw(int(x_center + y), int(y_center - x))  # Zone - 7 (y, -x)

# Global Variables
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
car_position=WINDOW_WIDTH//2 +25
missiles=[]
missile_counter=6
no_missile= missile_counter
missile_last_time = []
last_recharge_time = 0

hearts = []  
last_spawn_time = 0

game_started = False  
paused = False
last_time = time.time()
score=0
life=3

enemy_cars = []  # Stores data for enemy cars: [x, y, color]
enemy_car_speed = 4  # Speed of the enemy cars
spawn_interval = 5  # Time interval between spawning new sets of cars
last_spawn_time = 0  # Tracks the last spawn time

car_speed = 25  # Initialize car speed
key_pressed = None  # Track the currently pressed key

def road():
    # Draw white lane markers
    glColor3f(1.0, 1.0, 1.0)  # White color
    for y in range(0, 625, 40):  # Dashed lane markers
        MidpointLine(225, y, 225, y + 20)  # Draw short vertical segments
        MidpointLine(325, y, 325, y + 20)
        MidpointLine(425, y, 425, y + 20)
        MidpointLine(525, y, 525, y + 20)

    # Draw yellow boundary lines
    glColor3f(1.0, 1.0, 0.0)  # Yellow color
    MidpointLine(125, 0, 125, 625)  # Left boundary
    MidpointLine(625, 0, 625, 625)  # Right boundary

    #setting up the top
    MidpointLine(0,625,WINDOW_WIDTH,625)

def my_car():
    global car_position
    # Car body
    glPointSize(1.5)
    glColor3f(0.529, 0.808, 0.922)
    for y in range(12, 95):
        MidpointLine(car_position-25, y, car_position+25, y)

    #front design 
    glColor3f(1,1,1)
    MidpointLine(car_position-23, 86, car_position-5, 86)
    MidpointLine(car_position+23, 86, car_position+5, 86)
    MidpointLine(car_position, 94, car_position, 90)
    MidpointCircle(car_position,85,5)

    #front window glass
    glPointSize(1)
    glColor3f(0,0,0)

    # Defining the corner points of the polygon
    x1, y1 = car_position - 19, 60  # Bottom-left
    x2, y2 = car_position + 19, 60  # Bottom-right
    x3, y3 = car_position - 23, 72  # Top-left
    x4, y4 = car_position + 23, 72  # Top-right
    # Fill the upper triangular region (scanline filling)
    for y in range(y1, y3 + 1):  # Loop from the bottom to the top
        # Calculate the x-coordinates of the intersections for the current scanline (y)
        x_left = x1 + (x3 - x1) * (y - y1) // (y3 - y1)  # Left edge
        x_right = x2 + (x4 - x2) * (y - y2) // (y4 - y2)  # Right edge
        # Draw a horizontal line between x_left and x_right
        MidpointLine(x_left, y, x_right, y)

    #Top
    glColor3f(0.5,0.5,0.5)
    for y in range(35,55):
        MidpointLine(car_position-19, y, car_position+19, y) 

    #Missile tip
    glPointSize(1.5)
    glColor3f(1.0, 0.0, 0.0) 
    MidpointLine(car_position, 38, car_position-5, 43)  
    MidpointLine(car_position, 38, car_position+5, 43) 
    MidpointLine(car_position+5, 48, car_position+5, 43) 
    MidpointLine(car_position-5, 48, car_position-5, 43) 
    MidpointLine(car_position-5, 48, car_position+5, 48) 
    MidpointLine(car_position, 48, car_position, 58) 

    #Back Design
    glColor3f(1,1,1)
    glPointSize(1.5)
    MidpointLine(car_position-22, 16, car_position+22, 16)
    MidpointLine(car_position+22, 16, car_position+22, 32) 
    MidpointLine(car_position-22, 16, car_position-22, 32)
    MidpointLine(car_position+2, 16, car_position+2, 24)
    MidpointLine(car_position-2, 16, car_position+-2, 24)

    #back window glass
    glColor3f(0,0,0) 
    x1, y1 = car_position - 22, 32  # Bottom-left
    x2, y2 = car_position + 22, 32  # Bottom-right
    x3, y3 = car_position - 13, 24   # Top-left
    x4, y4 = car_position + 13, 24   # Top-right
    for y in range(y3, y1 + 1):
        if y1 != y3:  # Avoid division by zero
            x_left = x1 + (x3 - x1) * (y - y1) // (y3 - y1) 
            x_right = x2 + (x4 - x2) * (y - y2) // (y3 - y2) 
        else:
            x_left, x_right = x1, x2
        MidpointLine(x_left, y, x_right, y)

    #wheel
    glColor3f(0,0,1)
    glPointSize(5)
    MidpointLine(car_position+25, 88, car_position+25, 73)  
    MidpointLine(car_position-25, 88, car_position-25, 73)
    MidpointLine(car_position+25, 25, car_position+25, 40) 
    MidpointLine(car_position-25, 25, car_position-25, 40)

#Missile Section
def missile():
    for x,y in missiles:
       glPointSize(1)
       glColor3f(1.0, 0.0, 0.0)  
       MidpointLine(x,y,x,y+20)
       MidpointLine(x+5,y,x+5,y+20)
       MidpointLine(x,y,x+5,y)
       MidpointLine(x,y+20,x+3,y+24)
       MidpointLine(x+2,y+24,x+5,y+20)
       MidpointLine(x,y,x-3,y-5)
       MidpointLine(x+5,y,x+8,y-5)
        
def missiles_movement(d_time):
    global missiles
    for p in missiles[:]:
        p[1] += int(300 * d_time)
        if p[1] > 620:  # Remove missiles that are off-screen
            missiles.remove(p)
    glutPostRedisplay()

def can_shoot_missile():
    global no_missile, missile_last_time

    # Check if missile counter allows shooting
    if no_missile > 0:
        return True  # Missiles are available

    # Check if any missile has completed its cooldown
    current_time = time.time()
    for fire_time in missile_last_time:
        if current_time - fire_time >= 4:  # If any missile's cooldown is done
            return True

    # If neither condition is met, cannot shoot
    return False

def update_missiles():
    global missile_last_time, no_missile,last_recharge_time,missile_counter

    current_time = time.time()

    # Check if it's time to recharge the next missile
    if no_missile < missile_counter and (current_time - last_recharge_time) >= 4:
        no_missile += 1  # Recharge one missile
        last_recharge_time = current_time  # Update the last recharge time
        print(f"Missile recharged. {no_missile} missiles available to shoot.")  


def score_card():
    glColor3f(0.5, 0.5, 0.5)
    for y in range(460, 580):  # Cover the height of the track
        MidpointLine(5, y, 115, y)

    render_stroke_text(20, 555, f"Score: {score}", 0.13, (1,1,1), 1.5)
    render_stroke_text(20, 525, f"Speed: {car_speed}", 0.13, (1,1,1), 1.5)
    render_stroke_text(20, 495, f"Life: {life}", 0.13, (1,1,1), 1.5)
    render_stroke_text(20, 470, f"Missiles: {no_missile}", 0.13, (1,1,1), 1.5)
    
    # Draw yellow boundary lines
    glColor3f(1.0, 1.0, 0.0)  
    MidpointLine(5, 460, 5, 580)
    MidpointLine(115, 460, 115, 580)  
    MidpointLine(5, 580, 115, 580) 
    MidpointLine(115, 460, 5, 460)  

def draw_menu():
    render_stroke_text(230, 410, "Wreck & Race", 0.3, (1.0, 0.0, 0.0), 4.0)  # Red bold text
    render_stroke_text(250, 360, "Instruction", 0.2, (0.5, 0.0, 0.5), 1.5)  # Purple color
    glPointSize(2)
    MidpointLine(250,355,400,355)
    render_stroke_text(250, 340, "Press 'ENTER' To Start", 0.1, (1.0, 1.0, 1.0), 1.2)  # White text
    render_stroke_text(250, 320, "Press 'w' For Speed", 0.1, (1.0, 1.0, 1.0), 1.2)  # White text
    render_stroke_text(250, 300, "Press 'a' For Left & 'd' For Right Movement", 0.1, (1.0, 1.0, 1.0), 1.2)  # White text
    render_stroke_text(250, 280, "Press 'X' To Exit", 0.1, (1.0, 1.0, 1.0), 1.2)  # White text

class EnemyCar:
    def __init__(self, x, y,color, speed, is_special):
        # Initialize position, speed, and special flag
        self.x = x
        self.y = y
        self.color=color
        self.speed = speed
        self.is_special = is_special
        self.last_size_change_time = time.time()  # To track size changes over time
        self.height=80
        self.width=48

    def update_position(self):
        self.y -= self.speed 

    def out_of_boundary(self):
        return self.y < 0  

    def draw(self):
        y=self.y+ 20 if  self.is_special else self.y
        x=self.x+ 20 if  self.is_special else self.x
        glColor3f(*self.color) if  self.is_special else glColor3f(1.0, 0.0, 0.0)
         #body
        glPointSize(1.5)
        for yy in range(y-40, y+40):
            MidpointLine(x-24, yy, x+24, yy)

        # Front glass (filled rectangle)
        # glColor3f(1,1,1) if self.is_special else glColor3f(0,0,0)
        if self.is_special:
            glColor3f(1,1,1)
        else:
            glColor3f(0,0,0)
        for xx in range(x-20, x+20):  # Loop to fill using vertical lines
            MidpointLine(xx, y-25, xx, y-10)

        # Front flash
        glColor3f(0,0,1)
        for xx in range(x-21, x-15):  
            MidpointLine(xx, y-35, xx, y-30)
        glColor3f(0,0,1)
        for xy in range(x+15, x+21):  
            MidpointLine(xy, y-35, xy, y-30)

        # Back glass (filled rectangle)
        glColor3f(0,0,0)
        for xx in range(x-20, x+20): 
            MidpointLine(xx, y+20, xx, y+30)

        #whell
        glPointSize(3)
        glColor3f(0.5, 0.5, 0.5)
        MidpointLine(x-25,y+35,x-25,y+21)
        MidpointLine(x-25,y-31,x-25,y-17)
        MidpointLine(x+25,y+35,x+25,y+21)
        MidpointLine(x+25,y-31,x+25,y-17)

def spawn_enemy_cars():
    global enemy_cars, last_spawn_time

    current_time = time.time()
    if (current_time - last_spawn_time) >= spawn_interval:
        lanes = [175, 275, 375, 475]  # Centers of the lanes
        for _ in range(4):  # Spawn 4 cars
            x = random.choice(lanes)  # Choose a random lane
            y = 600  # Start at the top of the screen
            while True:
                color = (random.random(), random.random(), random.random())
                if color != (1, 0, 0) and color != (0, 0, 0):
                    break
            is_special = random.random() < 0.15
            enemy_cars.append(EnemyCar(x, y,color, enemy_car_speed, is_special))  # Add to the list of cars
            print(enemy_cars[_].is_special)
        last_spawn_time = current_time  # Update last spawn time

def update_enemy_cars():
    global enemy_cars
    for car in enemy_cars:
        car.update_position()  # Update position based on speed

    # Remove cars that go off the screen
    enemy_cars = [car for car in enemy_cars if not car.out_of_boundary()]

def draw_enemy_cars():
    for car in enemy_cars:
        car.draw() 

def display():
    global score, life, no_missile,game_started,last_spawn_time
    glClear(GL_COLOR_BUFFER_BIT)
    if not game_started:
        draw_menu()
    else:
        # Spawn, update, and draw enemy cars
        spawn_enemy_cars()  # Spawn new cars every 3 seconds
        update_enemy_cars()  # Update positions of cars
        draw_enemy_cars()  # Draw all active cars

        buttons()
        update_hearts()  
        # Draw all hearts
        for heart in hearts:
            heart.draw()
        score_card()
        road()
        my_car()
        update_missiles()
        missile()
    glFlush()

#Heart / Life Section
class Heart:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 1.0  # Opacity (1.0 = fully visible)

    def draw(self):
        glColor4f(1.0, 0.0, 0.0, self.alpha)  # Red color with transparency
        glPointSize(1.5)
        MidpointLine(self.x, self.y, self.x + 10, self.y + 8)
        MidpointLine(self.x, self.y, self.x - 10, self.y + 8)
        MidpointLine(self.x - 20, self.y, self.x - 10, self.y + 8)
        MidpointLine(self.x + 20, self.y, self.x + 10, self.y + 8)
        MidpointLine(self.x - 20, self.y, self.x - 20, self.y - 13)
        MidpointLine(self.x + 20, self.y, self.x + 20, self.y - 13)
        MidpointLine(self.x - 20, self.y - 13, self.x, self.y - 25)
        MidpointLine(self.x + 20, self.y - 13, self.x, self.y - 25)
        MidpointLine(self.x, self.y, self.x, self.y - 25)

    def update(self):
        self.y -= 8  # Move downward
        if self.y < 400:
            self.alpha -= 0.02  # Gradually fade out

        if self.alpha <= 0:
            return False  # Remove heart when fully faded
        return True

def spawn_heart():
    global hearts
    x = random.randint(150, 600)
    y = random.randint(500, 600)
    hearts.append(Heart(x, y))

def update_hearts():
    global last_spawn_time
    # Check if 12 seconds have passed since the last spawn
    current_time = time.time()
    if current_time - last_spawn_time > 12:
        spawn_heart()
        last_spawn_time = current_time

    # Update hearts and remove those that are no longer visible
    hearts[:] = [heart for heart in hearts if heart.update()]


def buttons():
    glPointSize(2)
    # Restart button (cyan) - Circle
    glColor3f(0.0, 1.0, 1.0)
    MidpointCircle(40, 665, 10, True)  
    MidpointLine(50,665, 40,661)
    MidpointLine(50, 665, 58,658)  # Drawing the tiny arrow

    glPointSize(3)
    # Play/Pause button
    glColor3f(1.0, 0.75, 0.0)
    MidpointLine(340, 655, 360, 665) 
    MidpointLine(360, 665, 340, 675)
    MidpointLine(340, 675, 340, 655)

    # Exit button
    glColor3f(1.0, 0.0, 0.0)
    MidpointLine(650, 655, 670, 675) 
    MidpointLine(650, 675, 670, 655)
    glColor3f(1, 1, 1)
    glRasterPos2f(530, 620)

# Update Function
def update(value):
    global last_time,car_position, car_speed, key_pressed,last_spawn_time,hearts
    

    if not paused:
        current_time = time.time()
        d_time = current_time - last_time
        last_time = current_time

    missiles_movement(d_time)
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def render_stroke_text(x, y, text, scale, color=(1, 1, 1), line_width=1):
    glPushMatrix()
    glColor3f(*color)  # Set text color (use * to unpack the tuple)
    glLineWidth(line_width)  # Set line width to make text bold
    glTranslatef(x, y, 0)  # Set text position
    glScalef(scale, scale, scale)  # Scale the text for desired size

    for char in text:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(char))    
    glPopMatrix()


def keyboard(key, x, y):
    global car_position, car_speed, key_pressed,game_started,missiles,no_missile,missile_last_time
    if not game_started:
        if key == b'\r': 
            game_started = True  # Set the game state to started
            glutPostRedisplay()
        elif key == b'x':
            print("Goodbye!")
            glutLeaveMainLoop() 
    else:
        if key == b'a' or key == b'A':
            car_position = max(25, car_position - car_speed)  # Move car left
        elif key == b'd' or key == b'D':
            car_position = min(675, car_position + car_speed)  # Move car right
        elif key == b' ' and can_shoot_missile():  # Only shoot if can_shoot_missile() allows
            current_time = time.time()

            if no_missile > 0:  # There are missiles available to shoot
                missiles.append([car_position, 105])  # Add new missile at car position
                missile_last_time.append(current_time)  # Store the current time of firing for this missile
                no_missile -= 1  # Decrease missile counter
                print(f"Missile fired. {len(missiles)} missiles in air. Missiles remaining: {no_missile}")
            else:
                print("No missiles left to shoot.")
        elif key == b'e':
            key_pressed = 'e'  # Set the key as pressed

        glutPostRedisplay()

def mouse(button, state, x, y):
    global paused, score, last_time,WINDOW_WIDTH, WINDOW_HEIGHT,game_started
    if state == GLUT_DOWN:
        # Convert screen coordinates to OpenGL coordinates
        gl_x = x  # Convert to OpenGL's coordinate system, where the origin is at the center
        gl_y = (WINDOW_HEIGHT-y )

        # print(gl_x,gl_y)
        # Check for Restart button (Triangle)
        if 30 <= gl_x <= 60 and 655 <= gl_y <= 675:  # Approximation of the bounding box for the triangle
                # restart()
                print("Starting Over...")

            # Check for Play/Pause button (Triangle)
        elif 340 <= gl_x <= 360 and 655 <= gl_y <= 675:  # Approximation of the bounding box for the triangle
                paused = not paused
                last_time = time.time()
                print("Game Paused" if paused else "Game Resumed")

            # Check for Exit button (Rectangle)
        elif 647 <= gl_x <= 672 and 653 <= gl_y <= 677:  # Exit button's rectangular area
                print("Goodbye!")
                print("Your final score was:", score)
                game_started=False
                # glutLeaveMainLoop()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0) # Black background
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)  # Set the coordinate system
    game_started = False  # Initially, the game has not started








glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
glutCreateWindow(b"Car with Missile Launcher")
init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutTimerFunc(30, update, 0)
glutMainLoop()

