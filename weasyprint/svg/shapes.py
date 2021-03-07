"""
    weasyprint.svg.shapes
    ---------------------

    Render simple shapes.

"""

from math import atan2, pi

from .utils import normalize, point, size


def circle(svg, node, font_size):
    r = size(node.get('r'), font_size, svg.normalized_diagonal)
    if not r:
        return
    ratio = r / (pi ** .5)
    cx = size(node.get('cx'), font_size, svg.concrete_width)
    cy = size(node.get('cy'), font_size, svg.concrete_height)

    svg.stream.move_to(cx + r, cy)
    svg.stream.curve_to(cx + r, cy + ratio, cx + ratio, cy + r, cx, cy + r)
    svg.stream.curve_to(cx - ratio, cy + r, cx - r, cy + ratio, cx - r, cy)
    svg.stream.curve_to(cx - r, cy - ratio, cx - ratio, cy - r, cx, cy - r)
    svg.stream.curve_to(cx + ratio, cy - r, cx + r, cy - ratio, cx + r, cy)
    svg.stream.close()


def ellipse(svg, node, font_size):
    rx = size(node.get('rx'), font_size, svg.concrete_width)
    ry = size(node.get('ry'), font_size, svg.concrete_height)
    if not rx or not ry:
        return
    ratio_x = rx / (pi ** .5)
    ratio_y = ry / (pi ** .5)
    cx = size(node.get('cx'), font_size, svg.concrete_width)
    cy = size(node.get('cy'), font_size, svg.concrete_height)

    svg.stream.move_to(cx + rx, cy)
    svg.stream.curve_to(
        cx + rx, cy + ratio_y, cx + ratio_x, cy + ry, cx, cy + ry)
    svg.stream.curve_to(
        cx - ratio_x, cy + ry, cx - rx, cy + ratio_y, cx - rx, cy)
    svg.stream.curve_to(
        cx - rx, cy - ratio_y, cx - ratio_x, cy - ry, cx, cy - ry)
    svg.stream.curve_to(
        cx + ratio_x, cy - ry, cx + rx, cy - ratio_y, cx + rx, cy)
    svg.stream.close()


def rect(svg, node, font_size):
    width = size(node.get('width'), font_size, svg.concrete_width)
    height = size(node.get('height'), font_size, svg.concrete_height)
    if width <= 0 or height <= 0:
        return

    rx = node.get('rx')
    ry = node.get('ry')
    if rx and ry is None:
        ry = rx
    elif ry and rx is None:
        rx = ry
    rx = size(rx, font_size, svg.concrete_width)
    ry = size(ry, font_size, svg.concrete_height)

    if rx == 0 or ry == 0:
        svg.stream.rectangle(0, 0, width, height)
        return

    if rx > width / 2:
        rx = width / 2
    if ry > height / 2:
        ry = height / 2

    # Inspired by Cairo Cookbook
    # http://cairographics.org/cookbook/roundedrectangles/
    ARC_TO_BEZIER = 4 * (2 ** .5 - 1) / 3
    c1, c2 = ARC_TO_BEZIER * rx, ARC_TO_BEZIER * ry

    svg.stream.move_to(rx, 0)
    svg.stream.line_to(width - rx, 0)
    svg.stream.curve_to(width - rx + c1, 0, width, c2, width, ry)
    svg.stream.line_to(width, height - ry)
    svg.stream.curve_to(
        width, height - ry + c2, width + c1 - rx, height,
        width - rx, height)
    svg.stream.line_to(rx, height)
    svg.stream.curve_to(rx - c1, height, 0, height - c2, 0, height - ry)
    svg.stream.line_to(0, ry)
    svg.stream.curve_to(0, ry - c2, rx - c1, 0, rx, 0)
    svg.stream.close()


def line(svg, node, font_size):
    x1, x2 = tuple(
        size(node.get(position), font_size, svg.concrete_width)
        for position in ('x1', 'x2'))
    y1, y2 = tuple(
        size(node.get(position), font_size, svg.concrete_height)
        for position in ('y1', 'y2'))
    svg.stream.move_to(x1, y1)
    svg.stream.line_to(x2, y2)
    angle = atan2(y2 - y1, x2 - x1)
    node.vertices = [(x1, y1), (pi - angle, angle), (x2, y2)]


def polygon(svg, node, font_size):
    polyline(svg, node, font_size)
    svg.stream.close()


def polyline(svg, node, font_size):
    points = normalize(node.get('points'))
    if points:
        x, y, points = point(svg, points, font_size)
        svg.stream.move_to(x, y)
        node.vertices = [(x, y)]
        while points:
            x_old, y_old = x, y
            x, y, points = point(svg, points, font_size)
            angle = atan2(x - x_old, y - y_old)
            node.vertices.append((pi - angle, angle))
            svg.stream.line_to(x, y)
            node.vertices.append((x, y))
