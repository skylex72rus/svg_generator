# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SvgBubbl
                                 A QGIS plugin
 create svg images from vector layer
                             -------------------
        begin                : 2017-06-18
        copyright            : (C) 2017 by Alex Russkikh. 
        email                : skylex72rus@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SvgBubbl class from file SvgBubbl.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .svg_generator import SvgBubbl
    return SvgBubbl(iface)
