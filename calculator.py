# glassy_calculator_dandan.py
from __future__ import annotations
import sys, ast, random, math
from PySide6 import QtCore, QtGui, QtWidgets

# ---------------- Safe evaluator ----------------
class SafeEval:
    ALLOWED = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
        ast.USub, ast.UAdd, ast.FloorDiv
    )
    OPS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
    }
    def eval(self, text: str) -> float:
        try:
            node = ast.parse(text, mode="eval")
        except SyntaxError as e:
            raise ValueError("Invalid expression") from e
        if not self._ok(node):
            raise ValueError("Disallowed expression")
        return self._eval(node.body)
    def _ok(self, n: ast.AST) -> bool:
        if not isinstance(n, self.ALLOWED): return False
        return all(self._ok(c) for c in ast.iter_child_nodes(n))
    def _eval(self, n: ast.AST) -> float:
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)): return float(n.value)
            raise ValueError("Invalid constant")
        if isinstance(n, ast.UnaryOp):
            v = self._eval(n.operand)
            if isinstance(n.op, ast.USub): return -v
            if isinstance(n.op, ast.UAdd): return +v
            raise ValueError("Bad unary")
        if isinstance(n, ast.BinOp):
            a, b = self._eval(n.left), self._eval(n.right)
            op = type(n.op)
            if op is ast.Div and b == 0: raise ZeroDivisionError("Division by zero")
            if op in self.OPS: return float(self.OPS[op](a, b))
        raise ValueError("Bad expression")

# ---------------- Theming ----------------
class Theme:
    def __init__(self, name, bg_top, bg_bottom, text, panel, accent, btn_bg, btn_bg_hover, btn_text):
        self.name=name; self.bg_top=bg_top; self.bg_bottom=bg_bottom
        self.text=text; self.panel=panel; self.accent=accent
        self.btn_bg=btn_bg; self.btn_bg_hover=btn_bg_hover; self.btn_text=btn_text

def theme_light():
    return Theme(
        "light",
        QtGui.QColor(255,255,255),
        QtGui.QColor(220,230,255),
        QtGui.QColor(15,18,28),
        QtGui.QColor(255,255,255,200),
        QtGui.QColor(67,97,238),
        QtGui.QColor(255,255,255,160),
        QtGui.QColor(255,255,255,210),
        QtGui.QColor(20,22,30),
    )
def theme_dark():
    return Theme(
        "dark",
        QtGui.QColor(25,28,35),
        QtGui.QColor(40,46,62),
        QtGui.QColor(235,240,250),
        QtGui.QColor(35,40,52,200),
        QtGui.QColor(124,200,255),
        QtGui.QColor(255,255,255,36),
        QtGui.QColor(255,255,255,66),
        QtGui.QColor(240,245,255),
    )

