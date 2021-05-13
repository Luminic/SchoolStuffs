from __future__ import annotations

import pygame
pygame.init()

from typing import Union, Optional, Callable
from enum import Enum
from numbers import Number

from graph import *

Version = ("Alpha",1,0,0)

class Point:
    """A typical 2D point class"""
    x: Number
    y: Number

    def __init__(self, x: Union[tuple[Number, Number], Number], y: Optional[Number] = None):
        """
        `Point(5, 6)`, `Point((5,6))`, and `Point([5,6])` are all valid ways of
        initializing a point with x=5 and y=6
        """

        if isinstance(x, (tuple, list)):
            self.x = x[0]
            self.y = x[1]
            assert y == None
        else:
            self.x = x
            self.y = y
            assert y != None

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"
    
    def __eq__(self, other: Point) -> bool:
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y,))
    
    def __neg__(self) -> Point:
        return Point(self.x, self.y)

    def __add__(self, other: Union[Point, Number]) -> Point:
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other, self.y + other)

    def __sub__(self, other: Union[Point, Number]) -> Point:
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other, self.y - other)
    
    def __mul__(self, other: Union[Point, Number]) -> Point:
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else:
            return Point(self.x * other, self.y * other)
    
    def __truediv__(self, other: Union[Point, Number]) -> Point:
        if isinstance(other, Point):
            return Point(self.x / other.x, self.y / other.y)
        else:
            return Point(self.x / other, self.y / other)
    
    def __radd__(self, other: Union[Point, Number]) -> Point:
        return self+other

    def __rsub__(self, other: Union[Point, Number]) -> Point:
        return -self + other

    def __rmul__(self, other: Union[Point, Number]) -> Point:
        return self*other
    
    def __rtruediv__(self, other: Union[Point, Number]) -> Point:
        return self.reciprocal() * other

    def __getitem__(self, index: int) -> Number:
        if index == 0: return self.x
        elif index == 1: return self.y
        else: raise IndexError

    def __iter__(self):
        yield self.x
        yield self.y
    
    def reciprocal(self) -> Point:
        return Point(1/self.x, 1/self.y)
    
    def map(self, func: Callable[[Number], Number]) -> Point:
        return Point(func(self.x), func(self.y))
    
    def dot(self, v2: Point) -> Number:
        return self.x * v2.x + self.y * v2.y
    
    def length(self) -> Number:
        return (self.x**2 + self.y**2)**(1/2)
    
    def normalized(self) -> Point:
        return self / self.length()
    
    def distance_to(self, p2: Point) -> Number:
        return (self-p2).length()


def point_line_segment_distance(p0: Point, p1: Point, p2: Point) -> Number:
    """Returns the distance between p0 and the line segment defined by p1 and p2"""
    direction = p2 - p1
    t = (p0-p1).dot(direction) / max(direction.dot(direction), 0.0001)

    if t < 0:
        return p0.distance_to(p1)
    elif t > 1:
        return p0.distance_to(p2)
    else:
        projection = p1 + t*direction
        return p0.distance_to(projection)


def default_vertex_namer(graph: Graph) -> str:
    """Gives a name to the nth vertex in a graph"""

    # if n < 26: return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[n]
    # else: return str(n-25)

    n = len(graph.vertices)

    letters = ""
    if n < len(letters): return letters[n]
    else: return str(n-len(letters)+1)


