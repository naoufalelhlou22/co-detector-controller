; ==============================================================================
; AutoCAD Mechanical AutoLISP Automation Routine: CO Detector Enclosure
; Architecture: Revision 2.0 (Stage 5)
; Instructions:
;   1. Open AutoCAD Mechanical.
;   2. Type (load "build_enclosure_drawing.lsp") in the command line (or drag-and-drop).
;   3. Type DRAW_ENCLOSURE and press Enter.
; ==============================================================================

(defun c:DRAW_ENCLOSURE ()
  (setvar "CMDECHO" 0)
  (setvar "OSMODE" 0)
  
  ;; 1. Setup Mechanical Standard Layers
  (command "-LAYER" "M" "AM_0" "C" "7" "" "LW" "0.50" "" "") ; Contours
  (command "-LAYER" "M" "AM_1" "C" "2" "" "L" "HIDDEN2" "" "LW" "0.25" "" "") ; Hidden
  (command "-LAYER" "M" "AM_2" "C" "1" "" "L" "CENTER2" "" "LW" "0.25" "" "") ; Centerlines
  (command "-LAYER" "M" "AM_3" "C" "3" "" "LW" "0.25" "" "") ; Dimensions
  (command "-LAYER" "M" "AM_4" "C" "4" "" "LW" "0.25" "" "") ; Hatch
  (command "-LAYER" "M" "AM_5" "C" "6" "" "LW" "0.35" "" "") ; Text
  (command "-LAYER" "M" "AM_BORDER" "C" "5" "" "LW" "0.70" "" "") ; Border
  
  ;; 2. Draw A3 Border & Frame
  (setvar "CLAYER" "AM_BORDER")
  (command "RECTANG" "0,0" "420,297")
  (command "RECTANG" "20,10" "410,287")
  
  ;; Title Block
  (command "RECTANG" "230,10" "410,65")
  (command "LINE" "230,40" "410,40" "")
  (command "LINE" "230,25" "410,25" "")
  (command "LINE" "320,10" "320,40" "")
  
  (setvar "CLAYER" "AM_5")
  (command "TEXT" "234,55" "3.5" "0" "PROJECT: SMART DUAL GAS DETECTOR (CO + LPG)")
  (command "TEXT" "234,45" "2.8" "0" "DRAWING: MECHANICAL ENCLOSURE BLUEPRINT")
  (command "TEXT" "234,30" "2.5" "0" "MATERIAL: PC/ABS FLAME RETARDANT (UL 94-V0)")
  (command "TEXT" "234,16" "2.5" "0" "WALL THICKNESS: 2.20 mm +/- 0.15 mm")
  (command "TEXT" "324,30" "2.5" "0" "REV: 2.0 (STAGE 5)")
  (command "TEXT" "324,16" "2.5" "0" "SCALE: 1:1 (mm)")
  
  ;; 3. View 1: Front Cover Plan View
  (setvar "CLAYER" "AM_0")
  (command "RECTANG" "F" "10" "79,149" "171,221")
  
  (setvar "CLAYER" "AM_2")
  (command "LINE" "73,185" "177,185" "")
  (command "LINE" "125,143" "125,227" "")
  
  ;; Rosette Acoustic Horn (at LS1: 122, 198)
  (setvar "CLAYER" "AM_0")
  (command "CIRCLE" "122,198" "1.6") ; Center hole
  (command "CIRCLE" "125.6,198" "1.1")
  (command "CIRCLE" "123.8,201.1" "1.1")
  (command "CIRCLE" "120.2,201.1" "1.1")
  (command "CIRCLE" "118.4,198" "1.1")
  (command "CIRCLE" "120.2,194.9" "1.1")
  (command "CIRCLE" "123.8,194.9" "1.1")
  
  ;; Button Cutout (at 132, 201)
  (command "RECTANG" "F" "2.5" "123,195" "141,207")
  
  ;; 4. Zoom Extents
  (command "ZOOM" "E")
  (setvar "CMDECHO" 1)
  (princ "
AutoCAD Mechanical: Dual Gas Detector Enclosure successfully generated!")
  (princ)
)
