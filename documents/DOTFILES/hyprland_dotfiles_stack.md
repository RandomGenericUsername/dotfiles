# Hyprland Dotfiles – Cross-Distro Stack Reference

This document serves as a **comprehensive, distro-agnostic reference** for building a Hyprland dotfiles setup. It lists all the essential tools, grouped by functionality, followed by distro-specific package names and alternative tools.

---

## 🧱 Core Components

| Function | Recommended Tool | Description |
|-----------|------------------|-------------|
| **Compositor** | Hyprland | Wayland compositor and window manager. |
| **Display Server** | Wayland | Required backend protocol. |
| **Legacy App Support** | Xwayland | Enables X11 applications under Wayland. |
| **Status Bar** | Waybar | Customizable bar with CSS styling and modules. |
| **Desktop Portals** | xdg-desktop-portal, xdg-desktop-portal-hyprland | Required for screenshots, file dialogs, and screen sharing. |
| **Audio/Video** | PipeWire + WirePlumber | Modern replacement for PulseAudio + JACK. |
| **Policy Agent** | hyprpolkitagent *(preferred)* | Handles authentication prompts natively in Hyprland. **polkit-gnome** or **lxqt-policykit** may be used if hyprpolkitagent is unavailable. Only one should run at a time. |

---

## 🧰 Daily Utilities

| Category | Tool | Purpose |
|-----------|------|----------|
| **Launcher** | Rofi | Modern, scriptable app launcher. Wayland-compatible. |
| **Notifications** | swaync / dunst | Notification daemon with tray integration. swaync provides notification center features; dunst is lighter. |
| **Clipboard** | wl-clipboard + cliphist / copyq / clipman | Clipboard manager supporting text, images, and multiple selection modes. |
| **Wallpaper** | hyprpaper / swww | Static or animated wallpaper daemon. |
| **Idle/Lock** | hypridle + hyprlock | Lock screen and idle management, both native to Hyprland. |
| **Screenshots** | grim + slurp + swappy | Screenshot (grim), region select (slurp), annotate (swappy). |
| **Screen Recording** | wf-recorder / obs-studio | Record Wayland outputs using PipeWire. |
| **Color Temperature / Shaders** | wlsunset / gammastep / hyprshade | Adjust screen warmth or apply real-time shaders for visual effects. |
| **On-Screen Display (OSD)** | swayosd / wob | Display volume or brightness overlays. |

---

## ⚙️ System & Session Tools

| Purpose | Tool | Notes |
|----------|------|-------|
| **Display/Login Manager** | greetd + tuigreet | Lightweight Wayland-native login. |
| **Network Management** | NetworkManager + nm-connection-editor | Graphical network management; integrates with Waybar. |
| **Bluetooth** | bluez + blueman | Bluetooth stack and GUI manager. |
| **File Manager** | Nautilus | Default GNOME file manager, stable and fully Wayland-compatible. |
| **Terminal Emulator** | kitty / wezterm / alacritty | Modern GPU-accelerated terminals compatible with Wayland. |
| **System Info Overlay** | neofetch / fastfetch | Optional visual system summary. |

---

## 🧩 Optional / Advanced Enhancements

| Feature | Tool | Description |
|----------|------|-------------|
| **Compositor Extensions** | hyprshade / wlogout | Shader filters and logout menus. |
| **Audio Visualization** | cava | Terminal-based real-time audio spectrum. |
| **App Launcher Theming** | rofi-wayland themes | CSS-based customization for menus. |
| **Notification Center Integration** | swaync-module in Waybar | Centralized notifications. |
| **Clipboard GUI** | cliphist-rofi | Select clipboard entries directly from rofi. |
| **Dynamic Wallpaper Sync** | pywal / wallust | Sync color palette with wallpaper for consistent theming. |

---

## 🐧 Distro-Specific Packages

| Purpose | Arch / EndeavourOS / Garuda | Fedora | Ubuntu / Debian | OpenSUSE Tumbleweed |
|----------|-------------------------------|---------|----------------|-------------------|
| **Compositor** | hyprland, wayland, xorg-xwayland | hyprland, wayland, xorg-xwayland | hyprland, wayland, xwayland | hyprland, wayland, xorg-xwayland |
| **Bar** | waybar | waybar | waybar | waybar |
| **Portals** | xdg-desktop-portal, xdg-desktop-portal-hyprland | xdg-desktop-portal, xdg-desktop-portal-hyprland | xdg-desktop-portal, xdg-desktop-portal-hyprland | xdg-desktop-portal, xdg-desktop-portal-hyprland |
| **Audio** | pipewire, wireplumber | pipewire, wireplumber | pipewire, wireplumber | pipewire, wireplumber |
| **Policy Agent** | hyprpolkitagent / polkit-gnome | hyprpolkitagent / polkit-gnome | hyprpolkitagent / polkit-gnome | hyprpolkitagent / polkit-gnome |
| **Launcher** | rofi | rofi | rofi | rofi |
| **Notifications** | swaync, dunst | swaync, dunst | swaync, dunst | swaync, dunst |
| **Clipboard** | wl-clipboard, cliphist, copyq, clipman | wl-clipboard, cliphist, copyq | wl-clipboard, cliphist, copyq | wl-clipboard, cliphist, copyq |
| **Screenshots** | grim, slurp, swappy | grim, slurp, swappy | grim, slurp, swappy | grim, slurp, swappy |
| **Screen Recording** | wf-recorder | wf-recorder | wf-recorder | wf-recorder |
| **Wallpaper** | hyprpaper, swww | hyprpaper, swww | hyprpaper, swww | hyprpaper, swww |
| **Idle/Lock** | hypridle, hyprlock | hypridle, hyprlock | hypridle, hyprlock | hypridle, hyprlock |
| **Color/Shaders** | wlsunset, gammastep, hyprshade | wlsunset, gammastep, hyprshade | wlsunset, gammastep, hyprshade | wlsunset, gammastep, hyprshade |
| **OSD** | swayosd, wob | swayosd, wob | swayosd, wob | swayosd, wob |
| **Network** | networkmanager | NetworkManager | network-manager | NetworkManager |
| **Bluetooth** | bluez, blueman | bluez, blueman | bluez, blueman | bluez, blueman |
| **File Manager** | nautilus | nautilus | nautilus | nautilus |
| **Terminal** | kitty, wezterm, alacritty | kitty, wezterm, alacritty | kitty, wezterm, alacritty | kitty, wezterm, alacritty |
| **Optional Enhancements** | cava, pywal, wallust, rofi-themes | cava, pywal, wallust | cava, pywal, wallust | cava, pywal, wallust |

---

## 💡 Notes
- **hyprpolkitagent** is the recommended polkit agent for Hyprland. If unavailable, **polkit-gnome** or **lxqt-policykit** can substitute. Do **not** run multiple polkit agents simultaneously.
- Only one **xdg-desktop-portal backend** should run (prefer `xdg-desktop-portal-hyprland`).
- PipeWire and WirePlumber replace PulseAudio and JACK.
- Prefer **Wayland-native** tools whenever possible.

---

### 📘 References
- [Hyprland Wiki](https://wiki.hyprland.org/Getting-Started/Installation/)
- [ArchWiki: Hyprland](https://wiki.archlinux.org/title/Hyprland)
- [Waybar Documentation](https://github.com/Alexays/Waybar)
- [Sway Notification Center](https://github.com/ErikReider/SwayNotificationCenter)
- [PipeWire Project](https://pipewire.org/)
