# This file is part of OnDA.
#
# OnDA is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# OnDA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with OnDA.
# If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2019 Deutsches Elektronen-Synchrotron DESY,
# a research centre of the Helmholtz Association.
"""
Geometry utilities.

Functions to manipulate geometry information.
"""
from __future__ import absolute_import, division, print_function

import collections

import numpy


PixelMaps = collections.namedtuple(
    typename="PixelMaps", field_names=["x", "y", "z", "r", "phi"]
)
"""
Pixel maps storing geometry information.

The first three fields, named "x" "y" and "z" respectively, store the pixel maps for
the x,the y and the z coordinates. The fourth field, named "r", is a pixel map storing
the distance of each pixel in the data array from the center of the reference system.
The fifth field, 'phi', is instead a pixel map that stores the angles that vectors
connecting each pixel with the center of the reference system make with respect to the
x axis of the reference system.
"""


def compute_pix_maps(geometry):
    """
    Computes pixel maps from a CrystFEL geometry object.

    Takes as input a CrystFEL-style geometry object (A dictionary returned by the
    function load_crystfel_geometry function in the crystfel_utils module) and returns a
    :obj:`PixelMaps` tuple . The origin the reference system used by the pixel maps is
    set at the beam interaction point.

    Args:

        geometry (Dict): A CrystFEL geometry object (A dictionary returned by the
            :obj:`cfelpyutils.crystfel_utils.load_crystfel_geometry` function).

    Returns:

        PixelMaps: A :obj:`PixelMaps` tuple storing the pixel maps (numpy.ndarrays of
        float).
    """
    max_fs_in_slab = numpy.array(
        [geometry["panels"][k]["max_fs"] for k in geometry["panels"]]
    ).max()
    max_ss_in_slab = numpy.array(
        [geometry["panels"][k]["max_ss"] for k in geometry["panels"]]
    ).max()

    x_map = numpy.zeros(
        shape=(max_ss_in_slab + 1, max_fs_in_slab + 1), dtype=numpy.float32
    )
    y_map = numpy.zeros(
        shape=(max_ss_in_slab + 1, max_fs_in_slab + 1), dtype=numpy.float32
    )
    z_map = numpy.zeros(
        shape=(max_ss_in_slab + 1, max_fs_in_slab + 1), dtype=numpy.float32
    )

    # Iterates over the panels. For each panel, determines the pixel indices, then
    # computes the x,y vectors. Finally, copies the panel pixel maps into the
    # detector-wide pixel maps.
    for pan in geometry["panels"]:

        if "clen" in geometry["panels"][pan]:
            pan_clen = geometry["panels"][pan]["clen"]
        else:
            pan_clen = 0.0

        ss_grid, fs_grid = numpy.meshgrid(
            numpy.arange(
                geometry["panels"][pan]["max_ss"]
                - geometry["panels"][pan]["min_ss"]
                + 1
            ),
            numpy.arange(
                geometry["panels"][pan]["max_fs"]
                - geometry["panels"][pan]["min_fs"]
                + 1
            ),
            indexing="ij",
        )
        y_panel = (
            ss_grid * geometry["panels"][pan]["ssy"]
            + fs_grid * geometry["panels"][pan]["fsy"]
            + geometry["panels"][pan]["cny"]
        )
        x_panel = (
            ss_grid * geometry["panels"][pan]["ssx"]
            + fs_grid * geometry["panels"][pan]["fsx"]
            + geometry["panels"][pan]["cnx"]
        )
        x_map[
            geometry["panels"][pan]["min_ss"] : geometry["panels"][pan]["max_ss"] + 1,
            geometry["panels"][pan]["min_fs"] : geometry["panels"][pan]["max_fs"] + 1,
        ] = x_panel
        y_map[
            geometry["panels"][pan]["min_ss"] : geometry["panels"][pan]["max_ss"] + 1,
            geometry["panels"][pan]["min_fs"] : geometry["panels"][pan]["max_fs"] + 1,
        ] = y_panel
        z_map[
            geometry["panels"][pan]["min_ss"] : geometry["panels"][pan]["max_ss"] + 1,
            geometry["panels"][pan]["min_fs"] : geometry["panels"][pan]["max_fs"] + 1,
        ] = pan_clen

    r_map = numpy.sqrt(numpy.square(x_map) + numpy.square(y_map))
    phi_map = numpy.arctan2(y_map, x_map)

    return PixelMaps(x_map, y_map, z_map, r_map, phi_map)


