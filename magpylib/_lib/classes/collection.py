# -------------------------------------------------------------------------------
# magpylib -- A Python 3 toolbox for working with magnetic fields.
# Copyright (C) Silicon Austria Labs, https://silicon-austria-labs.com/,
#               Michael Ortner <magpylib@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see <https://www.gnu.org/licenses/>.
# The acceptance of the conditions of the GNU Affero General Public License are
# compulsory for the usage of the software.
#
# For contact information, reach out over at <magpylib@gmail.com> or our issues
# page at https://www.github.com/magpylib/magpylib/issues.
# -------------------------------------------------------------------------------

######### Type hint definitions ########
# These aren't type hints, but look good 
# in Spyder IDE. Pycharm recognizes it.
from typing import Tuple
x=y=z=0.0 # Position Vector
numpyArray=[[x,y,z]] # List of Positions
listOfPos=[[x,y,z]] # List of Positions
#######################################
# %% IMPORTS
from copy import deepcopy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from numpy import array, amax, linspace, pi, sin, cos, finfo
from magpylib._lib.classes.magnets import Box, Cylinder, Sphere
from magpylib._lib.classes.currents import Line, Circular
from magpylib._lib.classes.moments import Dipole
from magpylib._lib.classes.fieldsampler import FieldSampler
from magpylib._lib.utility import drawCurrentArrows, drawMagAxis, drawDipole, isDisplayMarker
from magpylib._lib.utility import addListToCollection, isSource,  addUniqueSource, isPosVector
from magpylib._lib.mathLibPrivate import angleAxisRotation, fastNorm3D
from magpylib._lib.mathLibPublic import rotatePosition


