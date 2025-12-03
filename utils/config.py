import flet as ft

# Dynamic icon/color resolution for different Flet versions
ICONS = getattr(ft, "icons", None) or getattr(ft, "Icons", None)
COLORS = getattr(ft, "colors", None) or getattr(ft, "Colors", None)

if ICONS is None:
    raise RuntimeError("No icons module found on 'ft'. Please check your flet installation.")
if COLORS is None:
    class _C: 
        BLUE = "blue"
        GREY = "grey"
        GREEN = "green"
        RED = "red"
    COLORS = _C