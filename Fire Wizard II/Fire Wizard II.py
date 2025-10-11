# stable_multiplayer_fps.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from networking import *
from random import randint

# ===== INPUT =====
op_ip = input("Enter opponent IP (leave blank to host): ").strip()
playername = input("Enter your name: ").strip() or "Player"
is_host = (op_ip == "")
playerscore = 0
opponentscore=0
# ===== NETWORK =====
conn = NetworkConnection(is_host=is_host, peer_ip=None if is_host else op_ip)

# ===== URSINA SETUP =====
app = Ursina()
window.fullscreen = False
Sky()
floor = Entity(model='cube', scale=(40,1,40), collider='box', texture='grass')

# ===== PLAYERS =====
player = FirstPersonController(position=(0,3,0))
player.health = 10
wand = Entity(position=(0.3, 1.78, 0.42), model='mwand', parent=player, rotation=(0,-45,45), scale=0.26)

opponent = Entity(model='wizard', scale=1.8, rotation=(-22, 0, 45), enabled=False)
opponent.health = 10
op_name = Text(text="", color=color.white, scale=1.5, position=(0.6,0.35))

bullets = []

# ===== INPUT =====
def input(key):
    if key == 'left mouse down':
        b = Entity(model='sphere', color=color.red, scale=0.3,
                   position=player.position + camera.forward*1.5)
        b.direction = camera.forward
        bullets.append(b)
        conn.safe_send({
            'type':'shoot',
            'pos':[b.position.x,b.position.y,b.position.z],
            'dir':[b.direction.x,b.direction.y,b.direction.z]
        })
    if key == 'e':
        mouse.locked = not mouse.locked
    if key == 'o':
        quit_game()

def quit_game():
    conn.close()
    application.quit()

# ===== UPDATE LOOP =====
def update():
    global playerscore, opponentscore
    # --- Receive opponent messages ---
    while True:
        msg = conn.safe_receive()
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
            b = Entity(model='sphere', color=color.blue, scale=0.3,
                       position=Vec3(*pos))
            b.direction = Vec3(*dir)
            bullets.append(b)
        elif t == 'hit':
            player.health -= 1
            print(f"You got hit! HP={player.health}")

    # --- Send player position ---
    conn.safe_send({
        'type':'pos',
        'name':playername,
        'pos':[player.position.x,player.position.y,player.position.z],
        'rot_y':player.rotation_y,
        'health':player.health
    })

    # --- Update bullets ---
    remove_list = []
    for b in bullets:
        if not b or not b.enabled:
            remove_list.append(b)
            continue
        b.position += b.direction * 15 * time.dt
        if abs(b.x)>100 or abs(b.z)>100 or b.y<-10:
            remove_list.append(b)
            continue
        # Opponent hit
        if opponent.enabled and b.color==color.red and distance(b.position,opponent.position)<1:
            opponent.health -= 1
            print(f"Opponent hit! HP={opponent.health}")
            remove_list.append(b)
            conn.safe_send({'type':'hit'})
            if opponent.health<=0:
                playerscore += 1
                print(playerscore, opponentscore)
        # Player hit
        if b.color==color.blue and distance(b.position,player.position)<1:
            player.health -= 1
            print(f"You got hit! HP={player.health}")
            remove_list.append(b)
            player.position=(player.x,3,player.y)
        if player.health < 1:
            opponentscore += 1
            print(playerscore, opponentscore)
            player.position = (0, 6, 0)
    for b in remove_list:
        if b in bullets:
            bullets.remove(b)
        try:
            destroy(b)
        except:
            pass

    if player.y<-4:
        player.position=(0,4,0)

app.on_exit = quit_game
app.run()
