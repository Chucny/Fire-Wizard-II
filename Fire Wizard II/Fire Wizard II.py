#imports

import sys
import traceback
import os
import time
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from networking import NetworkConnection
from safe_debug_functions_not_needed import *



# ===== INPUT =====
op_ip = input("Enter opponent IP (leave blank to host): ").strip()
playername = input("Enter your name: ").strip() or "Player"
is_host = (op_ip == "")
playerscore = 0
opponentscore = 0

sys.excepthook = handle_exception

aga = input("Custom crosshair? Press enter if not, write something if yes. ")
if aga == "":
    crosshair=False
else:
    crosshair=True

FOV = input("FOV? Press enter for deafult or enter yhe FOV you want. ")
if FOV == "":
    fov1 = 90
else:
    fov1 = int(FOV)
# ===== URSINA SETUP =====
app = Ursina()
window.fullscreen = True

Sky()
camera.fov = fov1

floor = Entity(
    model='cube',
    scale=(40,1,40),
    collider='box',
    texture='grass'
)
def make_crosshair(size=0.005, color=color.white):
    # Makes a crosshair
    crosshair = Entity(parent=camera.ui)

    # Horizontal bar
    Entity(
        parent=crosshair,
        model='quad',
        scale=(size * 4, size),
        color=color,
        position=(0, 0, 0)
    )

    # Vertical bar
    Entity(
        parent=crosshair,
        model='quad',
        scale=(size, size * 4),
        color=color,
        position=(0, 0, 0)
    )

    return crosshair
if crosshair ==  True:
    make_crosshair()
# ===== NETWORK =====
conn = NetworkConnection(is_host=is_host, peer_ip=None if is_host else op_ip)
conn.start()

# ===== PLAYERS =====
player = FirstPersonController(position=(0,3,0))
player.health = 10

try:
    wand = Entity(
        position=(0.3,1.78,0.42),
        model='mwand',
        parent=player,
        rotation=(0,-45,45),
        scale=0.26
    )
except Exception as e:
    print("Wand not loaded:", e)

opponent = Entity(
    model='wizard',
    scale=1.8,
    rotation=(0, 0, 0),
    enabled=False
)
opponent.health = 10

op_name = Text(text="", color=color.white, scale=1.5, position=(0.6,0.35))
bullets = []

# ===== INPUT =====
def input(key):
    if key == 'left mouse down':
        if not hasattr(camera, 'forward') or camera.forward is None:
            return
        b = Entity(
            model='sphere',
            color=color.red,
            scale=0.3,
            position=player.position + camera.forward*1.5
        )
        b.direction = camera.forward
        bullets.append(b)
        try:
            conn.safe_send({
                'type':'shoot',
                'pos':[b.position.x,b.position.y,b.position.z],
                'dir':[b.direction.x,b.direction.y,b.direction.z]
            })
        except:
            pass
    if key == 'e':
        mouse.locked = not mouse.locked
    if key == 'o':
        quit_game_safely()
    if key == 'i':
        window.fullscreen = True
    if key == 'k':
        window.fullscreen = False
def quit_game_safely():
    try:
        conn.close()
    except:
        pass
    application.quit()

# ===== UPDATE LOOP =====
def update():
    global playerscore, opponentscore

    # --- RECEIVE MESSAGES ---
    while True:
        try:
            msg = conn.safe_receive()
        except:
            break
        if not msg:
            break

        t = msg.get('type')
        if t == 'pos':
            opponent.enabled = True
            pos = msg.get('pos',[0,0,0])
            opponent.position = Vec3(*pos)
            opponent.rotation_y = msg.get('rot_y',0)
            opponent.health = msg.get('health',opponent.health)
            op_name.text = f"Playing against: {msg.get('name','Opponent')}"
            op_name.world_position = opponent.world_position + Vec3(0,2,0)
        elif t == 'shoot':
            pos = msg.get('pos',[0,0,0])
            dir = msg.get('dir',[0,0,1])
            b = Entity(model='sphere', color=color.orange, scale=0.3, position=Vec3(*pos))
            b.direction = Vec3(*dir)
            bullets.append(b)
        elif t == 'hit':
            player.health -= 1
            if player.health < 1:
                opponentscore += 1
                player.health = 10
                player.position = Vec3(0,6,0)
                print(playerscore)
                print("-")
                print(opponentscore)


    # --- SEND PLAYER POS ---
    try:
        if conn.peer_addr:
            conn.safe_send({
                'type':'pos',
                'name':playername,
                'pos':[player.position.x,player.position.y,player.position.z],
                'rot_y':player.rotation_y,
                'health':player.health
            })
    except:
        pass

    # --- UPDATE BULLETS ---
    remove_list = []
    for b in bullets:
        if not b or not b.enabled:
            remove_list.append(b)
            continue
        if not hasattr(b,'direction') or b.direction is None:
            b.direction = Vec3(0,0,1)
        b.position += b.direction * 15 * time.dt

        if abs(b.x)>100 or abs(b.z)>100 or b.y<-10:
            remove_list.append(b)
            continue

        # Opponent hit
        if opponent.enabled and b.color==color.red and distance(b.position,opponent.position)<1:
            opponent.health -= 1
            remove_list.append(b)
            try: conn.safe_send({'type':'hit'})
            except: pass
            if opponent.health <=0:
                playerscore += 1
                opponent.enabled = False
                opponent.position = Vec3(0,-999,0)
                opponent.health = 10
                print(playerscore)
                print("-")
                print(opponentscore)

        # Player hit
        if b.color==color.orange and distance(b.position,player.position)<1:
            player.health -= 1
            remove_list.append(b)
            player.position = Vec3(player.position.x,3,player.position.z)
            if player.health < 1:
                opponentscore += 1
                player.health = 10
                player.position = Vec3(0,6,0)

    for b in remove_list:
        if b in bullets:
            bullets.remove(b)
        try:
            destroy(b)
        except:
            pass

    if player.y < -4:
        player.position = Vec3(0,4,0)

# ===== EXIT HANDLER =====
app.on_exit = quit_game_safely
app.run()