# ---------------- Anime DANDAN background ----------------
class AnimeDandanBackground(QtWidgets.QWidget):
    """
    Anime-style background:
      - Pulsing rings (like a 'dan-dan' beat)
      - Radial speed-lines sweeping around the center
      - Twinkling star field
    """
    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, True)
        self.t = 0.0
        self.dt = 1.0/60.0
        self.rings = []  # list of [radius, speed, alpha]
        self._beat_accum = 0.0
        self._beat_period = 0.45  # seconds per "dan"
        self._make_speedlines()
        self._make_stars()
        self.timer = QtCore.QTimer(self, timeout=self._tick)
        self.timer.start(int(self.dt*1000))

    def setTheme(self, theme: Theme):
        self.theme = theme
        self.update()

    def _make_speedlines(self):
        random.seed(5)
        self.lines = []
        n = 72
        for i in range(n):
            self.lines.append({
                "angle": (i / n) * 360.0,
                "width": random.uniform(2.0, 5.0),
                "len_k": random.uniform(0.75, 1.15),
                "omega": random.choice([25.0, 35.0, 45.0]) * (1 if i % 2 else -1)  # deg/sec
            })

    def _make_stars(self):
        random.seed(9)
        self.stars = []
        for _ in range(120):
            self.stars.append({
                "x": random.random(),
                "y": random.random(),
                "phase": random.uniform(0, math.tau),
                "freq": random.uniform(0.8, 2.2),
                "size": random.uniform(0.8, 1.6),
            })

    def _tick(self):
        self.t += self.dt
        self._beat_accum += self.dt
        if self._beat_accum >= self._beat_period:
            self._beat_accum -= self._beat_period
            # spawn a new ring
            self.rings.append([0.0, 300.0, 0.55])  # radius px, px/s, opacity
        # update rings
        for r in self.rings:
            r[0] += r[1] * self.dt
            r[2] *= 0.985
        # drop faded rings
        self.rings = [r for r in self.rings if r[2] > 0.02]
        self.update()

    def paintEvent(self, _):
        w, h = self.width(), self.height()
        cx, cy = w/2.0, h/2.0
        R = math.hypot(w, h) * 0.75

        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        # gradient sky
        g = QtGui.QLinearGradient(0, 0, 0, h)
        g.setColorAt(0.0, self.theme.bg_top)
        g.setColorAt(1.0, self.theme.bg_bottom)
        p.fillRect(self.rect(), g)

        # subtle rotating accent glow
        glow = QtGui.QRadialGradient(QtCore.QPointF(cx, cy), R)
        accent = QtGui.QColor(self.theme.accent)
        accent.setAlpha(30)
        transparent = QtGui.QColor(self.theme.accent); transparent.setAlpha(0)
        glow.setColorAt(0.0, accent)
        glow.setColorAt(1.0, transparent)
        p.fillRect(self.rect(), glow)

        # speed lines (anime opener vibes)
        p.save()
        pen = QtGui.QPen(self.theme.accent)
        for i, ln in enumerate(self.lines):
            ang = ln["angle"] + self.t * ln["omega"]
            rad = math.radians(ang)
            length = R * ln["len_k"]
            x2 = cx + math.cos(rad) * length
            y2 = cy + math.sin(rad) * length
            alpha = 70 + int(50 * (0.5 + 0.5*math.sin(self.t*2.0 + i*0.5)))
            c = QtGui.QColor(self.theme.accent); c.setAlpha(alpha)
            pen.setColor(c); pen.setWidthF(ln["width"])
            p.setPen(pen)
            p.drawLine(QtCore.QPointF(cx, cy), QtCore.QPointF(x2, y2))
        p.restore()

        # twinkling stars
        p.save()
        p.setPen(QtCore.Qt.NoPen)
        for s in self.stars:
            b = 0.4 + 0.6 * (0.5 + 0.5*math.sin(self.t*s["freq"] + s["phase"]))
            c = QtGui.QColor(self.theme.text)
            c.setAlpha(int(160*b))
            p.setBrush(c)
            sx, sy = s["x"]*w, s["y"]*h
            r = s["size"]
            p.drawEllipse(QtCore.QRectF(sx-r, sy-r, r*2, r*2))
        p.restore()

        # pulsing rings (the "dan-dan" beat)
        p.save()
        ring_color = QtGui.QColor(self.theme.accent)
        for r in self.rings:
            ring_color.setAlpha(int(255 * r[2]))
            pen = QtGui.QPen(ring_color)
            pen.setWidth(2)
            p.setPen(pen); p.setBrush(QtCore.Qt.NoBrush)
            p.drawEllipse(QtCore.QRectF(cx-r[0], cy-r[0], r[0]*2, r[0]*2))
        p.restore()

