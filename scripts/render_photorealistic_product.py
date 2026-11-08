"""
Photorealistic Industrial Design Render Engine - Smart Dual Gas Detector (Rev 3.0)
Generates high-resolution, publication-grade photorealistic product renders based on
the ground-truth mechanical CAD models and datum coordinates.
Output: cad/smart_dual_gas_detector_render.png
"""

import math
import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_photorealistic_render():
    # Render dimensions (High-Definition 2560 x 1440 at 2x supersampling for extreme fidelity)
    W, H = 2560, 1440
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # =========================================================================
    # 1. STUDIO LIGHTING ENVIRONMENT & ARCHITECTURAL WALL BACKGROUND
    # =========================================================================
    # Create soft neutral vignette backdrop (warm titanium / architectural matte)
    bg_arr = np.zeros((H, W, 3), dtype=np.float32)
    center_x, center_y = W * 0.48, H * 0.46
    y_coords, x_coords = np.ogrid[:H, :W]

    # Radial distance from primary spotlight
    dist_sq = ((x_coords - center_x) / (W * 0.75))**2 + ((y_coords - center_y) / (H * 0.65))**2
    vignette = np.clip(1.0 - dist_sq * 0.45, 0.0, 1.0)

    # Base wall color: subtle slate grey gradient (#1e2530 to #131922)
    c_top = np.array([32.0, 39.0, 50.0], dtype=np.float32)
    c_bot = np.array([16.0, 21.0, 28.0], dtype=np.float32)
    y_grad = np.linspace(0.0, 1.0, H)[:, None]

    bg_rgb = (c_top * (1.0 - y_grad) + c_bot * y_grad)[:, None, :] # shape (H, 1, 3)
    bg_rgb = bg_rgb * (0.65 + 0.35 * vignette[:, :, None])

    # Add subtle architectural surface micro-grain
    rng = np.random.RandomState(42)
    noise = rng.normal(0.0, 1.2, (H, W, 1)).astype(np.float32)
    bg_rgb = np.clip(bg_rgb + noise, 0.0, 255.0).astype(np.uint8)

    bg_img = Image.fromarray(bg_rgb, mode="RGB").convert("RGBA")
    img.paste(bg_img, (0, 0))

    # =========================================================================
    # 2. ENCLOSURE GEOMETRY & PROJECTION
    # =========================================================================
    # Scale: 1 mm = 12.0 pixels
    scale = 12.5
    # Enclosure center in pixel coordinates
    enc_cx = W * 0.48
    enc_cy = H * 0.48

    # Outer squircle: 86.0 mm x 66.0 mm, R = 8.0 mm
    enc_w = 86.0 * scale   # 1075 px
    enc_h = 66.0 * scale   # 825 px
    enc_r = 8.0 * scale    # 100 px
    enc_depth = 28.0 * scale * 0.45 # Projected isometric depth ~157 px

    # PCB (0,0) in enclosure coordinates:
    # Enclosure center corresponds to PCB (35.0, 25.0) mm.
    # Therefore, PCB (0,0) is at:
    # x_pcb_0 = enc_cx - 35.0 * scale
    # y_pcb_0 = enc_cy + 25.0 * scale (since CAD Y increases upwards, screen Y increases downwards!)
    p0_x = enc_cx - 35.0 * scale
    p0_y = enc_cy + 25.0 * scale

    def to_screen(x_mm, y_mm):
        # CAD X is positive right, CAD Y is positive up
        sx = p0_x + x_mm * scale
        sy = p0_y - y_mm * scale
        return sx, sy

    # =========================================================================
    # 3. CONTACT SHADOW (SOFT MULTI-STAGE AMBIENT OCCLUSION)
    # =========================================================================
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)

    # Wall drop shadow cast by housing (offset down-right by studio key light)
    for off, alpha, blur_rad in [(45, 75, 48), (25, 95, 28), (12, 130, 14)]:
        sx0 = enc_cx - enc_w / 2.0 + off * 0.6
        sy0 = enc_cy - enc_h / 2.0 + off
        sx1 = enc_cx + enc_w / 2.0 + off * 0.6
        sy1 = enc_cy + enc_h / 2.0 + off
        s_draw.rounded_rectangle([sx0, sy0, sx1, sy1], radius=enc_r, fill=(0, 0, 0, alpha))
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur_rad))

    img = Image.alpha_composite(img, shadow_layer)

    # =========================================================================
    # 4. LOWER CHASSIS BASE & PARTING LINE
    # =========================================================================
    # The base extends slightly behind the cover (revealing the 1.2mm stepped parting line)
    base_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(base_layer)

    bx0 = enc_cx - enc_w / 2.0 + 4
    by0 = enc_cy - enc_h / 2.0 + 8
    bx1 = enc_cx + enc_w / 2.0 + 8
    by1 = enc_cy + enc_h / 2.0 + 12
    # Darker base body (matte dark charcoal / lower housing)
    b_draw.rounded_rectangle([bx0, by0, bx1, by1], radius=enc_r, fill=(35, 42, 54, 255))
    # Bevel shadow line
    b_draw.rounded_rectangle([bx0, by0, bx1, by1], radius=enc_r, outline=(20, 24, 32, 255), width=3)
    img = Image.alpha_composite(img, base_layer)

    # =========================================================================
    # 5. FRONT COVER MAIN HOUSING BODY (PREMIUM PC/ABS CYCOLOY WHITE)
    # =========================================================================
    cover_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(cover_layer)

    fx0 = enc_cx - enc_w / 2.0
    fy0 = enc_cy - enc_h / 2.0
    fx1 = enc_cx + enc_w / 2.0
    fy1 = enc_cy + enc_h / 2.0

    # Draw housing solid with directional gradient simulation
    # Outer squircle
    c_draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=enc_r, fill=(244, 247, 250, 255))

    # Add directional lighting shading: Top-left is bright (255), bottom-right slightly darker (220)
    # Vectorized computation for blazing fast rendering
    x_grid, y_grid = np.meshgrid(np.arange(W), np.arange(H))
    prog_x = np.clip((x_grid - fx0) / max(1.0, fx1 - fx0), 0.0, 1.0)
    prog_y = np.clip((y_grid - fy0) / max(1.0, fy1 - fy0), 0.0, 1.0)
    
    val = np.clip(255.0 - 32.0 * (prog_x * 0.6 + prog_y * 0.8), 215.0, 255.0).astype(np.uint8)
    val_b = np.clip(val.astype(np.float32) + 2.0, 0.0, 255.0).astype(np.uint8)
    
    shade_arr = np.dstack([val, val, val_b, np.full((H, W), 255, dtype=np.uint8)])

    shade_img = Image.fromarray(shade_arr, mode="RGBA")
    # Mask to rounded rectangle
    mask = Image.new("L", (W, H), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=enc_r, fill=255)
    cover_layer.paste(shade_img, (0, 0), mask)

    # Top Edge Specular Highlight Chamfer (1.5mm fillet on perimeter)
    c_draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=enc_r, outline=(255, 255, 255, 220), width=3)
    c_draw.rounded_rectangle([fx0 + 4, fy0 + 4, fx1 - 4, fy1 - 4], radius=enc_r - 4, outline=(218, 224, 233, 140), width=2)
    # Subtle bottom edge contact shadow
    c_draw.line([fx0 + enc_r, fy1, fx1 - enc_r, fy1], fill=(160, 172, 188, 180), width=3)

    img = Image.alpha_composite(img, cover_layer)

    # =========================================================================
    # 6. FEATURE: 0.96-INCH I2C OLED DISPLAY (CAD: 48.50, 32.50)
    # =========================================================================
    oled_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(oled_layer)

    ox_c, oy_c = to_screen(48.50, 32.50)
    oled_w = 25.0 * scale   # 312 px
    oled_h = 14.0 * scale   # 175 px
    oled_r = 1.8 * scale    # 22 px

    ox0 = ox_c - oled_w / 2.0
    oy0 = oy_c - oled_h / 2.0
    ox1 = ox_c + oled_w / 2.0
    oy1 = oy_c + oled_h / 2.0

    # 1. Beveled Rebound Rim (Recessed into plastic face)
    o_draw.rounded_rectangle([ox0 - 3, oy0 - 3, ox1 + 3, oy1 + 3], radius=oled_r + 2, fill=(185, 195, 208, 255))
    o_draw.rounded_rectangle([ox0 - 1, oy0 - 1, ox1 + 1, oy1 + 1], radius=oled_r, fill=(15, 20, 28, 255))

    # 2. Smoked Acrylic Lens (True Black Glass)
    o_draw.rounded_rectangle([ox0, oy0, ox1, oy1], radius=oled_r, fill=(8, 12, 18, 255))

    # 3. Active 0.96" OLED 128x64 Matrix (Cyan & High-Contrast White)
    disp_w = 21.7 * scale   # 271 px
    disp_h = 10.8 * scale   # 135 px
    dx0 = ox_c - disp_w / 2.0
    dy0 = oy_c - disp_h / 2.0
    dx1 = ox_c + disp_w / 2.0
    dy1 = oy_c + disp_h / 2.0

    o_draw.rectangle([dx0, dy0, dx1, dy1], fill=(2, 6, 12, 255))

    # Simulated Font Telemetry Graphics
    # Header bar
    o_draw.line([dx0 + 8, dy0 + 26, dx1 - 8, dy0 + 26], fill=(56, 189, 248, 160), width=1)
    o_draw.text((dx0 + 12, dy0 + 8), "CO/LPG MONITOR", fill=(56, 189, 248, 255))
    o_draw.text((dx1 - 42, dy0 + 8), "99%", fill=(16, 185, 129, 255))

    # Telemetry Row 1: CO
    o_draw.text((dx0 + 14, dy0 + 36), "CO LEVEL", fill=(148, 163, 184, 255))
    o_draw.text((dx0 + 95, dy0 + 34), "0 PPM", fill=(255, 255, 255, 255))
    o_draw.rectangle([dx0 + 175, dy0 + 38, dx0 + 245, dy0 + 48], outline=(16, 185, 129, 200), width=1)
    o_draw.rectangle([dx0 + 177, dy0 + 40, dx0 + 195, dy0 + 46], fill=(16, 185, 129, 240))
    o_draw.text((dx0 + 182, dy0 + 51), "SAFE", fill=(16, 185, 129, 220))

    # Telemetry Row 2: LPG
    o_draw.text((dx0 + 14, dy0 + 68), "LPG GAS", fill=(148, 163, 184, 255))
    o_draw.text((dx0 + 95, dy0 + 66), "0 %LEL", fill=(255, 255, 255, 255))
    o_draw.rectangle([dx0 + 175, dy0 + 70, dx0 + 245, dy0 + 80], outline=(16, 185, 129, 200), width=1)
    o_draw.rectangle([dx0 + 177, dy0 + 72, dx0 + 195, dy0 + 78], fill=(16, 185, 129, 240))
    o_draw.text((dx0 + 180, dy0 + 83), "CLEAN", fill=(16, 185, 129, 220))

    # Footer Status
    o_draw.text((dx0 + 14, dy0 + 104), "WiFi: ONLINE", fill=(56, 189, 248, 240))
    o_draw.text((dx1 - 65, dy0 + 104), "24.2 C", fill=(148, 163, 184, 200))

    # Specular Glass Reflection Streak (Diagonal glossy highlight)
    refl_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(refl_layer)
    r_pts = [
        (ox0 + 15, oy0), (ox0 + 75, oy0),
        (ox0 + 35, oy1), (ox0 - 25, oy1)
    ]
    r_draw.polygon(r_pts, fill=(255, 255, 255, 38))
    r_pts2 = [
        (ox0 + 85, oy0), (ox0 + 115, oy0),
        (ox0 + 75, oy1), (ox0 + 45, oy1)
    ]
    r_draw.polygon(r_pts2, fill=(255, 255, 255, 22))
    refl_layer = refl_layer.filter(ImageFilter.GaussianBlur(2))

    oled_layer = Image.alpha_composite(oled_layer, refl_layer)
    img = Image.alpha_composite(img, oled_layer)

    # =========================================================================
    # 7. FEATURE: TACTILE BUTTONS SW1 (TEST) & SW2 (HUSH)
    # CAD: SW2 at (42.00, 12.00) | SW1 at (42.00, 6.00)
    # =========================================================================
    btn_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    btn_draw = ImageDraw.Draw(btn_layer)

    buttons = [
        ("SW2", 42.00, 12.00, "HUSH / NAV"),
        ("SW1", 42.00, 6.00,  "TEST / CHECK")
    ]
    btn_r = 2.75 * scale # dia 5.5mm -> radius ~34 px

    for bname, bx_mm, by_mm, blabel in buttons:
        bx, by = to_screen(bx_mm, by_mm)

        # Outer chamfer well
        btn_draw.ellipse([bx - btn_r - 4, by - btn_r - 4, bx + btn_r + 4, by + btn_r + 4], fill=(205, 214, 225, 255))
        btn_draw.ellipse([bx - btn_r - 1, by - btn_r - 1, bx + btn_r + 1, by + btn_r + 1], fill=(130, 142, 160, 255))

        # Plunger button cap (subtle blue-grey soft matte)
        btn_draw.ellipse([bx - btn_r, by - btn_r, bx + btn_r, by + btn_r], fill=(236, 241, 246, 255))
        # Top-left highlight
        btn_draw.arc([bx - btn_r + 2, by - btn_r + 2, bx + btn_r - 2, by + btn_r - 2], 180, 360, fill=(255, 255, 255, 220), width=2)
        # Bottom-right shadow
        btn_draw.arc([bx - btn_r + 2, by - btn_r + 2, bx + btn_r - 2, by + btn_r - 2], 0, 180, fill=(160, 172, 188, 180), width=2)

        # Center concave tactile dish
        dish_r = btn_r * 0.55
        btn_draw.ellipse([bx - dish_r, by - dish_r, bx + dish_r, by + dish_r], fill=(225, 232, 240, 255))

        # Precision laser-engraved micro-text
        btn_draw.text((bx - 18, by + btn_r + 6), blabel.split()[0], fill=(100, 116, 139, 230))

    img = Image.alpha_composite(img, btn_layer)

    # =========================================================================
    # 8. FEATURE: 4-CHANNEL OPTICAL STATUS LED LIGHT PIPES (CAD: Y = 4.00 mm)
    # =========================================================================
    led_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(led_layer)

    leds = [
        (26.80, "ALARM",  (239, 68, 68),   False), # Red (Off)
        (30.00, "NORMAL", (16, 185, 129),  True),  # Green (Radiant Active)
        (33.20, "WIFI",   (56, 189, 248),  True),  # Blue (Active Subtle)
        (36.40, "FAULT",  (245, 158, 11),  False)  # Yellow (Off)
    ]
    led_r = 1.0 * scale # dia 2.0mm -> radius ~12.5 px

    bloom_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bloom_draw = ImageDraw.Draw(bloom_layer)

    for lx_mm, label, color, is_lit in leds:
        lx, ly = to_screen(lx_mm, 4.00)

        # Lens aperture bezel
        l_draw.ellipse([lx - led_r - 2, ly - led_r - 2, lx + led_r + 2, ly + led_r + 2], fill=(185, 195, 206, 255))
        l_draw.ellipse([lx - led_r - 1, ly - led_r - 1, lx + led_r + 1, ly + led_r + 1], fill=(45, 55, 72, 255))

        if is_lit:
            # Illuminated translucent PMMA optical pipe
            l_draw.ellipse([lx - led_r, ly - led_r, lx + led_r, ly + led_r], fill=color + (255,))
            l_draw.ellipse([lx - led_r * 0.4, ly - led_r * 0.4, lx + led_r * 0.4, ly + led_r * 0.4], fill=(255, 255, 255, 240))

            # Volumetric glow bloom around active LED
            for rad_b, alpha_b in [(18, 90), (32, 50), (55, 25)]:
                bloom_draw.ellipse([lx - rad_b, ly - rad_b, lx + rad_b, ly + rad_b], fill=color + (alpha_b,))
        else:
            # Inactive jewel lens (dark core with subtle glass glint)
            dark_c = tuple(int(c * 0.28) for c in color)
            l_draw.ellipse([lx - led_r, ly - led_r, lx + led_r, ly + led_r], fill=dark_c + (255,))
            l_draw.arc([lx - led_r + 2, ly - led_r + 2, lx + led_r - 2, ly + led_r - 2], 200, 340, fill=(255, 255, 255, 160), width=1)

        # Screen-printed status label below LED
        l_draw.text((lx - 12, ly + led_r + 6), label, fill=(100, 116, 139, 210))

    bloom_layer = bloom_layer.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, bloom_layer)
    img = Image.alpha_composite(img, led_layer)

    # =========================================================================
    # 9. FEATURE: TDK PS1240 85dB ACOUSTIC ROSETTE HORN (CAD: 32.00, 12.00)
    # =========================================================================
    horn_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(horn_layer)

    hx_c, hy_c = to_screen(32.00, 12.00)
    rosette_pitch = 3.2 * scale # PCD radius ~40 px

    # 7 holes: center dia 2.5mm, 6 outer dia 2.0mm
    holes = [(hx_c, hy_c, 1.25 * scale)]
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = hx_c + rosette_pitch * math.cos(rad)
        hy = hy_c - rosette_pitch * math.sin(rad)
        holes.append((hx, hy, 1.0 * scale))

    for hx, hy, hr in holes:
        # Depth shading (beveled bore into resonant chamber)
        h_draw.ellipse([hx - hr - 1.5, hy - hr - 1.5, hx + hr + 1.5, hy + hr + 1.5], fill=(210, 218, 228, 255))
        h_draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(18, 24, 34, 255))
        # Internal cavity shadow
        h_draw.ellipse([hx - hr + 1, hy - hr + 1, hx + hr - 1, hy + hr - 1], fill=(5, 8, 12, 255))

    img = Image.alpha_composite(img, horn_layer)

    # =========================================================================
    # 10. FEATURE: WINSEN ME3-CO CONCENTRIC DIFFUSION LOUVERS (CAD: 56.50, 14.50)
    # =========================================================================
    co_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    co_draw = ImageDraw.Draw(co_layer)

    cx_c, cy_c = to_screen(56.50, 14.50)
    co_r = 10.25 * scale # dia 20.5mm -> radius ~128 px

    # Recessed circular diffusion well
    co_draw.ellipse([cx_c - co_r - 2, cy_c - co_r - 2, cx_c + co_r + 2, cy_c + co_r + 2], fill=(200, 210, 222, 255))
    co_draw.ellipse([cx_c - co_r, cy_c - co_r, cx_c + co_r, cy_c + co_r], fill=(228, 235, 242, 255))

    # Concentric breathing louvers (depth-etched circular rings)
    for ring_r_mm in [8.0, 5.5, 3.0]:
        rr = ring_r_mm * scale
        co_draw.ellipse([cx_c - rr, cy_c - rr, cx_c + rr, cy_c + rr], outline=(150, 164, 182, 255), width=3)
        co_draw.ellipse([cx_c - rr + 2, cy_c - rr + 2, cx_c + rr - 2, cy_c + rr - 2], outline=(40, 50, 65, 255), width=2)

    # 8 Radial acoustic / airflow stiffening vanes
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x_in = cx_c + (2.5 * scale) * math.cos(rad)
        y_in = cy_c - (2.5 * scale) * math.sin(rad)
        x_out = cx_c + (co_r - 4) * math.cos(rad)
        y_out = cy_c - (co_r - 4) * math.sin(rad)
        co_draw.line([(x_in, y_in), (x_out, y_out)], fill=(130, 145, 165, 255), width=2)

    # Center sintered hydrophobic gas membrane (porous PTFE white/grey disc)
    ptfe_r = 2.4 * scale
    co_draw.ellipse([cx_c - ptfe_r, cy_c - ptfe_r, cx_c + ptfe_r, cy_c + ptfe_r], fill=(240, 244, 248, 255))
    co_draw.ellipse([cx_c - ptfe_r, cy_c - ptfe_r, cx_c + ptfe_r, cy_c + ptfe_r], outline=(100, 116, 139, 200), width=1)

    co_draw.text((cx_c - 28, cy_c + co_r + 8), "CO SENSOR", fill=(100, 116, 139, 220))

    img = Image.alpha_composite(img, co_layer)

    # =========================================================================
    # 11. FEATURE: FIGARO TGS2610-C00 LPG THERMAL CONVECTION CHIMNEY (CAD: 59.00, 43.50)
    # =========================================================================
    lpg_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lpg_draw = ImageDraw.Draw(lpg_layer)

    lx_c, ly_c = to_screen(59.00, 43.50)
    lpg_r = 5.25 * scale # dia 10.5mm -> radius ~65 px

    # Chimney boss rim
    lpg_draw.ellipse([lx_c - lpg_r - 2, ly_c - lpg_r - 2, lx_c + lpg_r + 2, ly_c + lpg_r + 2], fill=(205, 214, 225, 255))
    lpg_draw.ellipse([lx_c - lpg_r, ly_c - lpg_r, lx_c + lpg_r, ly_c + lpg_r], fill=(232, 238, 245, 255))

    # Natural convection slots (venting chimney louvers for heated gas plume)
    for dy_mm in [-3.0, 0.0, 3.0]:
        sy = ly_c + dy_mm * scale
        slot_w = 4.2 * scale
        lpg_draw.rounded_rectangle([lx_c - slot_w, sy - 4, lx_c + slot_w, sy + 4], radius=4, fill=(18, 24, 34, 255))
        # Internal stainless-steel flame arrestor mesh glint
        lpg_draw.line([lx_c - slot_w + 4, sy, lx_c + slot_w - 4, sy], fill=(80, 95, 115, 220), width=1)

    lpg_draw.text((lx_c - 24, ly_c - lpg_r - 18), "LPG CHIMNEY", fill=(100, 116, 139, 220))

    img = Image.alpha_composite(img, lpg_layer)

    # =========================================================================
    # 12. SUBTLE BRAND LOGO & ENGINEERING ANNOTATIONS
    # =========================================================================
    ann_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a_draw = ImageDraw.Draw(ann_layer)

    # Sleek laser-etched product branding on front cover (upper-left)
    a_draw.text((fx0 + 36, fy0 + 32), "ANTIGRAVITY", fill=(120, 135, 155, 220))
    a_draw.text((fx0 + 36, fy0 + 50), "DUAL GAS CONTROLLER", fill=(155, 170, 190, 180))

    # EN 50291 & EN 50194 compliance mark
    a_draw.text((fx1 - 130, fy1 - 32), "EN 50291 / 50194", fill=(160, 175, 195, 160))

    img = Image.alpha_composite(img, ann_layer)

    # Save high-resolution PNG
    out_png = os.path.abspath("cad/smart_dual_gas_detector_render.png")
    img.save(out_png, "PNG", quality=100)
    print(f"[SUCCESS] Photorealistic CAD render created at: {out_png}")
    print(f"Dimensions: {W} x {H} px, File size: {os.path.getsize(out_png):,} bytes")
    return out_png

if __name__ == '__main__':
    create_photorealistic_render()
