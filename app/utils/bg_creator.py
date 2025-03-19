import svgwrite
import math

def get_point_along_line(x1, y1, x2, y2, d):
    """Returns a point d units away from (x2, y2) towards (x1, y1)."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return (x2, y2)
    factor = d / length
    return (x2 - dx * factor, y2 - dy * factor)

def get_point_from_start(x1, y1, x2, y2, d):
    """Returns a point d units away from (x1, y1) towards (x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return (x1, y1)
    factor = d / length
    return (x1 + dx * factor, y1 + dy * factor)

def create_rounded_triangle(dwg, points, radius, fill="none", glow=False, filter_id=None, **kwargs):
    A, B, C = points
    path_data = []

    # Start near B on AB
    p1 = get_point_along_line(A[0], A[1], B[0], B[1], radius)
    path_data.append(f"M {p1[0]:.2f} {p1[1]:.2f}")

    # Quadratic curve around B to BC
    p2 = get_point_from_start(B[0], B[1], C[0], C[1], radius)
    path_data.append(f"Q {B[0]} {B[1]} {p2[0]:.2f} {p2[1]:.2f}")

    # Line to near C on BC
    p3 = get_point_along_line(B[0], B[1], C[0], C[1], radius)
    path_data.append(f"L {p3[0]:.2f} {p3[1]:.2f}")

    # Quadratic curve around C to CA
    p4 = get_point_from_start(C[0], C[1], A[0], A[1], radius)
    path_data.append(f"Q {C[0]} {C[1]} {p4[0]:.2f} {p4[1]:.2f}")

    # Line to near A on CA
    p5 = get_point_along_line(C[0], C[1], A[0], A[1], radius)
    path_data.append(f"L {p5[0]:.2f} {p5[1]:.2f}")

    # Quadratic curve around A to AB
    p6 = get_point_from_start(A[0], A[1], B[0], B[1], radius)
    path_data.append(f"Q {A[0]} {A[1]} {p6[0]:.2f} {p6[1]:.2f}")

    # Close path
    path_data.append("Z")

    extra_attribs = {}
    if glow and filter_id:
        extra_attribs["filter"] = f"url(#{filter_id})"

    dwg.add(dwg.path(d=" ".join(path_data), fill=fill, **extra_attribs, **kwargs))

def create_glow_filter(dwg, color, filter_id):
    """Creates a glow filter tinted with the given color."""
    # Create a filter with extra space so the glow isn't clipped.
    f = dwg.defs.add(dwg.filter(id=filter_id, x="-50%", y="-50%", width="200%", height="200%"))
    # Blur the alpha channel of the shape
    f.feGaussianBlur(in_="SourceAlpha", stdDeviation=4, result="blur")
    # Flood with the desired glow color
    f.feFlood(flood_color=color, result="glowColor")
    # Composite the flood with the blurred alpha to create a colored glow
    f.feComposite(in_="glowColor", in2="blur", operator="in", result="coloredBlur")
    # Merge the colored glow with the original graphic
    f.feMerge(layernames=["coloredBlur", "SourceGraphic"])

# Create the drawing
dwg = svgwrite.Drawing('stacked_triangles.svg', size=('500px', '500px'))

# Base triangle templates and their colors
base_triangle_li = [
    [(220, 0), (0, 0), (0, 230)],
    [(210, 0), (0, 0), (0, 230)],
    [(200, 0), (0, 0), (0, 220)]
]
colors = ['#af40ff', '#c97dfb', '#ddacff']
radius_li = [30, 30, 30]

# Create 3 stacked triangles with a glow effect (each using its own colored filter)
for i in range(3):
    offset_y = i * 10
    offset_x = i * 12
    shifted_points = [(x + offset_x, y + offset_y) for (x, y) in base_triangle_li[i]]
    # Define a unique filter id for each triangle
    filter_id = f"glow_{i}"
    create_glow_filter(dwg, colors[i], filter_id)
    create_rounded_triangle(dwg,
                            points=shifted_points,
                            radius=radius_li[i],
                            fill=colors[i],
                            glow=True,
                            filter_id=filter_id)

dwg.save()
