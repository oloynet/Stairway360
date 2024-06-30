import adsk.core, adsk.fusion
import math

# ------------------------------------------------------------------------------

def moveOccurence( occurrence: adsk.fusion.Occurrence, x: float = 0, y: float = 0, z: float = 0 )-> bool:

        if occurrence.objectType != adsk.fusion.Occurrence.classType():
            return False

        occurrenceTransform: adsk.core.Matrix3D = occurrence.transform
        occurrenceTransform.translation = adsk.core.Vector3D.create( x, y, z )
        occurrence.transform = occurrenceTransform

        return True


def middlePoint(
        sketch:     adsk.fusion.Sketch,
        startPoint: adsk.core.Point3D | adsk.fusion.SketchPoint,
        endPoint:   adsk.core.Point3D | adsk.fusion.SketchPoint,
        offsetDist: float = 0.0
    ) -> adsk.core.Point3D:

    #futil.log( f' > : middlePoint( {offsetDist} )')

    startPoint3D: adsk.core.Point3D = startPoint.geometry  if( startPoint.classType() == adsk.fusion.SketchPoint.classType() )  else startPoint
    endPoint3D:   adsk.core.Point3D = endPoint.geometry    if( endPoint.classType()   == adsk.fusion.SketchPoint.classType() )  else endPoint

    line3D = adsk.core.Line3D.create( startPoint3D, endPoint3D )
    ( _, startP, endP )  = line3D.evaluator.getParameterExtents()
    ( _, middlePoint3D ) = line3D.evaluator.getPointAtParameter( ( endP - startP ) / 2 )


    if offsetDist == 0:
        return middlePoint3D

    # ------------------------------------------------------------------------------

    segmentLine3D = adsk.core.Line3D.create( middlePoint3D, endPoint3D )

    # ------------------------------------------------------------------------------
    # rotate PI/2

    zAxis = adsk.core.Vector3D.create( z = 1 )
    matrixRotation = adsk.core.Matrix3D.create()
    matrixRotation.setToRotation( math.pi / 2 , zAxis, middlePoint3D )
    segmentLine3D.transformBy( matrixRotation )

    # ------------------------------------------------------------------------------

    newPoint3D   = segmentLine3D.startPoint.copy()
    vector3D     = newPoint3D.vectorTo( segmentLine3D.endPoint )

    if vector3D.length == 0:
        return middlePoint3D

    # ------------------------------------------------------------------------------
    # translate

    vector3D.scaleBy( offsetDist / vector3D.length )
    newPoint3D.translateBy( vector3D )

    return newPoint3D


def offsetPoint(
        point3D: adsk.core.Point3D | adsk.fusion.SketchPoint,
        x:       float = 0.0,
        y:       float = 0.0,
        z:       float = 0.0
    ) -> adsk.core.Point3D:

    if point3D.classType() == adsk.fusion.SketchPoint.classType():
        point3D = point3D.geometry

    point3D.translateBy( adsk.core.Vector3D.create( x, y, z ) )

    return point3D


# ------------------------------------------------------------------------------

def getBigNurbsCurve (
        curves: list
    ) -> adsk.core.NurbsCurve3D:
    "Get a big NURBS curve from selected curves by Brian Etkins. See : https://forums.autodesk.com/t5/fusion-api-and-scripts/convert-multiple-lines-into-a-single-spline/m-p/10489789#M13828"

    nurbsCurves = []

    for curveSKT in curves:

        # Get each curve as a NURBS curve.
        nurbs:       adsk.core.NurbsCurve3D  = None
        sketchCurve: adsk.fusion.SketchCurve = curveSKT

        if sketchCurve.geometry.objectType == adsk.core.NurbsCurve3D.classType():
            # nurbs = sketchCurve.geometry
            nurbs = sketchCurve.worldGeometry
        else:
            # nurbs = sketchCurve.geometry.asNurbsCurve
            nurbs = sketchCurve.worldGeometry.asNurbsCurve


        # Determine if the end of the start curve matches either the start
        # or end of the second curve. If not, reverse the start curve.

        if len( nurbsCurves ) == 1:

            firstCurve: adsk.core.NurbsCurve3D = nurbsCurves[ 0 ]
            newCurve:   adsk.core.NurbsCurve3D = nurbs

            firstStart: adsk.core.Point3D = firstCurve.controlPoints[ 0 ]
            firstEnd:   adsk.core.Point3D = firstCurve.controlPoints[ -1 ]

            newStart:   adsk.core.Point3D = newCurve.controlPoints[ 0 ]
            newEnd:     adsk.core.Point3D = newCurve.controlPoints[ -1]

            if firstStart.isEqualTo( newStart ) or firstStart.isEqualTo( newEnd ):
                curves[ 0 ] = reverseNurbsCurve( curves[ 0 ] )

        # For each subsequent curve, check to see that it's start matches the end of the previous curve.
        # If it doesn't reverse the new curve.

        if len( nurbsCurves ) > 0:
            previousCurve: adsk.core.NurbsCurve3D = nurbsCurves[ -1 ]
            newCurve:      adsk.core.NurbsCurve3D = nurbs

            existingEnd:   adsk.core.Point3D = previousCurve.controlPoints[ -1 ]
            newStart:      adsk.core.Point3D = newCurve.controlPoints[ 0 ]

            if not existingEnd.isEqualTo( newStart ):
                nurbs = reverseNurbsCurve( nurbs )

        # Add the curve to the list.
        nurbsCurves.append( nurbs )


    # Merge the curves together to create a single NURBS curve.

    bigCurve: adsk.core.NurbsCurve3D = None

    for nurb in nurbsCurves:
        if bigCurve is None:
            bigCurve = nurb
        else:
            bigCurve = bigCurve.merge( nurb )


    return bigCurve


def reverseNurbsCurve(
        curve: adsk.core.NurbsCurve3D
    ) -> adsk.core.NurbsCurve3D:
    "Reverses and returns the input NURBS curve by Brian Etkins"

    ( _, points, degree, knots, isRational, weights, isPeriodic ) = curve.getData()
    # Reverse the points and weights.
    points  = points[::-1]
    weights = weights[::-1]

    # Create and return a new curve created with the reversed data.
    if isRational:
        return adsk.core.NurbsCurve3D.createRational( points, degree, knots, weights, isPeriodic )
    else:
        return adsk.core.NurbsCurve3D.createNonRational( points, degree, knots, isPeriodic )

    # ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------

def sign( value ) -> int:
    #return ( value > 0 ) - ( value < 0 )
    
    return math.copysign( 1, value )