# ---------------- Frosted panel with clipping ----------------
class FrostedPanel(QtWidgets.QFrame):
    def __init__(self, theme: Theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self._shadow = QtWidgets.QGraphicsDropShadowEffect(
            blurRadius=40, offset=QtCore.QPointF(0,10),
            color=QtGui.QColor(0,0,0,120))
        self.setGraphicsEffect(self._shadow)
        self._radius = 24
        self._update_mask()
    def setTheme(self, theme: Theme):
        self.theme = theme; self.update()
    def _update_mask(self):
        r = self.rect().adjusted(1,1,-1,-1)
        path = QtGui.QPainterPath(); path.addRoundedRect(r, self._radius, self._radius)
        self.setMask(QtGui.QRegion(path.toFillPolygon().toPolygon()))
    def resizeEvent(self, e):
        self._update_mask(); super().resizeEvent(e)
    def paintEvent(self, _):
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = self.rect().adjusted(1,1,-1,-1)
        path = QtGui.QPainterPath(); path.addRoundedRect(rect, self._radius, self._radius)
        p.setPen(QtGui.QPen(QtGui.QColor(255,255,255,70), 1))
        p.fillPath(path, self.theme.panel); p.drawPath(path)

# ---------------- Ripple button ----------------
class RippleButton(QtWidgets.QPushButton):
    def __init__(self, text: str, theme: Theme, parent=None):
        super().__init__(text, parent)
        self.theme = theme
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMinimumHeight(56)
        self.setFlat(True)
        self._center = QtCore.QPoint(0,0); self._radius = 0; self._opacity = 0.0; self._max = 40
        self._anim = QtCore.QVariantAnimation(self, duration=220,
                                              valueChanged=self._step, finished=self._end)
        self.updateTheme(theme)
    def updateTheme(self, theme: Theme):
        self.theme = theme
        t = self.theme.btn_text; b = self.theme.btn_bg; h = self.theme.btn_bg_hover
        self.setStyleSheet(f"""
            QPushButton {{
                border: none; border-radius: 14px;
                font-size: 20px; padding: 10px 14px;
                color: rgba({t.red()},{t.green()},{t.blue()},255);
                background-color: rgba({b.red()},{b.green()},{b.blue()},{b.alpha()});
            }}
            QPushButton:hover {{
                background-color: rgba({h.red()},{h.green()},{h.blue()},{h.alpha()});
            }}
        """)
    def mousePressEvent(self, e: QtGui.QMouseEvent):
        self._center = e.position().toPoint()
        self._max = max(self.width(), self.height()) * 0.9
        self._radius = 0; self._opacity = 0.35
        self._anim.stop(); self._anim.setStartValue(0.0); self._anim.setEndValue(1.0); self._anim.start()
        super().mousePressEvent(e)
    def _step(self, v):
        self._radius = int(self._max * float(v))
        self._opacity = max(0.0, 0.35 * (1.0 - float(v)))
        self.update()
    def _end(self):
        self._opacity = 0.0; self.update()
    def paintEvent(self, e):
        super().paintEvent(e)
        if self._opacity <= 0: return
        p = QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing)
        grad = QtGui.QRadialGradient(self._center, max(1, self._radius))
        c1 = QtGui.QColor(self.theme.accent); c1.setAlphaF(min(1.0, self._opacity))
        c2 = QtGui.QColor(self.theme.accent); c2.setAlpha(0)
        grad.setColorAt(0.0, c1); grad.setColorAt(1.0, c2)
        p.setPen(QtCore.Qt.NoPen); p.setBrush(grad)
        r = self._radius
        p.drawEllipse(QtCore.QRectF(self._center.x()-r, self._center.y()-r, r*2, r*2))

