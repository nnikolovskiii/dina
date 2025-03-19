import svgwrite
import os


def generate_ai_logo():
    # Create SVG canvas
    dwg = svgwrite.Drawing('ai_logo.svg', profile='tiny', size=('200px', '200px'))

    # Color scheme: Modern tech/AI colors
    colors = {
        'deep_blue': '#0A1F44',
        'neon_blue': '#00F3FF',
        'electric_purple': '#6C00FF',
        'silver': '#E8E9EB',
        'accent_cyan': '#00FFE0'
    }

    # Base abstract shape (hexagon representing connectivity)
    hexagon = dwg.polygon(
        points=[(100, 30), (150, 60), (150, 120), (100, 150), (50, 120), (50, 60)],
        fill=colors['deep_blue'],
        stroke=colors['neon_blue'],
        stroke_width=2,
        opacity=0.95
    )
    dwg.add(hexagon)

    # Neural network-inspired elements
    for i in range(3):
        dwg.add(dwg.circle(
            center=(100 + i * 20, 100 - i * 15),
            r=12 - i * 2,
            fill=colors['electric_purple'],
            opacity=0.8
        ))

    # Connecting lines (representing data flow)
    connections = dwg.add(dwg.g(stroke=colors['accent_cyan'], stroke_width=1.5, opacity=0.7))
    connections.add(dwg.line((85, 90), (115, 110)))
    connections.add(dwg.line((110, 85), (130, 120)))
    connections.add(dwg.line((70, 110), (90, 130)))

    # Glowing center dot
    dwg.add(dwg.circle(
        center=(100, 100),
        r=8,
        fill=colors['neon_blue'],
        stroke=colors['accent_cyan'],
        stroke_width=1,
        opacity=0.9
    ))


    # Save file
    dwg.save()


if __name__ == '__main__':
    generate_ai_logo()