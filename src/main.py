"""Quantum Stone-Paper-Scissors: tkinter UI. Run: python src/main.py"""
import math
import random
import tkinter as tk
from quantum_core import quantum_choice, get_winner

score = {"player": 0, "computer": 0, "tie": 0}
MESSAGES = {"player": "You win!", "computer": "Computer wins!", "tie": "It's a tie!"}

# ---------- Theme (display only) ----------
W, H = 480, 580
FONT = "Segoe UI"
TEXT = "#e9e7ff"
MUTED = "#8a86b8"
CARD = "#1b1740"
CARD_EDGE = "#3b3470"
RESULT_COLORS = {"player": "#4ade80", "computer": "#fb7185", "tie": "#facc15"}
MOVE_COLORS = {            # (normal, hover)
    "stone": ("#4b5563", "#6b7280"),
    "paper": ("#2563eb", "#3b82f6"),
    "scissors": ("#9333ea", "#a855f7"),
}
PARTICLE_COLORS = ["#8b5cf6", "#38bdf8", "#f472b6"]


# ---------- Helpers ----------
def lerp_color(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rr_points(x1, y1, x2, y2, r):
    """Points for a rounded rectangle (use with smooth=True)."""
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


def rounded(x1, y1, x2, y2, r=16, **kw):
    return canvas.create_polygon(rr_points(x1, y1, x2, y2, r), smooth=True, **kw)


# ---------- Game logic (unchanged behaviour) ----------
busy = False


def play(player_move: str):
    global busy
    if busy:
        return
    busy = True
    computer_move = quantum_choice()
    winner = get_winner(player_move, computer_move)
    score[winner] += 1
    measuring(player_move, computer_move, winner)


# ---------- Result animation ----------
def measuring(player_move, computer_move, winner, i=0):
    """Short 'measuring' animation before the result is revealed."""
    canvas.itemconfig(msg_text, text="Measuring qubits" + "." * (i % 4), fill=MUTED)
    canvas.itemconfig(you_move, text="?", fill=MUTED)
    canvas.itemconfig(cpu_move, text="?", fill=MUTED)
    canvas.itemconfig(card, outline=CARD_EDGE)
    if i < 5:
        root.after(100, measuring, player_move, computer_move, winner, i + 1)
    else:
        reveal(player_move, computer_move, winner)


def reveal(player_move, computer_move, winner):
    color = RESULT_COLORS[winner]
    canvas.itemconfig(you_move, text=player_move.capitalize())
    canvas.itemconfig(cpu_move, text=computer_move.capitalize())
    canvas.itemconfig(msg_text, text=MESSAGES[winner])
    for key in score:
        canvas.itemconfig(score_nums[key], text=str(score[key]))
    fade(0, color, winner)


def fade(i, color, winner):
    t = i / 8
    canvas.itemconfig(msg_text, fill=lerp_color("#ffffff", color, t))
    canvas.itemconfig(you_move, fill=lerp_color(MUTED, TEXT, t))
    canvas.itemconfig(cpu_move, fill=lerp_color(MUTED, TEXT, t))
    canvas.itemconfig(card, outline=lerp_color(CARD_EDGE, color, t))
    canvas.itemconfig(score_nums[winner], fill=lerp_color(color, TEXT, t))
    if i < 8:
        root.after(35, fade, i + 1, color, winner)
    else:
        global busy
        busy = False


# ---------- Window and canvas ----------
root = tk.Tk()
root.title("Quantum Stone Paper Scissors")
root.geometry(f"{W}x{H}")
root.resizable(False, False)

canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0, bd=0)
canvas.pack()

# Gradient background
for y in range(H):
    t = y / H
    c = lerp_color("#0f0c29", "#302b63", t * 2) if t < 0.5 else lerp_color("#302b63", "#1a1740", (t - 0.5) * 2)
    canvas.create_line(0, y, W, y, fill=c)

# Floating particles
particles = []
for _ in range(34):
    size = random.uniform(2, 5)
    color = lerp_color(random.choice(PARTICLE_COLORS), "#1a1740", 0.45)
    x, y = random.uniform(0, W), random.uniform(0, H)
    item = canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
    particles.append({"id": item, "x": x, "y": y, "s": size,
                      "vx": random.uniform(-0.25, 0.25), "vy": random.uniform(-0.5, -0.1),
                      "ph": random.uniform(0, 6.28)})

# Title with pulsing glow
glow_items = []
for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
    glow_items.append(canvas.create_text(W / 2 + dx, 52 + dy, text="QUANTUM",
                                         font=(FONT, 28, "bold"), fill="#4c3b9a"))
canvas.create_text(W / 2, 52, text="QUANTUM", font=(FONT, 28, "bold"), fill="#ffffff")
canvas.create_text(W / 2, 92, text="STONE  ·  PAPER  ·  SCISSORS",
                   font=(FONT, 11, "bold"), fill="#a78bfa")