class GraphMaker:
    graph: Graph
    vert_pos: dict[Vertex, Point]
    
    class InteractionState(Enum):
        NONE = 0
        EDGE_CREATION = 1
        VERTEX_MOVEMENT = 2


    def __init__(self, graph: Optional[Graph] = None, vert_pos: Optional[dict[Vertex, Point]] = None, vertex_namer: Callable[[Graph],str] = None):
        # Pygame Setup
        self.viewport = [900,900]
        # self.screen = pygame.display.set_mode(self.viewport)
        # self.screen.fill((255,255,255))

        # pygame.display.set_caption('Graph Maker (%s %s.%s.%s)' %Version)
        # pygame.display.update()

        # Other Setup
        self.running = True
        self.clock = pygame.time.Clock()
        self.pressed_keys = [] # Keys currently pressed

        self.graph = graph if graph != None else Graph()
        self.vert_pos = vert_pos if vert_pos != None else dict()

        self.vertex_namer = default_vertex_namer if vertex_namer == None else vertex_namer

        self.interaction_state = GraphMaker.InteractionState.NONE
        self.selected = None

        self.vertex_radius = 8
        self.edge_width = 5
        self.loop_radius = 15
    
    def init_screen(self):
        self.screen = pygame.display.set_mode(self.viewport)
        self.screen.fill((255,255,255))
        pygame.display.set_caption('Graph Maker (%s %s.%s.%s)' %Version)
        pygame.display.update()
    
    def screen_region(self) -> pygame.Rect:
        return pygame.Rect((0,0), self.viewport)
    
    def graph_selection(self, point: Point) -> Union[Vertex, Edge, None]:
        """Returns the object on the graph `point` is over or `None`

        `point` should be in screen coordinates
        """

        for vert in self.graph.vertices:
            if point.distance_to(self.vert_pos[vert]) <= self.vertex_radius:
                return vert
        
        for edge, multiplicity in self.graph.edges.items():
            if multiplicity >= 1:
                if edge.is_loop():
                    if self.loop_radius - self.edge_width*multiplicity/2 < point.distance_to(self.vert_pos[edge.v1] + Point(self.loop_radius-self.edge_width, -self.loop_radius+self.edge_width)) < self.loop_radius + self.edge_width*multiplicity/2:
                        return edge
                else:
                    if point_line_segment_distance(point, self.vert_pos[edge.v1], self.vert_pos[edge.v2]) <= self.edge_width*multiplicity:
                        return edge

        return None
    
    def update(self):
        """Single update cycle"""
        self.screen.fill((255, 255, 255))
        self.events_check()

        self.draw_graph(self.screen, self.screen_region())
        
        self.clock.tick(60)
        pygame.display.update()
    
    def mainloop(self, init_screen: bool = True, quit_on_end: bool = True):
        """Display graph until window is closed"""

        self.running = True

        if init_screen: self.init_screen()

        while self.running: self.update()

        if quit_on_end: pygame.quit()
        else: pygame.display.quit()

    def draw_graph(self, surface: pygame.Surface, region: pygame.Rect) -> None:
        to_pyg_coords = lambda v: list(self.vert_pos[v].map(int)) if isinstance(v, Vertex) else list(v.map(int))

        for edge, multiplicity in self.graph.edges.items():
            if multiplicity >= 1:
                color = (0,0,0)
                if edge == self.selected: color = (0,0,200)

                if edge.is_loop():
                    pygame.draw.circle(
                        surface,
                        color,
                        to_pyg_coords(self.vert_pos[edge.v1] + Point(self.loop_radius-self.edge_width, -self.loop_radius+self.edge_width)),
                        self.loop_radius + self.edge_width*multiplicity/2,
                        width = self.edge_width*multiplicity)
                else:
                    pygame.draw.line(surface, color, to_pyg_coords(edge.v1), to_pyg_coords(edge.v2), width=self.edge_width*multiplicity)
        
        for vert in self.graph.vertices:
            color = (255,0,0)
            if vert == self.selected: color = (255, 100, 0)

            vert_coords = to_pyg_coords(vert)
            pygame.draw.circle(surface, color, vert_coords, self.vertex_radius)
            
            myfont = pygame.font.SysFont("monospace", 25)

            # render text
            label = myfont.render(vert.name, True, (0,100,255))
            self.screen.blit(label, vert_coords)

        if self.interaction_state == self.InteractionState.EDGE_CREATION:
            assert isinstance(self.selected, Vertex)
            pygame.draw.line(surface, (0,0,200), to_pyg_coords(self.selected), pygame.mouse.get_pos(), width=self.edge_width)
    
    def events_check(self):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN: # When a key is pressed
                self.pressed_keys.append(event.key)

                if event.key == pygame.K_BACKSPACE:
                    if isinstance(self.selected, Vertex):
                        self.graph.remove_vertex(self.selected)
                    elif isinstance(self.selected, Edge):
                        self.graph.remove_edge(self.selected)
                    self.selected = None
                
                elif event.key == pygame.K_c:
                    self.graph.clear()
                    self.selected = None
                
                elif event.key == pygame.K_p:
                    print(self.graph)

                elif event.key == pygame.K_m:
                    if pygame.K_LCTRL in self.pressed_keys:
                        print(self.graph.adjacency_matrix_list())
                    else:
                        m = self.graph.adjacency_matrix()
                        if isinstance(m, la.Matrix): m.print()

            elif event.type == pygame.KEYUP: # When a key is unpressed
                try:
                    self.pressed_keys.remove(event.key)
                except ValueError:
                    pass
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.interaction_state == self.InteractionState.NONE:
                    mouse_coords = Point(pygame.mouse.get_pos())
                    self.selected = self.graph_selection(mouse_coords)

                    if event.button == 1:
                        # Begin moving a vertex
                        if isinstance(self.selected, Vertex):
                            self.interaction_state = self.InteractionState.VERTEX_MOVEMENT
                    
                    if event.button == 3:
                        # Creating a vertex
                        if self.selected == None:
                            new_vert = Vertex(self.vertex_namer(self.graph))
                            self.graph.vertices.add(new_vert)
                            self.vert_pos[new_vert] = mouse_coords

                            self.selected = new_vert

                        # Begin creating an edge
                        elif isinstance(self.selected, Vertex):
                            self.interaction_state = self.InteractionState.EDGE_CREATION
            
            elif event.type == pygame.MOUSEBUTTONUP:
                # Finish creating an edge
                if self.interaction_state == self.InteractionState.EDGE_CREATION:
                    mouse_coords = Point(pygame.mouse.get_pos())
                    mouse_over = self.graph_selection(mouse_coords)
                    if isinstance(mouse_over, Vertex):
                        self.graph.add_edge_safe(Edge(self.selected, mouse_over), convert=True)

                self.interaction_state = self.InteractionState.NONE
            
            elif event.type == pygame.MOUSEMOTION:
                # Actually move the vertex
                if self.interaction_state == self.InteractionState.VERTEX_MOVEMENT:
                    assert isinstance(self.selected, Vertex)
                    self.vert_pos[self.selected] = Point(pygame.mouse.get_pos())

            elif event.type == pygame.QUIT:
                self.running = False


if __name__ == "__main__":
    g = GraphMaker()
    g.mainloop()
