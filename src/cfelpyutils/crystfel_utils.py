# This file is part of CFELPyUtils.
#
# CFELPyUtils is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# CFELPyUtils is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with OnDA. If
# not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014-2019 Deutsches Elektronen-Synchrotron DESY,
# a research centre of the Helmholtz Association.
"""
CrystFEL utilities.

This module contains Python re-implementations of some functions from the `CrystFEL
<http://www.desy.de/~twhite/crystfel>`_ software package.
"""
from __future__ import absolute_import, division, print_function

import collections
import copy
import math
import re
import sys
from typing import Any, Dict, List, Tuple, Union  # pylint: disable=unused-import

from future.utils import raise_from, viewitems


def _assplode_algebraic(value):
    # type: (str) -> List[str]
    # Re-implementation of assplode_algegraic from libcrystfel/src/detector.c.
    items = [item for item in re.split("([+-])", string=value.strip()) if item != ""]
    if items and items[0] not in ("+", "-"):
        items.insert(0, "+")
    return ["".join((items[x], items[x + 1])) for x in range(0, len(items), 2)]


def _dir_conv(direction_x, direction_y, direction_z, value):
    # type: (float, float, float, str) -> List[float]
    # Re-implementation of dir_conv from libcrystfel/src/detector.c.
    direction = [direction_x, direction_y, direction_z]
    items = _assplode_algebraic(value)
    if not items:
        raise RuntimeError("Invalid direction: {}.".format(value))
    for item in items:
        axis = item[-1]
        if axis != "x" and axis != "y" and axis != "z":
            raise RuntimeError("Invalid Symbol: {} (must be x, y or z).".format(axis))
        if item[:-1] == "+":
            value = "1.0"
        elif item[:-1] == "-":
            value = "-1.0"
        else:
            value = item[:-1]
        if axis == "x":
            direction[0] = float(value)
        elif axis == "y":
            direction[1] = float(value)
        elif axis == "z":
            direction[2] = float(value)

    return direction


def _set_dim_structure_entry(key, value, panel):
    # type: (str, str, Dict[str, Any]) -> None
    # Re-implementation of set_dim_structure_entry from libcrystfel/src/events.c.
    if panel["dim_structure"] is not None:
        dim = panel["dim_structure"]
    else:
        dim = []
    try:
        dim_index = int(key[3])
    except IndexError:
        raise RuntimeError("'dim' must be followed by a number, e.g. 'dim0')")
    except ValueError:
        raise RuntimeError("Invalid dimension number {}".format(key[3]))
    if dim_index > len(dim) - 1:
        for _ in range(len(dim), dim_index + 1):
            dim.append(None)
    if value == "ss" or value == "fs" or value == "%":
        dim[dim_index] = value
    elif value.isdigit():
        dim[dim_index] = int(value)
    else:
        raise RuntimeError("Invalid dim entry: {}.".format(value))
    panel["dim_structure"] = dim


