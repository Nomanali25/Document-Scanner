# import numpy as np
# from matplotlib.lines import Line2D
# from matplotlib.artist import Artist
#
#
# class PolygonInteractor(object):
#     """
#     An polygon editor
#     """
#
#     showverts = True
#     epsilon = 5  # max pixel distance to count as a vertex hit
#
#     def __init__(self, ax, poly):
#         if poly.figure is None:
#             raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
#         self.ax = ax
#         canvas = poly.figure.canvas
#         self.poly = poly
#
#         x, y = zip(*self.poly.xy)
#         self.line = Line2D(x, y, marker='o', markerfacecolor='r', animated=True)
#         self.ax.add_line(self.line)
#
#         cid = self.poly.add_callback(self.poly_changed)
#         self._ind = None  # the active vert
#
#         canvas.mpl_connect('draw_event', self.draw_callback)
#         canvas.mpl_connect('button_press_event', self.button_press_callback)
#         canvas.mpl_connect('button_release_event', self.button_release_callback)
#         canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
#         self.canvas = canvas
#
#     def get_poly_points(self):
#         return np.asarray(self.poly.xy)
#
#     def draw_callback(self, event):
#         self.background = self.canvas.copy_from_bbox(self.ax.bbox)
#         self.ax.draw_artist(self.poly)
#         self.ax.draw_artist(self.line)
#         self.canvas.blit(self.ax.bbox)
#
#     def poly_changed(self, poly):
#         'this method is called whenever the polygon object is called'
#         # only copy the artist props to the line (except visibility)
#         vis = self.line.get_visible()
#         Artist.update_from(self.line, poly)
#         self.line.set_visible(vis)  # don't use the poly visibility state
#
#     def get_ind_under_point(self, event):
#         'get the index of the vertex under point if within epsilon tolerance'
#
#         # display coords
#         xy = np.asarray(self.poly.xy)
#         xyt = self.poly.get_transform().transform(xy)
#         xt, yt = xyt[:, 0], xyt[:, 1]
#         d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
#         indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
#         ind = indseq[0]
#
#         if d[ind] >= self.epsilon:
#             ind = None
#
#         return ind
#
#     def button_press_callback(self, event):
#         'whenever a mouse button is pressed'
#         if not self.showverts:
#             return
#         if event.inaxes is None:
#             return
#         if event.button != 1:
#             return
#         self._ind = self.get_ind_under_point(event)
#
#     def button_release_callback(self, event):
#         'whenever a mouse button is released'
#         if not self.showverts:
#             return
#         if event.button != 1:
#             return
#         self._ind = None
#
#     def motion_notify_callback(self, event):
#         'on mouse movement'
#         if not self.showverts:
#             return
#         if self._ind is None:
#             return
#         if event.inaxes is None:
#             return
#         if event.button != 1:
#             return
#         x, y = event.xdata, event.ydata
#
#         self.poly.xy[self._ind] = x, y
#         if self._ind == 0:
#             self.poly.xy[-1] = x, y
#         elif self._ind == len(self.poly.xy) - 1:
#             self.poly.xy[0] = x, y
#         self.line.set_data(zip(*self.poly.xy))
#
#         self.canvas.restore_region(self.background)
#         self.ax.draw_artist(self.poly)
#         self.ax.draw_artist(self.line)
#         self.canvas.blit(self.ax.bbox)




import numpy as np
from matplotlib.lines import Line2D
from matplotlib.artist import Artist

class PolygonInteractor:
    """
    A polygon editor for interactive adjustment of document corners.
    """

    showverts = True
    epsilon = 5  # Max pixel distance to count as a vertex hit

    def __init__(self, ax, poly):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly
        self.original_xy = self.poly.xy  # Save original points for reset

        x, y = zip(*self.poly.xy)
        self.line = Line2D(x, y, marker='o', markerfacecolor='r', animated=True)
        self.ax.add_line(self.line)

        # Add help text
        self.help_text = self.ax.text(0.05, 0.95, "Drag the corners to adjust the polygon.\nPress 'r' to reset.",
                                      transform=self.ax.transAxes, fontsize=10, verticalalignment='top',
                                      bbox=dict(facecolor='white', alpha=0.5))

        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None  # The active vertex

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)  # Add key press event
        self.canvas = canvas

    def get_poly_points(self):
        """Return the current polygon points."""
        return np.asarray(self.poly.xy)

    def draw_callback(self, event):
        """Callback for drawing the polygon and line."""
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        """Callback for polygon changes."""
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)

    def get_ind_under_point(self, event):
        """Get the index of the vertex under the mouse cursor."""
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None

        return ind

    def button_press_callback(self, event):
        """Callback for mouse button press."""
        if not self.showverts or event.inaxes is None or event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)

    def button_release_callback(self, event):
        """Callback for mouse button release."""
        if not self.showverts or event.button != 1:
            return
        self._ind = None

    def motion_notify_callback(self, event):
        """Callback for mouse motion."""
        if not self.showverts or self._ind is None or event.inaxes is None or event.button != 1:
            return
        x, y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x, y
        if self._ind == 0:
            self.poly.xy[-1] = x, y
        elif self._ind == len(self.poly.xy) - 1:
            self.poly.xy[0] = x, y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def key_press_callback(self, event):
        """Callback for key press (reset polygon)."""
        if event.key == 'r':
            self.poly.xy = self.original_xy
            self.line.set_data(zip(*self.poly.xy))
            self.canvas.draw()