#!/usr/bin/env python3
"""Controller mapping wizard - step through each button and axis to build a mapping."""
import pygame
import json
import sys
import os
import time

# Setup imports from project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from display.pixelfont import PixelFont

MAP_FILE = os.path.expanduser('~/.config/conway/controller_map.json')

# Colors (classic green terminal)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DIM = (0, 80, 0)
MID = (0, 150, 0)

STEPS = [
    # Face buttons
    {"name": "A",          "prompt": "PRESS A",              "type": "button"},
    {"name": "B",          "prompt": "PRESS B",              "type": "button"},
    {"name": "X",          "prompt": "PRESS X",              "type": "button"},
    {"name": "Y",          "prompt": "PRESS Y",              "type": "button"},
    # Menu buttons
    {"name": "START",      "prompt": "PRESS START",          "type": "button"},
    {"name": "SELECT",     "prompt": "PRESS SELECT",         "type": "button"},
    {"name": "PLUS",       "prompt": "PRESS PLUS",           "type": "button"},
    {"name": "MINUS",      "prompt": "PRESS MINUS",          "type": "button"},
    # Shoulder buttons
    {"name": "L",          "prompt": "PRESS L BUMPER",       "type": "button"},
    {"name": "R",          "prompt": "PRESS R BUMPER",       "type": "button"},
    {"name": "ZL",         "prompt": "PRESS L TRIGGER",      "type": "button"},
    {"name": "ZR",         "prompt": "PRESS R TRIGGER",      "type": "button"},
    # Stick clicks
    {"name": "L3",         "prompt": "CLICK L STICK",        "type": "button"},
    {"name": "R3",         "prompt": "CLICK R STICK",        "type": "button"},
    # D-pad (detects hat vs buttons automatically)
    {"name": "DPAD_UP",    "prompt": "PRESS D-PAD UP",       "type": "dpad"},
    {"name": "DPAD_DOWN",  "prompt": "PRESS D-PAD DOWN",     "type": "dpad"},
    {"name": "DPAD_LEFT",  "prompt": "PRESS D-PAD LEFT",     "type": "dpad"},
    {"name": "DPAD_RIGHT", "prompt": "PRESS D-PAD RIGHT",    "type": "dpad"},
    # Analog sticks
    {"name": "LEFT_X",     "prompt": "PUSH L STICK RIGHT",   "type": "axis"},
    {"name": "LEFT_Y",     "prompt": "PUSH L STICK DOWN",    "type": "axis"},
    {"name": "RIGHT_X",    "prompt": "PUSH R STICK RIGHT",   "type": "axis"},
    {"name": "RIGHT_Y",    "prompt": "PUSH R STICK DOWN",    "type": "axis"},
]