def _parse_field_for_panel(key, value, panel):
    # type: (str, str, Dict[str, Any]) -> None
    # Re-implementation of parse_field_for_panel from libcrystfel/src/detector.c.
    if key == "min_fs":
        panel["origin_min_fs"] = int(value)
        panel["min_fs"] = int(value)
    elif key == "max_fs":
        panel["origin_max_fs"] = int(value)
        panel["max_fs"] = int(value)
    elif key == "min_ss":
        panel["origin_min_ss"] = int(value)
        panel["min_ss"] = int(value)
    elif key == "max_ss":
        panel["origin_max_ss"] = int(value)
        panel["max_ss"] = int(value)
    elif key == "corner_x":
        panel["cnx"] = float(value)
    elif key == "corner_y":
        panel["cny"] = float(value)
    elif key == "rail_direction":
        try:
            panel["rail_x"], panel["rail_y"], panel["rail_z"] = _dir_conv(
                direction_x=panel["rail_x"],
                direction_y=panel["rail_y"],
                direction_z=panel["rail_z"],
                value=value,
            )
        except RuntimeError as exc:
            raise RuntimeError("Invalid rail direction. ", exc)
    elif key == "clen_for_centering":
        panel["clen_for_centering"] = float(value)
    elif key == "adu_per_eV":
        panel["adu_per_eV"] = float(value)
    elif key == "adu_per_photon":
        panel["adu_per_photon"] = float(value)
    elif key == "rigid_group":
        panel["rigid_group"] = value
    elif key == "clen":
        try:
            panel["clen"] = float(value)
            panel["clen_from"] = None
        except ValueError:
            panel["clen"] = -1
            panel["clen_from"] = value
    elif key == "data":
        if not value.startswith("/"):
            raise RuntimeError("Invalid data location: {}".format(value))
        panel["data"] = value
    elif key == "mask":
        if not value.startswith("/"):
            raise RuntimeError("Invalid data location: {}".format(value))
        panel["mask"] = value
    elif key == "mask_file":
        panel["mask_file"] = value
    elif key == "saturation_map":
        panel["saturation_map"] = value
    elif key == "saturation_map_file":
        panel["saturation_map_file"] = value
    elif key == "coffset":
        panel["coffset"] = float(value)
    elif key == "res":
        panel["res"] = float(value)
    elif key == "max_adu":
        panel["max_adu"] = value
    elif key == "badrow_direction":
        if value == "x":
            panel["badrow"] = "f"
        elif value == "y":
            panel["badrow"] = "s"
        elif value == "f":
            panel["badrow"] = "f"
        elif value == "s":
            panel["badrow"] = "s"
        elif value == "-":
            panel["badrow"] = "-"
        else:
            print("badrow_direction must be x, t, f, s, or '-'")
            print("Assuming '-'.")
            panel["badrow"] = "-"
    elif key == "no_index":
        panel["no_index"] = bool(value)
    elif key == "fs":
        try:
            panel["fsx"], panel["fsy"], panel["fsz"] = _dir_conv(
                direction_x=panel["fsx"],
                direction_y=panel["fsy"],
                direction_z=panel["fsz"],
                value=value,
            )
        except RuntimeError as exc:
            raise RuntimeError("Invalid fast scan direction.", exc)
    elif key == "ss":
        try:
            panel["ssx"], panel["ssy"], panel["ssz"] = _dir_conv(
                direction_x=panel["ssx"],
                direction_y=panel["ssy"],
                direction_z=panel["ssz"],
                value=value,
            )
        except RuntimeError as exc:
            raise RuntimeError("Invalid slow scan direction.", exc)
    elif key.startswith("dim"):
        _set_dim_structure_entry(key=key, value=value, panel=panel)
    else:
        RuntimeError("Unrecognized field: {}".format(key))


def _parse_toplevel(key, value, detector, beam, panel):
    # type: (str, str, Dict[str, Any], Dict[str, Any], Dict[str, Any]) -> None
    # Re-implementation of parse_toplevel from libcrystfel/src/detector.c.
    if key == "mask_bad":
        try:
            detector["mask_bad"] = int(value)
        except ValueError:
            detector["mask_bad"] = int(value, base=16)
    elif key == "mask_good":
        try:
            detector["mask_good"] = int(value)
        except ValueError:
            detector["mask_good"] = int(value, base=16)
    elif key == "coffset":
        panel["coffset"] = float(value)
    elif key == "photon_energy":
        if value.startswith("/"):
            beam["photon_energy"] = 0.0
            beam["photon_energy_from"] = value
        else:
            beam["photon_energy"] = float(value)
            beam["photon_energy_from"] = None
    elif key == "photon_energy_scale":
        beam["photon_energy_scale"] = float(value)
    elif key == "peak_info_location":
        detector["peak_info_location"] = value
    elif key.startswith("rigid_group") and not key.startswith("rigid_group_collection"):
        detector["rigid_groups"][key[12:]] = value.split(",")
    elif key.startswith("rigid_group_collection"):
        detector["rigid_group_collections"][key[23:]] = value.split(",")
    else:
        _parse_field_for_panel(key=key, value=value, panel=panel)


def _check_bad_fsss(bad_region, is_fsss):
    # type: (Dict[str, Any], int) -> None
    # Re-implementation of check_bad_fsss from libcrystfel/src/detector.c.
    if bad_region["is_fsss"] == 99:
        bad_region["is_fsss"] = is_fsss
        return

    if is_fsss != bad_region["is_fsss"]:
        raise RuntimeError("You can't mix x/y and fs/ss in a bad region")

    return


