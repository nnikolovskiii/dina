import svgwrite
from svgwrite import cm, mm
from svgwrite.gradients import LinearGradient


def create_professional_user_icon():
    # Create drawing with larger canvas
    dwg = svgwrite.Drawing('professional_user.svg', size=(120, 120), profile='full')

    # Add shadow filter
    shadow_filter = dwg.defs.add(dwg.filter(id="shadow", x="-20%", y="-20%", width="150%", height="150%"))
    shadow_filter.feGaussianBlur(in_="SourceAlpha", stdDeviation=3, result="blur")
    shadow_filter.feOffset(in_="blur", dx=2, dy=2, result="offsetBlur")
    shadow_filter.feMerge(
        dwg.feMergeNode(in_="offsetBlur"),
        dwg.feMergeNode(in_="SourceGraphic")
    )

    # Create gradient
    gradient = LinearGradient(start=(0, 0), end=(1, 1))
    gradient.add_stop_color(offset='0%', color='#2196F3')  # Material Blue
    gradient.add_stop_color(offset='100%', color='#1976D2')  # Darker Blue
    dwg.defs.add(gradient)

    # Background circle
    dwg.add(dwg.circle(
        center=(60, 60),
        r=50,
        fill=gradient.get_paint_server(),
        filter="url(#shadow)",
        opacity=0.9
    ))

    # User silhouette group
    user = dwg.g(transform="translate(60 60)")

    # Head (slightly oval)
    user.add(dwg.ellipse(
        center=(0, -25),
        r=(12, 14),  # x-radius, y-radius
        fill='white',
        opacity=0.9
    ))

    # Neck
    user.add(dwg.rect(
        insert=(-4, -10),
        size=(8, 12),
        fill='white',
        rx=2  # rounded corners
    ))

    # Shoulders (trapezoid shape)
    trapezoid = dwg.path(d=[
        ("M", -25, 5),
        ("L", 25, 5),
        ("L", 20, 25),
        ("L", -20, 25),
        ("Z",)
    ], fill='white', opacity=0.9)
    user.add(trapezoid)

    # Arms (curved)
    arm_style = {
        'stroke': 'white',
        'stroke_width': 8,
        'stroke_linecap': 'round',
        'fill': 'none'
    }

    # Left arm
    user.add(dwg.path(d=[
        ("M", -25, 15),
        ("Q", -35, 25, -40, 35)
    ], **arm_style))

    # Right arm
    user.add(dwg.path(d=[
        ("M", 25, 15),
        ("Q", 35, 25, 40, 35)
    ], **arm_style))

    # Add subtle facial features
    face = dwg.g(transform="translate(0 -25)")
    # Eyes
    face.add(dwg.ellipse(center=(-5, -2), r=(2, 3), fill='#455A64'))
    face.add(dwg.ellipse(center=(5, -2), r=(2, 3), fill='#455A64'))
    # Smile
    face.add(dwg.path(
        d=[("M", -6, 4), ("Q", 0, 8, 6, 4)],
        stroke='#455A64',
        stroke_width=1.5,
        fill='none'
    ))
    user.add(face)

    dwg.add(user)
    dwg.save()


create_professional_user_icon()