canvas.create_line(W / 2 - 90, 114, W / 2 + 90, 114, fill="#5b4bb5", width=2)

# Move buttons (custom rounded, hover + press effects)
BTN_W, BTN_H, BTN_GAP, BTN_Y = 130, 54, 14, 138
btn_x0 = (W - (3 * BTN_W + 2 * BTN_GAP)) / 2
buttons = {}


def set_btn(move, grow, color):
    x1 = btn_x0 + buttons[move]["i"] * (BTN_W + BTN_GAP)
    canvas.coords(buttons[move]["shape"],
                  *rr_points(x1 - grow, BTN_Y - grow, x1 + BTN_W + grow, BTN_Y + BTN_H + grow, 14))
    canvas.itemconfig(buttons[move]["shape"], fill=color)


for i, move in enumerate(("stone", "paper", "scissors")):
    normal, hover = MOVE_COLORS[move]
    x1 = btn_x0 + i * (BTN_W + BTN_GAP)
    shadow = rounded(x1 + 2, BTN_Y + 4, x1 + BTN_W + 2, BTN_Y + BTN_H + 4, 14, fill="#0a0820", outline="")
    shape = rounded(x1, BTN_Y, x1 + BTN_W, BTN_Y + BTN_H, 14, fill=normal, outline="")
    label = canvas.create_text(x1 + BTN_W / 2, BTN_Y + BTN_H / 2, text=move.capitalize(),
                               font=(FONT, 13, "bold"), fill="#ffffff")
    buttons[move] = {"i": i, "shape": shape}
    tag = f"btn_{move}"
    for item in (shape, label):
        canvas.addtag_withtag(tag, item)
    canvas.tag_bind(tag, "<Enter>", lambda e, m=move, h=hover: (set_btn(m, 3, h), canvas.config(cursor="hand2")))
    canvas.tag_bind(tag, "<Leave>", lambda e, m=move, n=normal: (set_btn(m, 0, n), canvas.config(cursor="")))
    canvas.tag_bind(tag, "<ButtonPress-1>", lambda e, m=move, n=normal: set_btn(m, -2, n))
    canvas.tag_bind(tag, "<ButtonRelease-1>",
                    lambda e, m=move, h=hover: (set_btn(m, 3, h), play(m)))

# Result card
card = rounded(40, 235, W - 40, 415, 22, fill=CARD, outline=CARD_EDGE, width=2)
canvas.create_text(130, 265, text="YOU", font=(FONT, 10, "bold"), fill="#a78bfa")
canvas.create_text(W - 130, 265, text="COMPUTER", font=(FONT, 10, "bold"), fill="#38bdf8")
canvas.create_text(W / 2, 312, text="VS", font=(FONT, 11, "bold"), fill=CARD_EDGE)
you_move = canvas.create_text(130, 312, text="-", font=(FONT, 18, "bold"), fill=MUTED)
cpu_move = canvas.create_text(W - 130, 312, text="-", font=(FONT, 18, "bold"), fill=MUTED)
canvas.create_line(70, 345, W - 70, 345, fill=CARD_EDGE)
msg_text = canvas.create_text(W / 2, 380, text="Choose your move",
                              font=(FONT, 17, "bold"), fill=MUTED)

# Score cards
score_nums = {}
for n, (key, title, tcolor) in enumerate((("player", "YOU", "#a78bfa"),
                                          ("tie", "TIES", "#facc15"),
                                          ("computer", "COMPUTER", "#38bdf8"))):
    x1 = 40 + n * 140
    rounded(x1, 445, x1 + 120, 520, 16, fill=CARD, outline=CARD_EDGE, width=1)
    canvas.create_text(x1 + 60, 463, text=title, font=(FONT, 9, "bold"), fill=tcolor)
    score_nums[key] = canvas.create_text(x1 + 60, 497, text=str(score[key]),
                                         font=(FONT, 22, "bold"), fill=TEXT)

canvas.create_text(W / 2, 550, text="Computer's move comes from a 2-qubit Qiskit circuit",
                   font=(FONT, 9), fill=MUTED)

# ---------- Ambient animation ----------
tick = 0.0


def animate():
    global tick
    tick += 0.06
    for p in particles:
        p["x"] += p["vx"] + math.sin(tick + p["ph"]) * 0.25
        p["y"] += p["vy"]
        if p["y"] < -10:
            p["y"], p["x"] = H + 10, random.uniform(0, W)
        p["x"] %= W
        canvas.coords(p["id"], p["x"], p["y"], p["x"] + p["s"], p["y"] + p["s"])
    glow = lerp_color("#2b2060", "#8b5cf6", (math.sin(tick) + 1) / 2)
    for g in glow_items:
        canvas.itemconfig(g, fill=glow)
    root.after(33, animate)


animate()
root.mainloop()