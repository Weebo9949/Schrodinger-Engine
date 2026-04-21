import numpy as np
import math
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
#inital perameters


#allowed functions
funcs = {
    "sin": np.sin,
    "cos": np.cos,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "pi": np.pi,
    "abs": np.abs
}

#define potential and intial state

def funcmaker(expr):
    expr = expr.replace("^", "**")
    def f(x):
        scope = {"x": x, **funcs}
        return eval(expr, {"__builtins__": {}}, scope)
    return f




#the engine 
#partion maker start from start adds spacing till end 


def run_engine(px, ranges, rangee, tend, delt, v, wfx):
    N = int((rangee - ranges) / px) + 1
    tN = int(tend / delt) + 1

    xpart = np.array([ranges + i * px for i in range(N)], dtype=float)

    H = np.zeros((N, N), dtype=complex)
    wfv = np.zeros(N, dtype=complex)

    for i in range(N):
        wfv[i] = wfx(xpart[i])

    # potential
    for i in range(N):
        H[i, i] += v(xpart[i])

    # kinetic
    shift = -0.5 / (px * px)
    for i in range(N):
        H[i, i] += -2 * shift
        if i > 0:
            H[i, i - 1] += shift
        if i < N - 1:
            H[i, i + 1] += shift

    wfdata = np.zeros((tN, N), dtype=complex)

    I = np.eye(N, dtype=complex)
    A = I + 1j * delt / 2 * H
    B = I - 1j * delt / 2 * H

    for ti in range(tN):
        wfdata[ti, :] = wfv
        b = B @ wfv
        wfv = np.linalg.solve(A, b)

    return xpart, wfdata



#gui

# -----------------------------
# 1. CREATE MAIN WINDOW
# -----------------------------
root = tk.Tk()                         # initialize the app
root.title("Shrodinger grapher")        # window title
root.geometry("1000x600")              # window size: width x height


# -----------------------------
# 2. MAIN CONTAINER FRAME
# -----------------------------
# this is like the "base layer" inside the window
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)


# -----------------------------
# 3. SPLIT INTO LEFT + RIGHT
# -----------------------------
# left = inputs, right = output (graph later)

left_panel = ttk.Frame(main_frame)
left_panel.pack(side="left", fill="y", padx=(0, 10))   # stick left

right_panel = ttk.Frame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)  # take remaining space


# -----------------------------
# 4. ADD TITLE LABEL (LEFT PANEL)
# -----------------------------
ttk.Label(left_panel, text="Simulation Parameters").pack(anchor="w")


# -----------------------------
# 5. INPUT FIELDS (ENTRY BOXES)
# -----------------------------
# each Entry = a box where user types something

# Δx
ttk.Label(left_panel, text="Δx (px)").pack(anchor="w")
px_entry = ttk.Entry(left_panel)
px_entry.insert(0, "1")   # default value
px_entry.pack(fill="x")

# x start
ttk.Label(left_panel, text="x start").pack(anchor="w")
ranges_entry = ttk.Entry(left_panel)
ranges_entry.insert(0, "0")
ranges_entry.pack(fill="x")

# x end
ttk.Label(left_panel, text="x end").pack(anchor="w")
rangee_entry = ttk.Entry(left_panel)
rangee_entry.insert(0, "10")
rangee_entry.pack(fill="x")

# t end
ttk.Label(left_panel, text="t end").pack(anchor="w")
tend_entry = ttk.Entry(left_panel)
tend_entry.insert(0, "10")
tend_entry.pack(fill="x")

# Δt
ttk.Label(left_panel, text="Δt (delt)").pack(anchor="w")
delt_entry = ttk.Entry(left_panel)
delt_entry.insert(0, "0.1")
delt_entry.pack(fill="x")


# -----------------------------
# 6. FUNCTION INPUTS
# -----------------------------
ttk.Label(left_panel, text="").pack()  # spacer

ttk.Label(left_panel, text="V(x)").pack(anchor="w")
v_entry = ttk.Entry(left_panel)
v_entry.insert(0, "0")
v_entry.pack(fill="x")

ttk.Label(left_panel, text="ψ(x,0)").pack(anchor="w")
wfx_entry = ttk.Entry(left_panel)
wfx_entry.insert(0, "sin(pi*x/10)")
wfx_entry.pack(fill="x")


# -----------------------------
# 7. RUN BUTTON
# -----------------------------
# create figure and axes
fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)

# embed into tkinter
canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill="both", expand=True)

def run_simulation():
    try:
        # get numeric parameters from the GUI
        px = float(px_entry.get())
        ranges = float(ranges_entry.get())
        rangee = float(rangee_entry.get())
        tend = float(tend_entry.get())
        delt = float(delt_entry.get())

        # get function strings and turn them into actual functions
        v = funcmaker(v_entry.get())
        wfx = funcmaker(wfx_entry.get())

        # run your engine
        xpart, wfdata = run_engine(px, ranges, rangee, tend, delt, v, wfx)

        # choose what to graph
        # first time slice = t = 0
        prob = np.abs(wfdata[0])**2

        # clear old graph
        ax.clear()

        # draw new graph
        ax.plot(xpart, prob)
        ax.set_title("Probability Density at t = 0")
        ax.set_xlabel("x")
        ax.set_ylabel("|ψ(x,t)|²")

        # refresh the canvas inside tkinter
        canvas.draw()

    except Exception as e:
        print("Error:", e)
        
ttk.Button(left_panel, text="Run Simulation", command=run_simulation).pack(pady=10)


# -----------------------------
# 8. RIGHT PANEL PLACEHOLDER
# -----------------------------
# later this will be your matplotlib graph

ttk.Label(right_panel, text="Graph will appear here").pack()


# -----------------------------
# 9. START THE GUI LOOP
# -----------------------------
root.mainloop()