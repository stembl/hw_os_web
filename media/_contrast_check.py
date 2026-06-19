def luminance(h):
    h = h.lstrip('#')
    r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
    lin = lambda c: c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)

def cr(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    return (max(l1,l2)+0.05) / (min(l1,l2)+0.05)

fixes = [
    ("D2 BW esc",             "#555555", "#FFFFFF"),
    ("D3 dark state_muted",   "#162447", "#90B8DC"),
    ("D3 dark fbw_muted",     "#5C1A1A", "#F0AEAE"),
]
for label, fill, text in fixes:
    r = cr(fill, text)
    print(f"{label}: {r:.2f} {'PASS' if r >= 4.5 else 'FAIL'}")
