"""
================================================================================
          PROJECT: BLACK RUSSIA - THE FORBIDDEN MONOLITH
          VERSION: 4.0 (AUCTION FINAL BOSS EDITION)
          FEATURES: PHYSICS BUGS, FLYING BELAZ, APK TEXTURE INJECTION
================================================================================
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import zipfile, io, os, random, math
from PIL import Image

# --- КУЛЬТОВЫЕ НАСТРОЙКИ ---
APK_PATH = r"C:\Users\Ирина\Downloads\Telegram Desktop\base (2).apk"
MONEY = 1500000
LOG_PREFIX = "[BR_GOD_MODE]"


# --- СИСТЕМА ИНЪЕКЦИИ РЕСУРСОВ ---
def get_apk_asset(internal_path, name):
    if os.path.exists(APK_PATH):
        try:
            with zipfile.ZipFile(APK_PATH, 'r') as z:
                with z.open(internal_path) as f:
                    img = Image.open(io.BytesIO(f.read()))
                    img.save(f"cache_{name}.png")
                    return load_texture(f"cache_{name}.png")
        except:
            return 'white_cube'
    return 'white_cube'


# --- ИНИЦИАЛИЗАЦИЯ ДВИЖКА ---
app = Ursina(title="GTA 7: BELAZ MONOLITH", borderless=False, development_mode=False)
window.fps_counter.enabled = False
Entity.default_shader = lit_with_shadows_shader

# Текстуры (Натягиваем всё, что нашли)
GROUND_TEX = get_apk_asset("res/drawable-nodpi-v4/bg_launcher.png", "ground")
LOGO_TEX = get_apk_asset("res/mipmap-xxhdpi-v4/ic_launcher_round.png", "logo")

# --- ИНТЕРФЕЙС (HUD И ИНВЕНТАРЬ) ---
fps_text = Text(text="FPS: 0", position=(0.7, 0.48), scale=1.2, color=color.lime, parent=camera.ui)
money_text = Text(text=f"CASH: ${MONEY:,}", position=(-0.85, 0.48), scale=1.5, color=color.gold, parent=camera.ui)


class Inventory(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, model='quad', scale=(0.5, 0.6), color=color.black90, enabled=False)
        Text(text="ИНВЕНТАРЬ (МАГНАТ)", parent=self, y=0.45, origin=(0, 0), scale=2, color=color.orange)
        for i in range(12):
            x, y = (i % 4) * 0.2 - 0.3, (i // 4) * -0.2 + 0.2
            Entity(parent=self, model='quad', scale=(0.15, 0.15), x=x, y=y, color=color.dark_gray)
        self.hint = Text(text="[I] ЗАКРЫТЬ", parent=self, y=-0.45, origin=(0, 0), scale=1)


inv = Inventory()

# --- МИР И ГРАФИКА ---
Sky(texture='sky_sunset')
ground = Entity(model='plane', scale=2500, texture=GROUND_TEX, collider='box', shader=lit_with_shadows_shader)
sun_parent = Entity()
sun = DirectionalLight(parent=sun_parent, y=30, rotation=(45, 90, 0), shadows=True)

# ГЛАВНЫЙ ГЕРОЙ - БЕЛАЗ
belaz = Entity(model='cube', texture=GROUND_TEX, color=color.orange, scale=(20, 12, 35), position=(40, 6, 80),
               collider='box')
belaz_label = Text(text="[ BELAZ-75710 ]", parent=belaz, y=1.2, scale=15, color=color.yellow)

# ЖЕРТВЫ (Трафик)
traffic = []
for i in range(20):
    t = Entity(model='cube', texture=LOGO_TEX, scale=(4, 2, 7),
               position=(random.randint(-300, 300), 1, random.randint(-300, 300)), collider='box')
    traffic.append(t)

# --- ИГРОК И ФИЗИКА ---
player = FirstPersonController(y=5, speed=15)
is_driving = False
is_falling = False


def update():
    global is_driving, is_falling, MONEY

    fps_text.text = f"FPS: {round(1 / time.dt) if time.dt > 0 else 0}"

    # ФИЗИКА "МЫЛО" (Падение на бегу)
    if not is_driving and player.enabled and not is_falling:
        if held_keys['shift'] and (held_keys['w'] or held_keys['a']):
            if random.random() < 0.005: fall_logic()

    # ЛОГИКА УПРАВЛЕНИЯ БЕЛАЗОМ
    if is_driving:
        # Плавные повороты (lerp)
        target_rot = (held_keys['d'] - held_keys['a']) * 45
        belaz.rotation_y = lerp(belaz.rotation_y, belaz.rotation_y + target_rot, time.dt * 2)

        # Движение
        mult = 4 if held_keys['shift'] else 1
        belaz.position += belaz.forward * (held_keys['w'] - held_keys['s']) * 40 * mult * time.dt

        # КАМЕРА (БЛИЗКИЙ ЭКШЕН)
        target_cam_pos = belaz.position + belaz.up * 20 - belaz.forward * 50
        camera.position = lerp(camera.position, target_cam_pos, time.dt * 5)
        camera.look_at(belaz.position + belaz.up * 5)

        # БАГ: "ДРИФТ В КОСМОСЕ"
        if held_keys['space']:
            belaz.rotation_z += 600 * time.dt
            belaz.y += 10 * time.dt  # Левитация
            belaz_label.text = "РЕЖИМ ПОЛЕТА: ON"
            belaz_label.color = color.cyan
        else:
            belaz.rotation_z = lerp(belaz.rotation_z, 0, time.dt * 5)
            belaz_label.text = "[ BELAZ-75710 ]"
            belaz_label.color = color.yellow

        # ДАВКА И БАГ МАСШТАБА
        for e in traffic:
            if distance(belaz.position, e.position) < 22 and e.scale_y > 0.5:
                e.scale_y = 0.1
                e.color = color.red
                MONEY += 50000
                money_text.text = f"CASH: ${MONEY:,}"
                camera.shake(duration=0.3, magnitude=4)
                # Рандомный баг колес
                belaz.scale_x += random.uniform(-0.2, 0.2)


def fall_logic():
    global is_falling
    is_falling = True
    player.enabled = False
    camera.animate_rotation_x(85, duration=0.2)
    t = Text(text="ПОДСКОЛЬЗНУЛСЯ НА МЕДВЕДЕ!", position=(0, 0), scale=3, color=color.red, origin=(0, 0))
    destroy(t, delay=2)
    invoke(setattr, player, 'enabled', True, delay=2)
    invoke(setattr, globals(), 'is_falling', False, delay=2)
    invoke(camera.animate_rotation_x, 0, duration=0.5, delay=2)


def input(key):
    global is_driving
    if key == 'i':
        inv.enabled = not inv.enabled
        mouse.locked = not inv.enabled
        player.enabled = not inv.enabled

    if key == 'e':
        # ВХОД
        if not is_driving and distance(player.position, belaz.position) < 40:
            is_driving = True
            player.enabled = False
            mouse.locked = False
        # ВЫХОД
        elif is_driving:
            is_driving = False
            camera.parent = scene
            camera.position = (0, 0, 0)
            player.position = belaz.position + belaz.right * 35 + Vec3(0, 5, 0)
            player.enabled = True
            mouse.locked = True
            belaz.scale = (20, 12, 35)  # Сброс багов масштаба

    if key == 'g' and is_driving:
        belaz.animate_y(belaz.y + 40, duration=1, curve=curve.out_expo)
        belaz.animate_rotation_x(belaz.rotation_x + 360, duration=1)

    if key == 'escape':
        if inv.enabled:
            inv.enabled = False
            mouse.locked = True
            player.enabled = True
        else:
            application.quit()


print(f"{LOG_PREFIX} Лот готов к аукциону. Не забудьте надеть шлем.")
app.run()