def run():
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("Controller Mapping")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    font_lg = PixelFont(scale=3)
    font_md = PixelFont(scale=2)
    font_sm = PixelFont(scale=1)
    sys_font = pygame.font.Font(None, 24)

    # --- Wait for controller ---
    pygame.joystick.init()
    joystick = None

    while joystick is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.JOYDEVICEADDED:
                pygame.joystick.init()

        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            break

        screen.fill(BLACK)
        text = font_md.render("CONNECT CONTROLLER", GREEN)
        screen.blit(text, (400 - text.get_width() // 2, 230))
        dots = font_md.render("." * (int(time.time() * 2) % 4), DIM)
        screen.blit(dots, (400 - dots.get_width() // 2, 260))
        pygame.display.flip()
        clock.tick(30)

    controller_name = joystick.get_name()

    # Brief splash showing detected controller
    screen.fill(BLACK)
    found = font_md.render("FOUND!", GREEN)
    screen.blit(found, (400 - found.get_width() // 2, 220))
    name_surf = sys_font.render(controller_name, True, MID)
    screen.blit(name_surf, (400 - name_surf.get_width() // 2, 260))
    pygame.display.flip()
    pygame.time.wait(1500)

    # --- Mapping state ---
    mapping = {
        "name": controller_name,
        "buttons": {},
        "dpad_type": None,
        "hat_index": None,
        "axes": {},
        "axis_inversion": {},
    }

    step_idx = 0
    log = []               # list of (name, description) tuples
    recorded_at = 0        # timestamp of last recording
    RECORD_DELAY = 0.45    # seconds to show confirmation
    skip_dpad_rest = False  # True if d-pad uses hat (skip remaining d-pad steps)
    axis_snapshot = None    # resting axis values for delta detection
    running = True

    while running:
        now = time.time()

        if step_idx >= len(STEPS):
            break

        step = STEPS[step_idx]

        # Auto-fill remaining d-pad steps when hat detected
        if step["type"] == "dpad" and skip_dpad_rest and step["name"] != "DPAD_UP":
            log.append((step["name"], f"HAT {mapping['hat_index']}"))
            step_idx += 1
            continue

        # Advance after recording delay
        if recorded_at and now - recorded_at >= RECORD_DELAY:
            recorded_at = 0
            step_idx += 1
            axis_snapshot = None
            pygame.event.clear()
            continue

        # Snapshot resting axis values when entering an axis step
        if step["type"] == "axis" and axis_snapshot is None and not recorded_at:
            pygame.event.clear()
            pygame.time.wait(80)
            pygame.event.clear()
            axis_snapshot = {}
            for i in range(joystick.get_numaxes()):
                axis_snapshot[i] = joystick.get_axis(i)

        # --- Process events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                # Skip this step
                if event.key == pygame.K_SPACE and not recorded_at:
                    log.append((step["name"], "SKIP"))
                    recorded_at = now
                # Undo last step
                if event.key == pygame.K_BACKSPACE and not recorded_at and step_idx > 0:
                    step_idx -= 1
                    prev = STEPS[step_idx]
                    mapping["buttons"].pop(prev["name"], None)
                    mapping["axes"].pop(prev["name"], None)
                    mapping["axis_inversion"].pop(prev["name"], None)
                    if prev["name"] == "DPAD_UP":
                        skip_dpad_rest = False
                        mapping["dpad_type"] = None
                        mapping["hat_index"] = None
                    if log:
                        log.pop()
                    axis_snapshot = None
                continue

            if recorded_at:
                continue

            # Button steps - listen for joystick button press
            if step["type"] == "button" and event.type == pygame.JOYBUTTONDOWN:
                mapping["buttons"][step["name"]] = event.button
                log.append((step["name"], f"BTN {event.button}"))
                recorded_at = now

            # D-pad steps - accept hat or button
            elif step["type"] == "dpad":
                if event.type == pygame.JOYHATMOTION and event.value != (0, 0):
                    mapping["dpad_type"] = "hat"
                    mapping["hat_index"] = event.hat
                    log.append((step["name"], f"HAT {event.hat}"))
                    skip_dpad_rest = True
                    recorded_at = now
                elif event.type == pygame.JOYBUTTONDOWN:
                    mapping["dpad_type"] = "buttons"
                    mapping["buttons"][step["name"]] = event.button
                    log.append((step["name"], f"BTN {event.button}"))
                    recorded_at = now

            # Axis steps - detect which axis moved significantly
            elif step["type"] == "axis" and event.type == pygame.JOYAXISMOTION:
                if axis_snapshot is not None:
                    rest = axis_snapshot.get(event.axis, 0.0)
                    delta = event.value - rest
                    if abs(delta) > 0.5:
                        mapping["axes"][step["name"]] = event.axis
                        inverted = delta < 0
                        mapping["axis_inversion"][step["name"]] = inverted
                        tag = "INV" if inverted else "OK"
                        log.append((step["name"], f"AXIS {event.axis} {tag}"))
                        recorded_at = now

        if not running:
            break

        # --- Render ---
        screen.fill(BLACK)

        # Header
        title = font_sm.render("MAPPING", DIM)
        screen.blit(title, (20, 15))
        counter = font_sm.render(f"{step_idx + 1}/{len(STEPS)}", MID)
        screen.blit(counter, (780 - counter.get_width(), 15))
        pygame.draw.line(screen, DIM, (20, 32), (780, 32))

        # Main prompt
        if recorded_at:
            prompt = font_lg.render("GOT IT!", GREEN)
        else:
            prompt = font_lg.render(step["prompt"], GREEN)
        screen.blit(prompt, (400 - prompt.get_width() // 2, 55))

        # Keyboard hints
        if not recorded_at:
            hints = [("SPACE", "SKIP"), ("BACK", "UNDO"), ("ESC", "QUIT")]
            hx = 400 - 140
            for key, action in hints:
                k = font_sm.render(key, MID)
                a = font_sm.render(f" {action}  ", DIM)
                screen.blit(k, (hx, 88))
                screen.blit(a, (hx + k.get_width(), 88))
                hx += k.get_width() + a.get_width()

        # Log of completed mappings
        pygame.draw.line(screen, DIM, (20, 110), (780, 110))
        y = 122
        for name, value in log[-24:]:
            display_name = name.replace("_", " ")
            n = font_sm.render(f"{display_name}:", MID)
            v = font_sm.render(f" {value}", GREEN if value != "SKIP" else DIM)
            screen.blit(n, (30, y))
            screen.blit(v, (30 + n.get_width(), y))
            y += 14
            if y > 460:
                break

        pygame.display.flip()
        clock.tick(60)

    if not running and step_idx < len(STEPS):
        pygame.quit()
        sys.exit(1)

    # --- Save mapping ---
    os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)
    with open(MAP_FILE, 'w') as f:
        json.dump(mapping, f, indent=2)

    # --- Completion screen ---
    screen.fill(BLACK)
    done_text = font_lg.render("MAPPING COMPLETE!", GREEN)
    screen.blit(done_text, (400 - done_text.get_width() // 2, 30))

    saved = font_sm.render("SAVED!", MID)
    screen.blit(saved, (400 - saved.get_width() // 2, 68))

    pygame.draw.line(screen, DIM, (20, 85), (780, 85))

    y = 98
    for name, value in log:
        display_name = name.replace("_", " ")
        n = font_sm.render(f"{display_name}:", MID)
        v = font_sm.render(f" {value}", GREEN if value != "SKIP" else DIM)
        screen.blit(n, (30, y))
        screen.blit(v, (30 + n.get_width(), y))
        y += 14
        if y > 440:
            break

    hint = font_sm.render("PRESS ANY BUTTON TO EXIT", DIM)
    screen.blit(hint, (400 - hint.get_width() // 2, 460))
    pygame.display.flip()

    # Wait for exit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.JOYBUTTONDOWN, pygame.KEYDOWN):
                waiting = False
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    run()
