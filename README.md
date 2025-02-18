<p align="center"><img align="center" src=https://i.imgur.com/n9oeT4C.png><p>
<p align="center"><i>magpylib - A simple and user friendly magnetic toolbox for Python 3</i><p>




---
<div>
<p align="center"> Builds: 
<a href="https://dev.azure.com/magpylib/magpylib/_build/latest?definitionId=1&branchName=master"> <img align='center' src="https://dev.azure.com/magpylib/magpylib/_apis/build/status/magpylib.magpylib?branchName=master"> </a>
<a href="https://circleci.com/gh/magpylib/magpylib"> <img align='center' src="https://circleci.com/gh/magpylib/magpylib.svg?style=svg"> </a>
<a href="https://ci.appveyor.com/project/OrtnerMichael/magpylib/branch/master"> <img align='center' src="https://ci.appveyor.com/api/projects/status/0mka52e1tqnkgnx3/branch/master?svg=true"> </a>
<a href="https://app.fossa.io/projects/git%2Bgithub.com%2Fmagpylib%2Fmagpylib?ref=badge_shield" alt="FOSSA Status"><img src="https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmagpylib%2Fmagpylib.svg?type=shield"/></a>
</p>

<p align="center"> Documentation: 
<a href="https://magpylib.readthedocs.io/en/latest/"> <img align='center' src="https://readthedocs.org/projects/magpylib/badge/?version=latest"> </a>
<a href="https://www.gnu.org/licenses/agpl-3.0"> <img align='center' src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg"> </a>
</p>

<p align="center"> Test Coverage: 
<a href="https://codecov.io/gh/magpylib/magpylib">
  <img src="https://codecov.io/gh/magpylib/magpylib/branch/master/graph/badge.svg" />
</a>
</p>

<p align="center"> Downloads: 
<a href="https://pypi.org/project/magpylib/">
<img src="https://badge.fury.io/py/magpylib.svg" alt="PyPI version" height="18"></a>
</p>


</div>


## What is magpylib ?
- Python package for calculating magnetic fields of magnets, currents and
  moments (sources).
- It provides convenient methods to generate, geometrically manipulate, group
  and vizualize assemblies of sources.
- The magnetic fields are determined from underlying (semi-analytical)
  solutions which results in fast computation times (sub-millisecond) and
  requires little computation power.

<p align="center">
    <img align='center' src="https://magpylib.readthedocs.io/en/latest/_images/sourceBasics.svg">
</p>


### Dependencies: 
_Python3.6+_, _Numpy_, _Matplotlib_

---

### Guides & Installation:

**Please [check out our documentation](https://magpylib.readthedocs.io/en/latest) for getting started and more info!**

(_Installation methods are still WIP._)

Installing this project using pip:
- run the following in your Python environment terminal:
  ```
  pip install magpylib
  ```

Installing this project locally:
- Clone this repository to your machine.
- In the directory, run `pip install .` in your conda terminal.


### Example:

- Two permanent magnets with axial magnetization are created and geometrically manipulated. They are grouped in a single collection and the system geometry is displayed using a supplied method.
- The total magnetic field that is generated by the collection is calculated on a grid in the xz-plane and is displayed using matplotlib.

**Program output:**
![](https://raw.githubusercontent.com/magpylib/magpylib/master/docs/_static/images/documentation/examplePlot.jpg)

**Code:**
```python
# imports
import numpy as np
import matplotlib.pyplot as plt
import magpylib as magpy
 
# create magnets
magnet1 = magpy.source.magnet.Box(mag=[0,0,600],dim=[3,3,3],pos=[-4,0,3])
magnet2 = magpy.source.magnet.Cylinder(mag=[0,0,500], dim=[3,5], pos=[0,0,0])

# manipulate magnets
magnet1.rotate(45,[0,1,0],anchor=[0,0,0])
magnet2.move([5,0,-4])

# collect magnets
pmc = magpy.Collection(magnet1,magnet2)

# display system geometry
pmc.displaySystem()

# calculate B-fields on a grid
xs = np.linspace(-10,10,20)
zs = np.linspace(-10,10,20)
Bs = np.array([[pmc.getB([x,0,z]) for x in xs] for z in zs])

# display fields using matplotlib
fig, ax = plt.subplots()
X,Y = np.meshgrid(xs,zs)
U,V = Bs[:,:,0], Bs[:,:,2]
ax.streamplot(X, Y, U, V, color=np.log(U**2+V**2), density=1.5)
plt.show() 
```






## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmagpylib%2Fmagpylib.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmagpylib%2Fmagpylib?ref=badge_large)