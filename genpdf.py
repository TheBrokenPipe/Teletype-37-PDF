#!/usr/bin/env python3
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class TTYConfig:
    def __init__(this):
        this.AltSingleQuote = True
        this.DebugOutput = False
        this.FontName = "Courier"
        this.FontSize = 12
        this.LeftMargin = 72
        this.CharWidth = 7.21
        this.TopMargin = 14
        this.CharHeight = 11.95

class TTY:
    def __init__(this, filename, config):
        this._canvas = canvas.Canvas(filename, bottomup = 0, pagesize = letter)
        this._row = 0
        this._col = 0
        this._escaping = False
        this._config = config
        this._colour = (0, 0, 0)
        this._init_page()

    def _init_page(this):
        this._canvas.setFont(this._config.FontName, this._config.FontSize)
        if this._config.DebugOutput:
            this._canvas.setFillColorRGB(0, 1, 0)
        else:
            this._canvas.setFillColorRGB(this._colour[0], this._colour[1], this._colour[2])

    def putchar(this, c):
        if this._escaping:
            if c == 0x33:
                this.print_red()
            if c == 0x34:
                this.print_black()
            if c == 0x37:
                this.line_up()
            if c == 0x38:
                this.hl_up()
            elif c == 0x39:
                this.hl_down()
            this._escaping = False
            return

        if c == 0x08: # BS
            if this._col != 0:
                this._col -= 1
            return
        elif c == 0x09: # HT (8 chars)
            this._col = ((this._col // 8) + 1) * 8
            return
        elif c == 0x0A: # LF (translates to CRLF to make UNIX happy)
            this._col = 0
            this._row += 1
            return
        elif c == 0x0B: # VT (1 line)
            this._row += 1
            return
        elif c == 0x0C: # FF
            if this._row != 0:
                this._row = 66
            return
        elif c == 0x0D: # CR
            this._col = 0
            return
        elif c == 0x1B: # ESC
            this._escaping = True
            return
        elif this._config.AltSingleQuote and c == 0x27: # '
            c = ord("’")

        if this._row >= 66:
            this._row -= 66
            this._canvas.showPage()
            this._init_page()
            this.putchar(c)
            return
        this._canvas.drawString(this._config.LeftMargin + this._col * this._config.CharWidth, this._config.TopMargin + this._row * this._config.CharHeight, chr(c))
        this._col += 1

    def print_red(this):
        this._colour = (1, 0, 0)
        if not this._config.DebugOutput:
            this._canvas.setFillColorRGB(1, 0, 0)

    def print_black(this):
        this._colour = (0, 0, 0)
        if not this._config.DebugOutput:
            this._canvas.setFillColorRGB(0, 0, 0)

    def hl_up(this):
        this._row -= 0.5

    def hl_down(this):
        this._row += 0.5

    def line_up(this):
        this._row -= 1

    def export(this):
        this._canvas.showPage()
        this._canvas.save()

if sys.argv[1] == "-":
    f = sys.stdin.buffer
else:
    f = open(sys.argv[1], "rb")
data = f.read()
f.close()

cfg = TTYConfig()
# cfg.DebugOutput = True
# cfg.AltSingleQuote = False

tty = TTY(sys.argv[2], cfg)
for c in data:
    tty.putchar(c)
tty.export()
