import sys
from examples.auth import authorization
from socrata import Socrata

socrata = Socrata(authorization)

file_path = sys.argv[1]

"""
This shows reprojecting from British National Grid
to WGS84

We're using the proj4 def from here:
http://spatialreference.org/ref/epsg/27700/
"""

with open(file_path, 'rb') as file:
    (revision, output_schema) = socrata.create(
        name = "parking structures",
        description = "cool"
    ).csv(file)


    (ok, output_schema) = output_schema\
        .add_column(
            'point_wgs84',
            'Location',
            """
            reproject_to_wgs84(
                set_projection(
                    make_point(
                        to_number(`northing`),
                        to_number(`easting`)
                    ),
                    "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +datum=OSGB36 +units=m +no_defs"
                )

            )
            """,
            'the easting/northing as wgs84 point'
        )\
        .run()

    revision.apply(output_schema = output_schema)
    revision.open_in_browser()