def compute_min_array_size(pixel_maps):
    """
    Computes the minimum size of an array stroing the applied geometry.

    Returns the minimum size of an array that can store data on which the geometry
    information described by the pixel maps has been applied.

    The returned array shape is big enough to display all the input pixel values in the
    reference system of the physical detector. The array is also supposed to be
    centered at the center of the reference system of the detector (i.e: the beam
    interaction point).

    Args:

        pixel_maps (PixelMaps): a :obj:`PixelMaps` tuple.

    Returns:

        Tuple[int, int]: a numpy-style shape tuple storing the minimum array size.
    """
    # Find the largest absolute values of x and y in the maps. Since the returned array
    # is centered on the origin, the minimum array size along a certain axis must be at
    # least twice the maximum value for that axis. 2 pixels are added for good measure.
    x_map, y_map = pixel_maps.x, pixel_maps.y
    y_minimum = 2 * int(max(abs(y_map.max()), abs(y_map.min()))) + 2
    x_minimum = 2 * int(max(abs(x_map.max()), abs(x_map.min()))) + 2

    return (y_minimum, x_minimum)


def compute_visualization_pix_maps(geometry):
    """
    Computes pixel maps for visualization of the data.

    The pixel maps can be used for to display the data in a Pyqtgraph ImageView widget.

    Args:

        geometry (Dict): A CrystFEL geometry object (A dictionary returned by the
            :obj:`cfelpyutils.crystfel_utils.load_crystfel_geometry` function).

    Returns:

        PixelMaps: A PixelMaps tuple containing the adjusted pixel maps. The first two
        fields, named "x" and "y" respectively, store the pixel maps for the x
        coordinate and the y coordinates (as ndarrays of type int). The third, fourth
        and fifth fields ("z", "r" and "phi") are just set to None.
    """
    # Shifts the origin of the reference system from the beam position to the top-left
    # of the image that will be displayed. Computes the size of the array needed to
    # display the data, then use this information to estimate the magnitude of the
    # shift.
    pixel_maps = compute_pix_maps(geometry)
    min_shape = compute_min_array_size(pixel_maps)
    new_x_map = (
        numpy.array(object=pixel_maps.x, dtype=numpy.int) + min_shape[1] // 2 - 1
    )

    new_y_map = (
        numpy.array(object=pixel_maps.y, dtype=numpy.int) + min_shape[0] // 2 - 1
    )

    return PixelMaps(new_x_map, new_y_map, None, None, None)


def apply_geometry_to_data(data, geometry):
    """
    Applies geometry to data.

    Returns a new numpy array containing the input data with the geometry applied.
    The array is ready to be displayed using a library like matplotlib or pyqtgraph.

    Args:

        data (ndarray): a numpy array storing the data to which geometry should be
            applied.

        geometry (Dict): A CrystFEL geometry object (A dictionary
            returned by the
            :obj:`cfelpyutils.crystfel_utils.load_crystfel_geometry`
            function).

    Returns:

        ndarray: a new array containing the input data to which the geometry has been
        applied. The returned array shape is big enough to display all the input data
        in the reference system of the physical detector. The array is also supposed to
        be centered at the center of the reference system of the detector (i.e: the
        beam interaction point).
    """
    pixel_maps = compute_pix_maps(geometry)
    min_array_shape = compute_min_array_size(pixel_maps)
    visualization_array = numpy.zeros(min_array_shape, dtype=float)
    visual_pixel_maps = compute_visualization_pix_maps(geometry)
    visualization_array[
        visual_pixel_maps.y.flatten(), visual_pixel_maps.x.flatten()
    ] = data.ravel().astype(visualization_array.dtype)
    return visualization_array
