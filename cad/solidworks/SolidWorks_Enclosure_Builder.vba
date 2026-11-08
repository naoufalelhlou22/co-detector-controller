' ******************************************************************************
' SolidWorks VBA API Macro: Smart Dual Gas Detector Enclosure Generator
' Architecture: Revision 2.0 (Stage 5 Architecture)
' Instructions:
'   1. Open SolidWorks.
'   2. Go to Tools -> Macro -> New... (or Edit...).
'   3. Paste this code into the module and press F5 (Run Sub AutoBuildEnclosureBase).
' ******************************************************************************

Option Explicit

Dim swApp As Object
Dim Part As Object
Dim boolstatus As Boolean
Dim longstatus As Long, longwarnings As Long

Sub AutoBuildEnclosureBase()
    Set swApp = Application.SldWorks
    
    ' 1. Create a new metric Part document (MMGS)
    Set Part = swApp.NewDocument("C:\ProgramData\SolidWorks\SolidWorks 2024\templates\Part.prtdot", 0, 0, 0)
    If Part Is Nothing Then
        Set Part = swApp.NewPart()
    End If
    
    ' Set units to Millimeters
    Part.SetUnits swUnits_Length_Millimeters, swUnits_DecimalPlaces_Two
    
    ' 2. Select Top Plane for base sketch
    boolstatus = Part.Extension.SelectByID2("Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
    Part.SketchManager.InsertSketch True
    Part.ClearSelection2 True
    
    ' Draw centered 92mm x 72mm base outline with 10mm corner fillets
    ' In SW API, coordinates are in meters (e.g. 92mm = 0.092m)
    Dim w As Double, h As Double, r As Double
    w = 0.092 / 2
    h = 0.072 / 2
    r = 0.010
    
    ' Draw straight segments
    Part.SketchManager.CreateLine -w + r, -h, 0, w - r, -h, 0
    Part.SketchManager.CreateLine w, -h + r, 0, w, h - r, 0
    Part.SketchManager.CreateLine w - r, h, 0, -w + r, h, 0
    Part.SketchManager.CreateLine -w, h - r, 0, -w, -h + r, 0
    
    ' Draw 4 corner arcs
    Part.SketchManager.CreateArc w - r, -h + r, 0, w, -h + r, 0, w - r, -h, 0, 1
    Part.SketchManager.CreateArc w - r, h - r, 0, w - r, h, 0, w, h - r, 0, 1
    Part.SketchManager.CreateArc -w + r, h - r, 0, -w, h - r, 0, -w + r, h, 0, 1
    Part.SketchManager.CreateArc -w + r, -h + r, 0, -w + r, -h, 0, -w, -h + r, 0, 1
    
    ' Extrude base block up 10.0mm with 1.0 deg draft
    Dim myFeature As Object
    Set myFeature = Part.FeatureManager.FeatureExtrusion3(True, False, False, 0, 0, 0.01, 0, False, False, False, False, 0.01745, 0.01745, False, False, False, False, True, True, True, 0, 0, False)
    Part.ClearSelection2 True
    
    ' 3. Shell outward to create uniform 2.2mm wall thickness
    boolstatus = Part.Extension.SelectByID2("", "FACE", 0, 0, 0.01, False, 1, Nothing, 0)
    Set myFeature = Part.FeatureManager.InsertFeatureShell(0.0022, False)
    Part.ClearSelection2 True
    
    ' 4. Create PCB Mounting Bosses at (+/-31.5mm, +/-21.5mm)
    boolstatus = Part.Extension.SelectByID2("", "FACE", 0, 0, 0.0022, False, 0, Nothing, 0)
    Part.SketchManager.InsertSketch True
    
    Dim bossCoords(3, 1) As Double
    bossCoords(0, 0) = -0.0315: bossCoords(0, 1) = -0.0215
    bossCoords(1, 0) = 0.0315:  bossCoords(1, 1) = -0.0215
    bossCoords(2, 0) = -0.0315: bossCoords(2, 1) = 0.0215
    bossCoords(3, 0) = 0.0315:  bossCoords(3, 1) = 0.0215
    
    Dim i As Integer
    For i = 0 To 3
        ' Outer boss dia 5.5mm (radius 0.00275m)
        Part.SketchManager.CreateCircleByRadius bossCoords(i, 0), bossCoords(i, 1), 0, 0.00275
        ' Inner insert pilot hole dia 3.6mm (radius 0.0018m)
        Part.SketchManager.CreateCircleByRadius bossCoords(i, 0), bossCoords(i, 1), 0, 0.0018
    Next i
    
    ' Extrude bosses up 4.5mm (standoff height)
    Set myFeature = Part.FeatureManager.FeatureExtrusion3(True, False, False, 0, 0, 0.0045, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False)
    Part.ClearSelection2 True
    
    ' 5. Terminal Block Cutouts on Left Wall (-X)
    boolstatus = Part.Extension.SelectByID2("Right Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
    Part.SketchManager.InsertSketch True
    
    ' Cutout J1 (Y = -13.0mm, Width = 12.0mm, Height = 9.0mm)
    Part.SketchManager.CreateCenterRectangle -0.013, 0.0065, 0, 0.006, 0.0045, 0
    ' Cutout J2 (Y = +13.0mm, Width = 12.0mm, Height = 9.0mm)
    Part.SketchManager.CreateCenterRectangle 0.013, 0.0065, 0, 0.006, 0.0045, 0
    
    Set myFeature = Part.FeatureManager.FeatureCut4(True, False, False, 1, 0, 0.05, 0.05, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, 0, 0, False, False)
    Part.ClearSelection2 True
    
    ' Fit to screen
    Part.ViewZoomtofit2
    MsgBox "Smart Dual Gas Detector Base Chassis successfully generated in SolidWorks!", vbInformation, "SolidWorks Automation"
End Sub