class Collection(FieldSampler):
    """
    Create a collection of :mod:`magpylib.source` objects for common manipulation.

    Parameters
    ----------
    sources : source objects
        python magic variable passes source objects to the collection at initialization.

    Attributes
    ----------
    sources : list of source objects
        List of all sources that have been added to the collection.

    Example
    -------
        >>> from magpylib import source, Collection
        >>> pm1 = source.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = source.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> pm3 = source.magnet.Sphere(mag=[0,0,1000],dim=1)
        >>> col = Collection(pm1,pm2,pm3)
        >>> B = col.getB([1,0,1])
        >>> print(B)
        [9.93360625e+01 1.76697482e-14 3.12727683e+01]
    """

    def __init__(self, *sources, dupWarning=True):

        self.sources = []

        # The following will add Sources to the Collection sources list,
        # The code is the same as the addsource method.
        # addSource() is not cast here because it will
        # put a tuple inside a tuple.
        # Iterating for this would compromise performance.
        for s in sources:
            if type(s) == Collection:
                addListToCollection(self.sources, s.sources, dupWarning)
            elif isinstance(s, list) or isinstance(s, tuple):
                addListToCollection(self.sources, s, dupWarning)
            else:
                assert isSource(s), "Argument " + str(s) + \
                    " in addSource is not a valid source for Collection"
                if dupWarning is True:
                    addUniqueSource(s, self.sources)
                else:
                    self.sources += [s]

    def removeSource(self, source_ref=-1):
        """
        Remove a source from the sources list. 

        Parameters
        ----------

        source_ref : source object or int
            [Optional] Remove the inputted source from the list
            [Optional] If given an int, remove a source at the given index position. Default: Last position.

        Return
        ------

        Popped source object.

        Raises
        ------

        ValueError
            Will be thrown if you attempt to remove a source that is not in the Collection.

        AssertionError
            Will be thrown if inputted index kwarg type is not type int

        Example
        -------

            >>> from magpylib import Collection, source
            >>> s = source.magnet.Sphere(mag=[1,2,3],dim=1,pos=[3,3,3])
            >>> s2 = source.magnet.Sphere(mag=[1,2,3],dim=2,pos=[-3,-3,-3])
            >>> m = source.moment.Dipole(moment=[1,2,3],pos=(0,0,0))
            >>> c = Collection(s,s2,m)
            >>> print(c.sources)
            [<magpylib._lib.classes.magnets.Sphere object at 0xa31eafcc>, 
            <magpylib._lib.classes.magnets.Sphere object at 0xa31ea1cc>, 
            <magpylib._lib.classes.moments.Dipole object at 0xa31ea06c>]
            >>> c.removeSource(s)
            >>> print(c.sources)
            [<magpylib._lib.classes.magnets.Sphere object at 0xa31ea1cc>, 
            <magpylib._lib.classes.moments.Dipole object at 0xa31ea06c>]
            >>> c.removeSource(s2)
            >>> print(c.sources)
            [<magpylib._lib.classes.moments.Dipole object at 0xa31ea06c>]
            >>> c.removeSource()
            >>> print(c.sources)
            []



        """
        assert type(source_ref) == int or isSource(
            source_ref), "Reference in removeSource is not an int nor a source"
        if type(source_ref) == int:
            try:
                return self.sources.pop(source_ref)
            except IndexError as e:  # Give a more helpful error message.
                raise type(e)(str(e) + ' - Index ' + str(source_ref) +
                              ' in collection source is not accessible for removeSource')
        else:
            try:
                self.sources.remove(source_ref)
            except ValueError as e:  # Give a more helpful error message.
                raise type(e)(str(e) + ' - ' + str(type(source_ref)
                                                   ) + ' not in list for removeSource')
            return source_ref

    def addSources(self, *sources, dupWarning=True):
        """
        This method adds the argument source objects to the collection.
        May also include other collections.

        Parameters
        ----------
        source : source object
            adds the source object `source` to the collection.

        dupWarning : bool
            Warn and prevent if there is an attempt to add a 
            duplicate source into the collection. Set to false to disable
            check and increase performance.

        Returns
        -------
        None

        Example
        -------
        >>> from magpylib import source, Collection
        >>> pm1 = source.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = source.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> pm3 = source.magnet.Sphere(mag=[0,0,1000],dim=1)
        >>> col = Collection(pm1)
        >>> print(col.getB([1,0,1]))
          [4.29223532e+01 1.76697482e-14 1.37461635e+01]
        >>> col.addSource(pm2)
        >>> print(col.getB([1,0,1]))
          [7.72389756e+01 1.76697482e-14 2.39070726e+01]
        >>> col.addSource(pm3)
        >>> print(
          [9.93360625e+01 1.76697482e-14 3.12727683e+01]
        """
        for s in sources:
            if type(s) == Collection:
                addListToCollection(self.sources, s.sources, dupWarning)
            elif isinstance(s, list) or isinstance(s, tuple):
                addListToCollection(self.sources, s, dupWarning)
            else:
                assert isSource(s), "Argument " + str(s) + \
                    " in addSource is not a valid source for Collection"
                if dupWarning is True:
                    addUniqueSource(s, self.sources)
                else:
                    self.sources += [s]

    def getBsweep(self, pos=numpyArray, multiprocessing=False, processes=0):

        Btotal = []

        assert all(isPosVector(item)
                   for item in pos), "Non-position vector in Collection getBsweep"
        calcFields = [s.getBsweep(pos, multiprocessing=multiprocessing,
                                  processes=processes) for s in self.sources]

        for p in range(len(pos)):  # For each position, calculate and sum all fields
            px = py = pz = 0
            for src in range(len(self.sources)):
                px += calcFields[src][p][0]  # x coord val of this position
                py += calcFields[src][p][1]  # y coord val of this position
                pz += calcFields[src][p][2]  # z coord val of this position
            Btotal.append([px, py, pz])
        return Btotal

    def getB(self, pos):
        """
        This method returns the magnetic field vector generated by the whole
        collection at the argument position `pos` in units of [mT]

        Parameters
        ----------
        pos : vec3 [mm]
            Position where magnetic field should be determined.

        Returns
        -------
        magnetic field vector : arr3 [mT]
            Magnetic field at the argument position `pos` generated by the
            collection in units of [mT].
        """
        Btotal = sum([s.getB(pos) for s in self.sources])
        return Btotal

    def move(self, displacement):
        """
        This method moves each source in the collection by the argument vector `displacement`. 
        Vector input format can be either list, tuple or array of any data
        type (float, int).

        Parameters
        ----------
        displacement : vec3 - [mm]
            Displacement vector

        Returns
        -------
        None

        Example
        -------
        >>> from magpylib import source, Collection
        >>> pm1 = source.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = source.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> print(pm1.position,pm2.position)
          [0. 0. 0.] [0. 0. 0.]
        >>> col = Collection(pm1,pm2)
        >>> col.move([1,1,1])
        >>> print(pm1.position,pm2.position)
          [1. 1. 1.] [1. 1. 1.]
        """
        for s in self.sources:
            s.move(displacement)

    def rotate(self, angle, axis, anchor='self.position'):
        """
        This method rotates each source in the collection about `axis` by `angle`. The axis passes
        through the center of rotation anchor. Scalar input is either integer or
        float. Vector input format can be either list, tuple or array of any
        data type (float, int).

        Parameters
        ----------
        angle  : scalar [deg]
            Angle of rotation in units of [deg]
        axis : vec3
            Axis of rotation
        anchor : vec3
            The Center of rotation which defines the position of the axis of rotation.
            If not specified all sources will rotate about their respective center.

        Returns
        -------
        None

        Example
        -------
        >>> from magpylib import source, Collection
        >>> pm1 = source.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = source.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> print(pm1.position, pm1.angle, pm1.axis)
          [0. 0. 0.] 0.0 [0. 0. 1.]
        >>> print(pm2.position, pm2.angle, pm2.axis)
          [0. 0. 0.] 0.0 [0. 0. 1.]
        >>> col = Collection(pm1,pm2)
        >>> col.rotate(90, [0,1,0], anchor=[1,0,0])
        >>> print(pm1.position, pm1.angle, pm1.axis)
          [1. 0. 1.] 90.0 [0. 1. 0.]
        >>> print(pm2.position, pm2.angle, pm2.axis)
          [1. 0. 1.] 90.0 [0. 1. 0.]
        """
        for s in self.sources:
            s.rotate(angle, axis, anchor=anchor)

    def displaySystem(self, markers=listOfPos, suppress=False, direc=False):
        """
        Shows the collection system in an interactive pyplot and returns a matplotlib figure identifier.



        WARNING
        -------
        As a result of an inherent problem in matplotlib the 
        Poly3DCollections z-ordering fails when bounding boxes intersect.


        Parameters
        ----------
        markers : list[scalar,scalar,scalar,[label]]
            List of position vectors to add visual markers to the display, optional label.
            Default: [[0,0,0]]

        Example
        -------
        >>> from magpylib import Collection, source
        >>> c=source.current.Circular(3,7)
        >>> x = Collection(c)
        >>> marker0 = [0,0,0,"Neutral Position"]
        >>> marker1 = [10,10,10]
        >>> x.displaySystem(markers=[ marker0,
        ...                           marker1])


        Parameters
        ----------
        suppress : bool
            If True, only return Figure information, do not show. Interactive mode must be off.
            Default: False.


        Example
        -------
        >>> ## Suppress matplotlib.pyplot.show() 
        >>> ## and returning figure from showing up
        >>> from matplotlib import pyplot 
        >>> pyplot.ioff()
        >>> figureData = Collection.displayFigure(suppress=True)

        Parameters
        ----------
        direc : bool
            Set to True to show current directions and magnetization vectors.
            Default: False


        Return    
        ------
        matplotlib Figure object
            graphics object is displayed through plt.show()

        Example
        -------
        >>> from magpylib import source, Collection
        >>> pm1 = source.magnet.Box(mag=[0,0,1000],dim=[1,1,1],pos=[-1,-1,-1],angle=45,axis=[0,0,1])
        >>> pm2 = source.magnet.Cylinder(mag=[0,0,1000],dim=[2,2],pos=[0,-1,1],angle=45,axis=[1,0,0])
        >>> pm3 = source.magnet.Sphere(mag=[0,0,1000],dim=3,pos=[-2,1,2],angle=45,axis=[1,0,0])
        >>> C1 = source.current.Circular(curr=100,dim=6)
        >>> col = Collection(pm1,pm2,pm3,C1)
        >>> col.displaySystem()

        Raises
        ------
        AssertionError
            If Marker position list is poorly defined. i.e. listOfPos=(x,y,z) instead of lisOfPos=[(x,y,z)]
        """
        fig = plt.figure(dpi=80, figsize=(8, 8))
        ax = fig.gca(projection='3d')

        # count magnets
        Nm = 0
        for s in self.sources:
            if type(s) is Box or type(s) is Cylinder or type(s) is Sphere:
                Nm += 1
        cm = plt.cm.hsv  # Linter complains about this but it is working pylint: disable=no-member
        # select colors
        colors = [cm(x) for x in linspace(0, 1, Nm+1)]

        ii = -1
        SYSSIZE = finfo(float).eps  # Machine Epsilon for moment
        dipolesList = []
        magnetsList = []
        currentsList = []
        markersList = []

        # Check input and Add markers to the Markers list before plotting
        for m in markers:
            assert isDisplayMarker(m), "Invalid marker definition in displaySystem:" + str(
                m) + ". Needs to be [vec3] or [vec3,string]"
            markersList += [m]

        for s in self.sources:
            if type(s) is Box:
                ii += 1  # increase color counter
                P = s.position
                D = s.dimension/2
                # create vertices in canonical basis
                v0 = array([D, D*array([1, 1, -1]), D*array([1, -1, -1]), D*array([1, -1, 1]),
                            D*array([-1, 1, 1]), D*array([-1, 1, -1]), -D, D*array([-1, -1, 1])])
                # rotate vertices + displace
                v = array([angleAxisRotation(s.angle, s.axis, d)+P for d in v0])
                # create faces
                faces = [[v[0], v[1], v[2], v[3]],
                         [v[0], v[1], v[5], v[4]],
                         [v[4], v[5], v[6], v[7]],
                         [v[2], v[3], v[7], v[6]],
                         [v[0], v[3], v[7], v[4]],
                         [v[1], v[2], v[6], v[5]]]
                # plot
                boxf = Poly3DCollection(
                    faces, facecolors=colors[ii], linewidths=0.5, edgecolors='k', alpha=1)
                ax.add_collection3d(boxf)
                # check system size
                maxSize = amax(abs(v))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

                if direc is True:
                    s.color = colors[ii]
                    magnetsList.append(s)
            elif type(s) is Cylinder:
                ii += 1  # increase color counter
                P = s.position
                R, H = s.dimension/2

                resolution = 20

                # vertices
                phis = linspace(0, 2*pi, resolution)
                vertB0 = array([[R*cos(p), R*sin(p), -H] for p in phis])
                vertT0 = array([[R*cos(p), R*sin(p), H] for p in phis])
                # rotate vertices+displacement
                vB = array(
                    [angleAxisRotation(s.angle, s.axis, d)+P for d in vertB0])
                vT = array(
                    [angleAxisRotation(s.angle, s.axis, d)+P for d in vertT0])
                # faces
                faces = [[vT[i], vB[i], vB[i+1], vT[i+1]]
                         for i in range(resolution-1)]
                faces += [vT, vB]
                # plot
                coll = Poly3DCollection(
                    faces, facecolors=colors[ii], linewidths=0.5, edgecolors='k', alpha=1)
                ax.add_collection3d(coll)
                # check system size
                maxSize = max([amax(abs(vB)), amax(abs(vT))])
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

                if direc is True:
                    s.color = colors[ii]
                    magnetsList.append(s)

            elif type(s) is Sphere:
                ii += 1  # increase color counter
                P = s.position
                R = s.dimension/2

                resolution = 12

                # vertices
                phis = linspace(0, 2*pi, resolution)
                thetas = linspace(0, pi, resolution)
                vs0 = [[[R*cos(phi)*sin(th), R*sin(phi)*sin(th), R*cos(th)]
                        for phi in phis] for th in thetas]
                # rotate vertices + displacement
                vs = array(
                    [[angleAxisRotation(s.angle, s.axis, v)+P for v in vss] for vss in vs0])
                # faces
                faces = []
                for j in range(resolution-1):
                    faces += [[vs[i, j], vs[i+1, j], vs[i+1, j+1], vs[i, j+1]]
                              for i in range(resolution-1)]
                # plot
                boxf = Poly3DCollection(
                    faces, facecolors=colors[ii], linewidths=0.5, edgecolors='k', alpha=1)
                ax.add_collection3d(boxf)
                # check system size
                maxSize = amax(abs(vs))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

                if direc is True:
                    s.color = colors[ii]
                    magnetsList.append(s)

            elif type(s) is Line:
                P = s.position
                vs0 = s.vertices
                # rotate vertices + displacement
                vs = array(
                    [angleAxisRotation(s.angle, s.axis, v)+P for v in vs0])
                # plot
                ax.plot(vs[:, 0], vs[:, 1], vs[:, 2], lw=1, color='k')
                # check system size
                maxSize = amax(abs(vs))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

                if direc is True:
                    # These don't move in the original object,
                    sCopyWithVertices = deepcopy(s)
                    sCopyWithVertices.vertices = vs  # We just draw the frame rotation, discard changes
                    currentsList.append(sCopyWithVertices)

            elif type(s) is Circular:
                P = s.position
                R = s.dimension/2

                resolution = 20

                # vertices
                phis = linspace(0, 2*pi, resolution)
                vs0 = array([[R*cos(p), R*sin(p), 0] for p in phis])
                # rotate vertices + displacement
                vs = array(
                    [angleAxisRotation(s.angle, s.axis, v)+P for v in vs0])
                # plot
                ax.plot(vs[:, 0], vs[:, 1], vs[:, 2], lw=1, color='k')
                # check system size
                maxSize = amax(abs(vs))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

                if direc is True:
                    # Send the Circular vertice information
                    sCopyWithVertices = deepcopy(s)
                    sCopyWithVertices.vertices = vs  # to the object drawing list
                    currentsList.append(sCopyWithVertices)

            elif type(s) is Dipole:
                P = rotatePosition(s.position, s.angle, s.axis)
                maxSize = amax(abs(P))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

                dipolesList.append(s)

        for m in markersList:  # Draw Markers
            ax.scatter(m[0], m[1], m[2], s=20, marker='x')
            if(len(m) > 3):
                zdir = None
                ax.text(m[0], m[1], m[2], m[3], zdir)
            # Goes up to 3rd Position
            maxSize = max([abs(pos) for pos in m[:3]])
            if maxSize > SYSSIZE:
                SYSSIZE = maxSize

        for d in dipolesList:
            drawDipole(d.position, d.moment,
                       d.angle, d.axis,
                       SYSSIZE, plt)

        if direc is True:  # Draw the Magnetization axes and current directions
            drawCurrentArrows(currentsList, SYSSIZE, plt)
            drawMagAxis(magnetsList, SYSSIZE, plt)

        for tick in ax.xaxis.get_ticklabels()+ax.yaxis.get_ticklabels()+ax.zaxis.get_ticklabels():
            tick.set_fontsize(12)
        ax.set_xlabel('x[mm]', fontsize=12)
        ax.set_ylabel('y[mm]', fontsize=12)
        ax.set_zlabel('z[mm]', fontsize=12)
        ax.set(
            xlim=(-SYSSIZE, SYSSIZE),
            ylim=(-SYSSIZE, SYSSIZE),
            zlim=(-SYSSIZE, SYSSIZE),
        )
        plt.tight_layout()

        if suppress is False:
            plt.show()

        return plt.gcf()
