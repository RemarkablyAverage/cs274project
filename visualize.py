import triangle
import triangle.plot as plot
import matplotlib.pyplot as plt

def vertices(ax, **kw):
    verts = kw['vertices']
    ax.scatter(*verts.T, s=.25, color='k')
    if 'labels' in kw:
        for i in range(verts.shape[0]):
            ax.text(verts[i, 0], verts[i, 1], str(i))
    if 'markers' in kw:
        vm = kw['vertex_markers']
        for i in range(verts.shape[0]):
            ax.text(verts[i, 0], verts[i, 1], str(vm[i]))

def triangles(ax, **kw):
    verts = kw['vertices']
    ax.triplot(verts[:, 0], verts[:, 1], kw['triangles'], 'ko-', markersize=.25)

def plot(ax, **kw):
    vertices(ax, **kw)
    ax.axes.set_aspect('equal')
    if 'triangles' in kw: triangles(ax, **kw)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

def main3(name, dt):
    file = open(name).read()
    v = triangle.loads(file)
    ax1 = plt.subplot(111, aspect="equal")
    plot(ax1, **v)
    plt.show()
    elef = name[:-5] + "DT" + str(dt) + ".ele"
    ele_file = open(elef).read()
    triangulation = triangle.loads(file, ele_file)
    ax2 = plt.subplot(111, sharex=ax1, sharey=ax1)
    plot(ax2, **triangulation)
    plt.show()



