"""
Define and display the Electromagnetic Field contour of 
an assembly of Line and Circular Currents.
"""


from magpylib import source, Collection
import numpy as np
from matplotlib import pyplot as plt
vertices = [[-8, 5, 4],
            [-8, -5, 2],
            [-7, 5, 7],
            [-4, -5, 8],
            [-1, 5, 9]]
l = source.current.Line(100, vertices, pos=[6, 6, 3], angle=80)
c = source.current.Circular(-100, 10, [-3, -2, -2], angle=50, axis=(1, 0, 0))

print(l.vertices)
print(l.getB([0, 0, 0]))

pmc = Collection(l, c)
fig = pmc.displaySystem(direc=True)

fig.suptitle("Source Currents")

xs = np.linspace(-15, 15, 50)
zs = np.linspace(-15, 15, 50)
Bs = np.array([[pmc.getB([x, 0, z]) for x in xs] for z in zs])

# display fields
fig = plt.figure(figsize=(10, 8), facecolor='w', dpi=80)
AXS = [fig.add_subplot(1, 1, i, axisbelow=True) for i in range(1, 2)]
ax1 = AXS[0]

X, Y = np.meshgrid(xs, zs)
U, V = Bs[:, :, 0], Bs[:, :, 2]
amp = np.sqrt(U**2+V**2)
#ax1.pcolormesh(X,Y,amp, cmap=plt.cm.jet, vmin=np.amin(0), vmax=np.amax(100))
ax1.contourf(X, Y, amp, np.linspace(0, 130, 100),
             cmap=plt.cm.brg)  # pylint: disable=no-member
ax1.streamplot(X, Y, U, V, color='w', density=3, linewidth=0.8)
#ax1.pcolormesh(X,Y,amp, cmap=plt.cm.RdBu, vmin=np.amin(amp), vmax=np.amax(amp))

ax1.set(
    title='B-field of a Line current assembly',
    xlabel='x-position [mm]',
    ylabel='z-position [mm]',
    xlim=[-15, 15],
    ylim=[-15, 15],
    aspect=1)