# ---------------- Calculator ----------------
class Calculator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glassy Calculator")
        self.resize(420, 680); self.setMinimumSize(360, 560)
        base_font = QtGui.QFont("Segoe UI" if sys.platform.startswith("win") else "Arial", 10)
        self.setFont(base_font)

        self.theme = theme_dark()
        self.eval = SafeEval()
        self.expr = ""

        # Layers (use the new anime background)
        self.bg = AnimeDandanBackground(self.theme); self.setCentralWidget(self.bg)
        self.panel = FrostedPanel(self.theme)
        root = QtWidgets.QVBoxLayout(self.bg); root.setContentsMargins(24,24,24,24); root.addWidget(self.panel)

        lay = QtWidgets.QVBoxLayout(self.panel); lay.setContentsMargins(22,22,22,22); lay.setSpacing(12)

        # Header
        hdr = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Calculator")
        tf = QtGui.QFont(self.font()); tf.setPointSize(18); tf.setBold(True); title.setFont(tf)
        title.setStyleSheet(self._label_css())
        self.theme_btn = RippleButton("Toggle theme", self.theme)
        self.theme_btn.setFixedHeight(50); self.theme_btn.clicked.connect(self.toggle_theme)
        hdr.addWidget(title); hdr.addStretch(1); hdr.addWidget(self.theme_btn)
        lay.addLayout(hdr)

        # Display
        self.display = QtWidgets.QLabel("0")
        self.display.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        df = QtGui.QFont(self.font()); df.setPointSize(30); df.setWeight(QtGui.QFont.Medium)
        self.display.setFont(df)
        self.display.setMinimumHeight(84)
        self.display.setStyleSheet(self._display_css())
        lay.addWidget(self.display)

        # Grid
        grid = QtWidgets.QGridLayout(); grid.setSpacing(10); lay.addLayout(grid, 1)
        def add(text, r, c, rs=1, cs=1):
            btn = RippleButton(text, self.theme)
            btn.clicked.connect(lambda _=False, t=text: self.on_button(t))
            grid.addWidget(btn, r, c, rs, cs)
            return btn

        add("AC", 0, 0); add("Back", 0, 1); add("(", 0, 2); add(")", 0, 3)
        add("7", 1, 0); add("8", 1, 1); add("9", 1, 2); add("/", 1, 3)
        add("4", 2, 0); add("5", 2, 1); add("6", 2, 2); add("*", 2, 3)
        add("1", 3, 0); add("2", 3, 1); add("3", 3, 2); add("-", 3, 3)
        add("0", 4, 0); add(".", 4, 1); add("%", 4, 2); add("+", 4, 3)
        eq = add("=", 5, 0, 1, 4); eq.setMinimumHeight(62)

        # Keyboard
        self.keymap = {
            QtCore.Qt.Key.Key_0: "0", QtCore.Qt.Key.Key_1: "1", QtCore.Qt.Key.Key_2: "2",
            QtCore.Qt.Key.Key_3: "3", QtCore.Qt.Key.Key_4: "4", QtCore.Qt.Key.Key_5: "5",
            QtCore.Qt.Key.Key_6: "6", QtCore.Qt.Key.Key_7: "7", QtCore.Qt.Key.Key_8: "8",
            QtCore.Qt.Key.Key_9: "9", QtCore.Qt.Key.Key_Plus: "+", QtCore.Qt.Key.Key_Minus: "-",
            QtCore.Qt.Key.Key_Asterisk: "*", QtCore.Qt.Key.Key_Slash: "/", QtCore.Qt.Key.Key_ParenLeft: "(",
            QtCore.Qt.Key.Key_ParenRight: ")", QtCore.Qt.Key.Key_Period: ".", QtCore.Qt.Key.Key_Comma: ".",
            QtCore.Qt.Key.Key_Equal: "=", QtCore.Qt.Key.Key_Return: "=", QtCore.Qt.Key.Key_Enter: "=",
            QtCore.Qt.Key.Key_Backspace: "Back", QtCore.Qt.Key.Key_Delete: "AC", QtCore.Qt.Key.Key_Percent: "%",
        }

        self._apply_theme()
        self._set_display("0")

    def _label_css(self) -> str:
        c = self.theme.text
        return f"color: rgba({c.red()},{c.green()},{c.blue()},255);"
    def _display_css(self) -> str:
        t = self.theme.text
        return (f"QLabel {{ background: transparent; border: none; padding: 6px 10px;"
                f" color: rgba({t.red()},{t.green()},{t.blue()},255); }}")
    def _apply_theme(self):
        self.bg.setTheme(self.theme); self.panel.setTheme(self.theme)
        self.display.setStyleSheet(self._display_css())
        for b in self.findChildren(RippleButton): b.updateTheme(self.theme)
        pal = self.palette(); pal.setColor(QtGui.QPalette.WindowText, self.theme.text)
        self.setPalette(pal); self.update()
    def toggle_theme(self):
        self.theme = theme_light() if self.theme.name == "dark" else theme_dark()
        self._apply_theme()
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() in self.keymap: self.on_button(self.keymap[e.key()])
        else: super().keyPressEvent(e)
    def on_button(self, t: str):
        if t == "AC": self.expr = ""; self._set_display("0"); return
        if t == "Back": self.expr = self.expr[:-1]; self._set_display(self.expr or "0"); return
        if t == "=": self._compute(); return
        self.expr += t; self._set_display(self.expr)
    def _compute(self):
        if not self.expr: return
        try:
            v = self.eval.eval(self.expr)
            text = str(int(v)) if abs(v - int(v)) < 1e-12 else (f"{v:.12f}".rstrip("0").rstrip("."))
            self.expr = text; self._set_display(text)
        except ZeroDivisionError:
            self._set_display("Division by zero"); self.expr = ""
        except Exception:
            self._set_display("Error"); self.expr = ""
    def _set_display(self, text: str):
        metrics = QtGui.QFontMetrics(self.display.font())
        elided = metrics.elidedText(text, QtCore.Qt.ElideLeft, self.display.width() - 16)
        self.display.setText(elided)
    def resizeEvent(self, e):
        self._set_display(self.expr or "0")
        super().resizeEvent(e)

# ---------------- main ----------------
if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    w = Calculator(); w.show()
    sys.exit(app.exec())
