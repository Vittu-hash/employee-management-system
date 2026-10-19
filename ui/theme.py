"""Authoritative visual language for the Employee Analytics application."""

PALETTE = {
    "smart_blue": "#0466C8", "sapphire": "#0353A4", "regal_navy": "#023E7D",
    "prussian_blue": "#002855", "prussian_blue_2": "#001845", "prussian_blue_3": "#001233",
    "twilight_indigo": "#33415C", "blue_slate": "#5C677D", "slate_grey": "#7D8597",
    "lavender_grey": "#979DAC", "white": "#FFFFFF", "error": "#B42318",
}

COLORS = {
    **PALETTE,
    "background": "#F4F6FA", "surface": PALETTE["white"], "surface_secondary": "#E9EEF5",
    "text_primary": PALETTE["prussian_blue_3"], "text_secondary": PALETTE["blue_slate"],
    "primary": PALETTE["smart_blue"], "primary_hover": PALETTE["sapphire"],
    "secondary": "#DCE6F3", "success": PALETTE["smart_blue"], "warning": PALETTE["blue_slate"],
    "danger": PALETTE["error"], "critical": PALETTE["error"], "line": "#D8E0EA", "grid": "#E2E8F0",
    "sidebar": PALETTE["prussian_blue_3"], "sidebar_hover": PALETTE["prussian_blue"],
    "sidebar_text": "#D7E2F1", "active_nav": PALETTE["regal_navy"], "active_accent": PALETTE["smart_blue"],
    "muted": PALETTE["slate_grey"], "soft_success": "#E6F0FC", "soft_warning": "#EEF1F5", "soft_danger": "#FDECEA",
    # Compatibility aliases preserve existing screens while moving them to the new system.
    "papaya_whip": "#F4F6FA", "deep_space_blue": PALETTE["prussian_blue"], "steel_blue": PALETTE["smart_blue"],
    "brick_red": PALETTE["error"], "molten_lava": PALETTE["error"], "ink": PALETTE["prussian_blue_3"],
    "soft_blue": "#E6F0FC", "dark_teal": PALETTE["regal_navy"], "dark_cyan": PALETTE["smart_blue"],
    "pearl_aqua": "#DCE6F3", "golden_orange": PALETTE["blue_slate"], "burnt_caramel": PALETTE["blue_slate"],
    "rusty_spice": PALETTE["error"], "oxidized_iron": PALETTE["error"], "brown_red": PALETTE["error"],
    "vanilla_custard": "#F4F6FA", "soft_red": "#FDECEA",
}

DISPLAY_FONT = "Plus Jakarta Sans"
UI_FONT = "Inter"
DATA_FONT = "JetBrains Mono"
FONT = UI_FONT
