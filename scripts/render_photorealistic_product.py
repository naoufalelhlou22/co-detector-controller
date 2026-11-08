"""
Photorealistic Industrial Design Render Engine - Smart LPG Gas Detector (Rev 4.0)
Generates high-resolution, publication-grade photorealistic product renders based on
the ground-truth mechanical CAD models and datum coordinates.
Rev 4.0: Figaro TGS2610-C00 LPG Detector with 1100mAh LiPo Battery Backup & Smart Power-Path.
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
    bg_arr = np.zeros((H, W, 3), dtype=np.float32)
    center_x, center_y = W * 0.48, H * 0.46
    y_coords, x_coords = np.ogrid[:H, :W]

    dist_sq = ((x_coords - center_x) / (W * 0.75)) ** 2 + ((y_coords - center_y) / (H * 0.65)) ** 2
    vignette = np.clip(1.0 - dist_sq * 0.45, 0.0, 1.0)

    # Base wall color: subtle slate grey gradient (#1e2530 to #131922)
    c_top = np.array([32.0, 39.0, 50.0], dtype=np.float32)
    c_bot = np.array([16.0, 21.0, 28.0], dtype=np.float32)
    y_grad = np.linspace(0.0, 1.0, H)[:, None]

    bg_rgb = (c_top * (1.0 - y_grad) + c_bot * y_grad)[:, None, :] # shape (H, 1, 3)
    bg_rgb = bg_rgb * (0.65 + 0.35 * vignette[:, :, None])

    # Micro-grain texture
    rng = np.random.RandomState(42)
    noise = rng.normal(0.0, 1.2, (H, W, 1)).astype(np.float32)
    bg_rgb = np.clip(bg_rgb + noise, 0.0, 255.0).astype(np.uint8)

    bg_img = Image.fromarray(bg_rgb, mode="RGB").convert("RGBA")
    img.paste(bg_img, (0, 0))

    # =========================================================================
    # 2. ENCLOSURE GEOMETRY & PROJECTION
    # =========================================================================
    scale = 12.5
    enc_cx = W * 0.48
    enc_cy = H * 0.48

    enc_w = 86.0 * scale   # 1075 px
    enc_h = 66.0 * scale   # 825 px
    enc_r = 8.0 * scale    # 100 px

    p0_x = enc_cx - 35.0 * scale
    p0_y = enc_cy + 25.0 * scale

    def to_screen(x_mm, y_mm):
        sx = p0_x + x_mm * scale
        sy = p0_y - y_mm * scale
        return sx, sy

    # =========================================================================
    # 3. CONTACT SHADOW (SOFT MULTI-STAGE AMBIENT OCCLUSION)
    # =========================================================================
    shadow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)

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
    base_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(base_layer)
    bx0 = enc_cx - enc_w / 2.0 + 4
    by0 = enc_cy - enc_h / 2.0 + 8
    bx1 = enc_cx + enc_w / 2.0 + 8
    by1 = enc_cy + enc_h / 2.0 + 12
    b_draw.rounded_rectangle([bx0, by0, bx1, by1], radius=enc_r, fill=(35, 42, 54, 255))
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

    c_draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=enc_r, fill=(244, 247, 250, 255))

    # Directional lighting gradient
    x_grid, y_grid = np.meshgrid(np.arange(W), np.arange(H))
    prog_x = np.clip((x_grid - fx0) / max(1.0, fx1 - fx0), 0.0, 1.0)
    prog_y = np.clip((y_grid - fy0) / max(1.0, fy1 - fy0), 0.0, 1.0)
    val = np.clip(255.0 - 32.0 * (prog_x * 0.6 + prog_y * 0.8), 215.0, 255.0).astype(np.uint8)
    val_b = np.clip(val.astype(np.float32) + 2.0, 0.0, 255.0).astype(np.uint8)
    shade_arr = np.dstack([val, val, val_b, np.full((H, W), 255, dtype=np.uint8)])
    shade_img = Image.fromarray(shade_arr, mode="RGBA")

    mask = Image.new("L", (W, H), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=enc_r, fill=255)
    cover_layer.paste(shade_img, (0, 0), mask)

    # Top Edge Specular Chamfer
    c_draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=enc_r, outline=(255, 255, 255, 220), width=3)
    c_draw.rounded_rectangle([fx0 + 4, fy0 + 4, fx1 - 4, fy1 - 4], radius=enc_r - 4, outline=(218, 224, 233, 140), width=2)
    c_draw.line([fx0 + enc_r, fy1, fx1 - enc_r, fy1], fill=(160, 172, 188, 180), width=3)

    img = Image.alpha_composite(img, cover_layer)

    # =========================================================================
    # 6. FEATURE: 0.96-INCH I2C OLED DISPLAY AT CAD (42.00, 25.00)
    # =========================================================================
    oled_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(oled_layer)

    ox_c, oy_c = to_screen(42.00, 25.00)
    oled_w = 25.0 * scale   # 312 px
    oled_h = 14.0 * scale   # 175 px
    oled_r = 1.8 * scale    # 22 px

    ox0 = ox_c - oled_w / 2.0
    oy0 = oy_c - oled_h / 2.0
    ox1 = ox_c + oled_w / 2.0
    oy1 = oy_c + oled_h / 2.0

    # Beveled rim
    o_draw.rounded_rectangle([ox0 - 3, oy0 - 3, ox1 + 3, oy1 + 3], radius=oled_r + 2, fill=(185, 195, 208, 255))
    o_draw.rounded_rectangle([ox0 - 1, oy0 - 1, ox1 + 1, oy1 + 1], radius=oled_r, fill=(15, 20, 28, 255))

    # Smoked Acrylic Display Window
    o_draw.rounded_rectangle([ox0, oy0, ox1, oy1], radius=oled_r, fill=(8, 12, 18, 255))

    # Active 128x64 Matrix
    disp_w = 21.7 * scale
    disp_h = 10.8 * scale
    dx0 = ox_c - disp_w / 2.0
    dy0 = oy_c - disp_h / 2.0
    dx1 = ox_c + disp_w / 2.0
    dy1 = oy_c + disp_h / 2.0
    o_draw.rectangle([dx0, dy0, dx1, dy1], fill=(2, 6, 12, 255))

    # OLED Telemetry Graphics (Rev 4.0: LPG + Battery Telemetry)
    o_draw.line([dx0 + 8, dy0 + 26, dx1 - 8, dy0 + 26], fill=(56, 189, 248, 160), width=1)
    o_draw.text((dx0 + 12, dy0 + 8), "SMART LPG DETECTOR", fill=(56, 189, 248, 255))
    o_draw.text((dx1 - 55, dy0 + 8), "BAT 100%", fill=(16, 185, 129, 255))

    # Row 1: Gas concentration
    o_draw.text((dx0 + 14, dy0 + 36), "LPG GAS", fill=(148, 163, 184, 255))
    o_draw.text((dx0 + 95, dy0 + 34), "0 %LEL", fill=(255, 255, 255, 255))
    o_draw.rectangle([dx0 + 175, dy0 + 38, dx0 + 245, dy0 + 48], outline=(16, 185, 129, 200), width=1)
    o_draw.rectangle([dx0 + 177, dy0 + 40, dx0 + 195, dy0 + 46], fill=(16, 185, 129, 240))
    o_draw.text((dx0 + 180, dy0 + 51), "CLEAN", fill=(16, 185, 129, 220))

    # Row 2: Battery & Power Status
    o_draw.text((dx0 + 14, dy0 + 68), "POWER", fill=(148, 163, 184, 255))
    o_draw.text((dx0 + 95, dy0 + 66), "12V MAINS", fill=(56, 189, 248, 255))
    o_draw.text((dx0 + 178, dy0 + 68), "[CHG OFF]", fill=(148, 163, 184, 220))

    # Footer
    o_draw.text((dx0 + 14, dy0 + 104), "WiFi: ONLINE", fill=(56, 189, 248, 240))
    o_draw.text((dx1 - 70, dy0 + 104), "VBAT 4.2V", fill=(16, 185, 129, 220))

    # Specular Glass Streak
    refl_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r_draw = ImageDraw.Draw(refl_layer)
    r_pts = [(ox0 + 15, oy0), (ox0 + 75, oy0), (ox0 + 35, oy1), (ox0 - 25, oy1)]
    r_draw.polygon(r_pts, fill=(255, 255, 255, 38))
    r_pts2 = [(ox0 + 85, oy0), (ox0 + 115, oy0), (ox0 + 75, oy1), (ox0 + 45, oy1)]
    r_draw.polygon(r_pts2, fill=(255, 255, 255, 22))
    refl_layer = refl_layer.filter(ImageFilter.GaussianBlur(2))

    oled_layer = Image.alpha_composite(oled_layer, refl_layer)
    img = Image.alpha_composite(img, oled_layer)

    # =========================================================================
    # 7. FEATURE: TACTILE BUTTONS SW2 (HUSH at 35.0, 13.0) & SW1 (TEST at 45.0, 13.0)
    # =========================================================================
    btn_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    btn_draw = ImageDraw.Draw(btn_layer)
    buttons = [
        ("SW2", 35.00, 13.00, "HUSH / SILENCE"),
        ("SW1", 45.00, 13.00, "TEST / CAL")
    ]
    btn_r = 2.75 * scale

    for bname, bx_mm, by_mm, blabel in buttons:
        bx, by = to_screen(bx_mm, by_mm)
        btn_draw.ellipse([bx - btn_r - 4, by - btn_r - 4, bx + btn_r + 4, by + btn_r + 4], fill=(205, 214, 225, 255))
        btn_draw.ellipse([bx - btn_r - 1, by - btn_r - 1, bx + btn_r + 1, by + btn_r + 1], fill=(130, 142, 160, 255))
        btn_draw.ellipse([bx - btn_r, by - btn_r, bx + btn_r, by + btn_r], fill=(236, 241, 246, 255))
        btn_draw.arc([bx - btn_r + 2, by - btn_r + 2, bx + btn_r - 2, by + btn_r - 2], 180, 360, fill=(255, 255, 255, 220), width=2)
        btn_draw.arc([bx - btn_r + 2, by - btn_r + 2, bx + btn_r - 2, by + btn_r - 2], 0, 180, fill=(160, 172, 188, 180), width=2)

        dish_r = btn_r * 0.55
        btn_draw.ellipse([bx - dish_r, by - dish_r, bx + dish_r, by + dish_r], fill=(225, 232, 240, 255))
        btn_draw.text((bx - 16, by + btn_r + 6), blabel.split()[0], fill=(100, 116, 139, 230))

    img = Image.alpha_composite(img, btn_layer)

    # =========================================================================
    # 8. FEATURE: 4 STATUS LEDS (CAD Y = 4.00 mm: X = 28, 34, 40, 46 mm)
    # =========================================================================
    led_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(led_layer)
    leds = [
        (28.00, "PWR",  (16, 185, 129),  True),  # Green (Mains active)
        (34.00, "LPG",  (16, 185, 129),  True),  # Green (Sensor healthy)
        (40.00, "ALM",  (239, 68, 68),   False), # Red (Alarm inactive)
        (46.00, "WIFI", (56, 189, 248),  True)   # Blue (Cloud connected)
    ]
    led_r = 1.1 * scale
    bloom_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bloom_draw = ImageDraw.Draw(bloom_layer)

    for lx_mm, label, color, is_lit in leds:
        lx, ly = to_screen(lx_mm, 4.00)
        l_draw.ellipse([lx - led_r - 2, ly - led_r - 2, lx + led_r + 2, ly + led_r + 2], fill=(185, 195, 206, 255))
        l_draw.ellipse([lx - led_r - 1, ly - led_r - 1, lx + led_r + 1, ly + led_r + 1], fill=(45, 55, 72, 255))

        if is_lit:
            l_draw.ellipse([lx - led_r, ly - led_r, lx + led_r, ly + led_r], fill=color + (255,))
            l_draw.ellipse([lx - led_r * 0.4, ly - led_r * 0.4, lx + led_r * 0.4, ly + led_r * 0.4], fill=(255, 255, 255, 240))
            for rad_b, alpha_b in [(18, 90), (32, 50), (55, 25)]:
                bloom_draw.ellipse([lx - rad_b, ly - rad_b, lx + rad_b, ly + rad_b], fill=color + (alpha_b,))
        else:
            dark_c = tuple(int(c * 0.28) for c in color)
            l_draw.ellipse([lx - led_r, ly - led_r, lx + led_r, ly + led_r], fill=dark_c + (255,))
            l_draw.arc([lx - led_r + 2, ly - led_r + 2, lx + led_r - 2, ly + led_r - 2], 200, 340, fill=(255, 255, 255, 160), width=1)

        l_draw.text((lx - 12, ly + led_r + 6), label, fill=(100, 116, 139, 210))

    bloom_layer = bloom_layer.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, bloom_layer)
    img = Image.alpha_composite(img, led_layer)

    # =========================================================================
    # 9. FEATURE: TDK PS1240 85dB ACOUSTIC ROSETTE HORN AT CAD (60.00, 16.00)
    # =========================================================================
    horn_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(horn_layer)
    hx_c, hy_c = to_screen(60.00, 16.00)
    rosette_pitch = 3.2 * scale

    holes = [(hx_c, hy_c, 1.25 * scale)]
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = hx_c + rosette_pitch * math.cos(rad)
        hy = hy_c - rosette_pitch * math.sin(rad)
        holes.append((hx, hy, 0.90 * scale))

    for hx, hy, hr in holes:
        h_draw.ellipse([hx - hr - 1.5, hy - hr - 1.5, hx + hr + 1.5, hy + hr + 1.5], fill=(210, 218, 228, 255))
        h_draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(18, 24, 34, 255))
        h_draw.ellipse([hx - hr + 1, hy - hr + 1, hx + hr - 1, hy + hr - 1], fill=(5, 8, 12, 255))

    h_draw.text((hx_c - 20, hy_c + rosette_pitch + 16), "85dB ALARM", fill=(100, 116, 139, 220))
    img = Image.alpha_composite(img, horn_layer)

    # =========================================================================
    # 10. FEATURE: FIGARO TGS2610-C00 LPG THERMAL CHIMNEY AT CAD (60.00, 37.00)
    # =========================================================================
    lpg_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lpg_draw = ImageDraw.Draw(lpg_layer)
    lx_c, ly_c = to_screen(60.00, 37.00)
    lpg_r = 5.5 * scale

    lpg_draw.ellipse([lx_c - lpg_r - 2, ly_c - lpg_r - 2, lx_c + lpg_r + 2, ly_c + lpg_r + 2], fill=(205, 214, 225, 255))
    lpg_draw.ellipse([lx_c - lpg_r, ly_c - lpg_r, lx_c + lpg_r, ly_c + lpg_r], fill=(232, 238, 245, 255))

    for dy_mm in [-3.0, -1.0, 1.0, 3.0]:
        sy = ly_c + dy_mm * scale
        slot_w = 4.2 * scale
        lpg_draw.rounded_rectangle([lx_c - slot_w, sy - 3, lx_c + slot_w, sy + 3], radius=3, fill=(18, 24, 34, 255))
        lpg_draw.line([lx_c - slot_w + 4, sy, lx_c + slot_w - 4, sy], fill=(80, 95, 115, 220), width=1)

    lpg_draw.text((lx_c - 28, ly_c - lpg_r - 18), "LPG CHIMNEY", fill=(100, 116, 139, 220))
    img = Image.alpha_composite(img, lpg_layer)

    # =========================================================================
    # 11. BRAND LOGO & COMPLIANCE ANNOTATIONS
    # =========================================================================
    ann_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a_draw = ImageDraw.Draw(ann_layer)

    a_draw.text((fx0 + 36, fy0 + 32), "ANTIGRAVITY", fill=(120, 135, 155, 220))
    a_draw.text((fx0 + 36, fy0 + 50), "LPG DETECTOR & BATTERY BACKUP", fill=(155, 170, 190, 180))
    a_draw.text((fx1 - 145, fy1 - 32), "EN 50194-1 / UL 2075", fill=(160, 175, 195, 160))

    img = Image.alpha_composite(img, ann_layer)

    # Save hero product render
    out_png = os.path.abspath("cad/smart_dual_gas_detector_render.png")
    img.save(out_png, "PNG", quality=100)
    print(f"[SUCCESS] Photorealistic CAD render created at: {out_png}")
    print(f"Dimensions: {W} x {H} px, File size: {os.path.getsize(out_png):,} bytes")
    return out_png


if __name__ == '__main__':
    create_photorealistic_render()