def _parse_field_bad(key, value, bad):
    # type: (str, str, Dict[str, Any]) -> None
    # Re-implementation of parse_field_bad from libcrystfel/src/detector.c.
    if key == "min_x":
        bad["min_x"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "max_x":
        bad["max_x"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "min_y":
        bad["min_y"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "max_y":
        bad["max_y"] = float(value)
        _check_bad_fsss(bad_region=bad, is_fsss=False)
    elif key == "min_fs":
        bad["min_fs"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "max_fs":
        bad["max_fs"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "min_ss":
        bad["min_ss"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "max_ss":
        bad["max_ss"] = int(value)
        _check_bad_fsss(bad_region=bad, is_fsss=True)
    elif key == "panel":
        bad["panel"] = value
    else:
        raise RuntimeError("Unrecognized field: {}".format(key))

    return


def _check_point(
    name,  # type: str
    panel,  # type: Dict[str, Any]
    fs_,  # type: int
    ss_,  # type: int
    min_d,  # type: float
    max_d,  # type: float
    detector,  # type: Dict[str, Any]
):
    # type: (...) -> Tuple[float, float]
    # Re-implementation of check_point from libcrystfel/src/detector.c.
    xs_ = fs_ * panel["fsx"] + ss_ * panel["ssx"]
    ys_ = fs_ * panel["fsy"] + ss_ * panel["ssy"]
    rx_ = (xs_ + panel["cnx"]) / panel["res"]
    ry_ = (ys_ + panel["cny"]) / panel["res"]
    dist = math.sqrt(rx_ * rx_ + ry_ * ry_)
    if dist > max_d:
        detector["furthest_out_panel"] = name
        detector["furthest_out_fs"] = fs_
        detector["furthest_out_ss"] = ss_
        max_d = dist
    elif dist < min_d:
        detector["furthest_in_panel"] = name
        detector["furthest_in_fs"] = fs_
        detector["furthest_in_ss"] = ss_
        min_d = dist

    return min_d, max_d


def _find_min_max_d(detector):
    # type: (Dict[str, Any]) -> None
    # Re-implementation of find_min_max_d from libcrystfel/src/detector.c.
    min_d = float("inf")
    max_d = 0.0
    for name, panel in detector["panels"].items():
        min_d, max_d = _check_point(
            name=name,
            panel=panel,
            fs_=0,
            ss_=0,
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )
        min_d, max_d = _check_point(
            name=name,
            panel=panel,
            fs_=panel["w"],
            ss_=0,
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )
        min_d, max_d = _check_point(
            name=name,
            panel=panel,
            fs_=0,
            ss_=panel["h"],
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )
        min_d, max_d = _check_point(
            name=name,
            panel=panel,
            fs_=panel["w"],
            ss_=panel["h"],
            min_d=min_d,
            max_d=max_d,
            detector=detector,
        )


def load_crystfel_geometry(filename):
    # type: (str) -> Dict[str, Any]
    """
    Loads a CrystFEL geometry file.

    This function is a Re-implementation of the get_detector_geometry_2 function from
    CrystFEL. It reads information from a CrystFEL geometry file.

    For a full documentation of the CrystFEL geometry format, see the relevant `man
    page <http://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html>`_.

    The function returns a dictionary with the geometry information.

    * The CrystFEL geometry file uses a key/value language. The keys in the returned
      dictionary match the keys in the geometry file.

    * The dictionary values store the corresponding values.

    * The code of this function is currently synchronized with the code of the function
      'get_detector_geometry_2' in CrystFEL at commit 41a8fa9819010.

    Arguments:

        filename (str): the absolute or relative path to a CrystFEL geometry file.

    Returns:

        Dict[str, Any]: a dictionary with the geometry information loaded from the
        file.
    """
    beam = {"photon_energy": 0.0, "photon_energy_from": None, "photon_energy_scale": 1}
    detector = {
        "panels": collections.OrderedDict(),
        "bad": collections.OrderedDict(),
        "mask_good": 0,
        "mask_bad": 0,
        "rigid_groups": {},
        "rigid_group_collections": {},
    }
    default_panel = {
        "cnx": None,
        "cny": None,
        "clen": None,
        "coffset": 0.0,
        "res": -1.0,
        "badrow": "-",
        "no_index": False,
        "fsx": 1.0,
        "fsy": 0.0,
        "fsz": 0.0,
        "ssx": 0.0,
        "ssy": 1.0,
        "ssz": 0.0,
        "rail_x": None,
        "rail_y": None,
        "rail_z": None,
        "clen_for_centering": None,
        "adu_per_eV": None,
        "adu_per_photon": None,
        "max_adu": float("inf"),
        "mask": None,
        "mask_file": None,
        "satmap": None,
        "satmap_file": None,
        "data": None,
        "dim_structure": None,
    }
    default_bad_region = {
        "min_x": None,
        "max_x": None,
        "min_y": None,
        "max_y": None,
        "min_fs": 0,
        "max_fs": 0,
        "min_ss": 0,
        "max_ss": 0,
        "is_fsss": 99,
    }
    default_dim = ["ss", "fs"]

    try:
        with open(filename, mode="r") as file_handle:
            file_lines = file_handle.readlines()
            for line in file_lines:
                if line.startswith(";"):
                    continue
                line_without_comments = line.strip().split(";")[0]
                line_items = re.split(pattern="([ \t])", string=line_without_comments)
                line_items = [
                    item for item in line_items if item not in ("", " ", "\t")
                ]
                if len(line_items) < 3:
                    continue
                value = "".join(line_items[2:])
                if line_items[1] != "=":
                    continue
                path = re.split("(/)", line_items[0])
                path = [item for item in path if item not in "/"]
                if len(path) < 2:
                    _parse_toplevel(
                        key=line_items[0],
                        value=value,
                        detector=detector,
                        beam=beam,
                        panel=default_panel,
                    )
                    continue
                curr_bad = None
                curr_panel = None
                if path[0].startswith("bad"):
                    if path[0] in detector["bad"]:
                        curr_bad = detector["bad"][path[0]]
                    else:
                        curr_bad = copy.deepcopy(default_bad_region)
                        detector["bad"][path[0]] = curr_bad
                else:
                    if path[0] in detector["panels"]:
                        curr_panel = detector["panels"][path[0]]
                    else:
                        curr_panel = copy.deepcopy(default_panel)
                        detector["panels"][path[0]] = curr_panel
                if curr_panel is not None:
                    _parse_field_for_panel(key=path[1], value=value, panel=curr_panel)
                else:
                    _parse_field_bad(key=path[1], value=value, bad=curr_bad)
            if not detector["panels"]:
                raise RuntimeError("No panel descriptions in geometry file.")
            num_placeholders_in_panels = None
            for panel in detector["panels"].values():
                if panel["dim_structure"] is not None:
                    curr_num_placeholders = panel["dim_structure"].count("%")
                else:
                    curr_num_placeholders = 0

                if num_placeholders_in_panels is None:
                    num_placeholders_in_panels = curr_num_placeholders
                else:
                    if curr_num_placeholders != num_placeholders_in_panels:
                        raise RuntimeError(
                            "All panels' data and mask entries must have the same "
                            "number of placeholders."
                        )
            num_placeholders_in_masks = None
            for panel in detector["panels"].values():
                if panel["mask"] is not None:
                    curr_num_placeholders = panel["mask"].count("%")
                else:
                    curr_num_placeholders = 0

                if num_placeholders_in_masks is None:
                    num_placeholders_in_masks = curr_num_placeholders
                else:
                    if curr_num_placeholders != num_placeholders_in_masks:
                        raise RuntimeError(
                            "All panels' data and mask entries must have the same "
                            "number of placeholders."
                        )
            if num_placeholders_in_masks > num_placeholders_in_panels:
                raise RuntimeError(
                    "Number of placeholders in mask cannot be larger the number than "
                    "for data."
                )
            dim_length = None
            for panel_name, panel in viewitems(detector["panels"]):
                if panel["dim_structure"] is None:
                    panel["dim_structure"] = copy.deepcopy(default_dim)

                found_ss = 0
                found_fs = 0
                found_placeholder = 0
                for dim_index, entry in enumerate(panel["dim_structure"]):
                    if entry is None:
                        raise RuntimeError(
                            "Dimension {} for panel {} is undefined.".format(
                                dim_index, panel_name
                            )
                        )
                    elif entry == "ss":
                        found_ss += 1
                    elif entry == "fs":
                        found_fs += 1
                    elif entry == "%":
                        found_placeholder += 1
                if found_ss != 1:
                    raise RuntimeError(
                        "Exactly one slow scan dim coordinate is needed (found {} for "
                        "panel {}).".format(found_ss, panel_name)
                    )
                if found_fs != 1:
                    raise RuntimeError(
                        "Exactly one fast scan dim coordinate is needed (found {} for "
                        "panel {}).".format(found_fs, panel_name)
                    )
                if found_placeholder > 1:
                    raise RuntimeError(
                        "Only one placeholder dim coordinate is allowed. Maximum one "
                        "placeholder dim coordinate is allowed "
                        "(found {} for panel {})".format(found_placeholder, panel_name)
                    )
                if dim_length is None:
                    dim_length = len(panel["dim_structure"])
                elif dim_length != len(panel["dim_structure"]):
                    raise RuntimeError(
                        "Number of dim coordinates must be the same for all panels."
                    )
                if dim_length == 1:
                    raise RuntimeError(
                        "Number of dim coordinates must be at least " "two."
                    )
            for panel_name, panel in viewitems(detector["panels"]):
                if panel["origin_min_fs"] < 0:
                    raise RuntimeError(
                        "Please specify the minimum fs coordinate for panel {}.".format(
                            panel_name
                        )
                    )
                if panel["origin_max_fs"] < 0:
                    raise RuntimeError(
                        "Please specify the maximum fs coordinate for panel {}.".format(
                            panel_name
                        )
                    )
                if panel["origin_min_ss"] < 0:
                    raise RuntimeError(
                        "Please specify the minimum ss coordinate for panel {}.".format(
                            panel_name
                        )
                    )
                if panel["origin_max_ss"] < 0:
                    raise RuntimeError(
                        "Please specify the maximum ss coordinate for panel {}.".format(
                            panel_name
                        )
                    )
                if panel["cnx"] is None:
                    raise RuntimeError(
                        "Please specify the corner X coordinate for panel {}.".format(
                            panel_name
                        )
                    )
                if panel["clen"] is None and panel["clen_from"] is None:
                    raise RuntimeError(
                        "Please specify the camera length for panel {}.".format(
                            panel_name
                        )
                    )
                if panel["res"] < 0:
                    raise RuntimeError(
                        "Please specify the resolution or panel {}.".format(panel_name)
                    )
                if panel["adu_per_eV"] is None and panel["adu_per_photon"] is None:
                    raise RuntimeError(
                        "Please specify either adu_per_eV or adu_per_photon for panel "
                        "{}.".format(panel_name)
                    )
                if panel["clen_for_centering"] is None and panel["rail_x"] is not None:
                    raise RuntimeError(
                        "You must specify clen_for_centering if you specify the rail "
                        "direction (panel {})".format(panel_name)
                    )
                if panel["rail_x"] is None:
                    panel["rail_x"] = 0.0
                    panel["rail_y"] = 0.0
                    panel["rail_z"] = 1.0
                if panel["clen_for_centering"] is None:
                    panel["clen_for_centering"] = 0.0
                panel["w"] = panel["origin_max_fs"] - panel["origin_min_fs"] + 1
                panel["h"] = panel["origin_max_ss"] - panel["origin_min_ss"] + 1
            for bad_region_name, bad_region in viewitems(detector["bad"]):
                if bad_region["is_fsss"] == 99:
                    raise RuntimeError(
                        "Please specify the coordinate ranges for bad "
                        "region {}.".format(bad_region_name)
                    )
            for group in detector["rigid_groups"]:
                for name in detector["rigid_groups"][group]:
                    if name not in detector["panels"]:
                        raise RuntimeError(
                            "Cannot add panel to rigid_group. Panel not "
                            "found: {}".format(name)
                        )
            for group_collection in detector["rigid_group_collections"]:
                for name in detector["rigid_group_collections"][group_collection]:
                    if name not in detector["rigid_groups"]:
                        raise RuntimeError(
                            "Cannot add rigid_group to collection. Rigid group not "
                            "found: {}".format(name)
                        )
            for panel in detector["panels"].values():
                d__ = panel["fsx"] * panel["ssy"] - panel["ssx"] * panel["fsy"]
                if d__ == 0.0:
                    raise RuntimeError("Panel {} transformation is singular.")
                panel["xfs"] = panel["ssy"] / d__
                panel["yfs"] = panel["ssx"] / d__
                panel["xss"] = panel["fsy"] / d__
                panel["yss"] = panel["fsx"] / d__
            _find_min_max_d(detector)
    except (IOError, OSError) as exc:
        exc_type, exc_value = sys.exc_info()[:2]
        raise_from(
            exc=RuntimeError(
                "The following error occurred while reading the {0} geometry"
                "file {1}: {2}".format(filename, exc_type.__name__, exc_value,)
            ),
            cause=exc,
        )

    return detector