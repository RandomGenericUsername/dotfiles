#!/usr/bin/env bash
# hyprland-docker-bootstrap.sh (nested mode, Docker-only)
set -euo pipefail

: "${IMAGE_NAME:=hyprland:latest}"
: "${CONTAINER_NAME:=hypr-nested}"
: "${USE_HOST_CONFIGS:=1}"
: "${ENABLE_PIPEWIRE:=1}"
: "${NVIDIA:=0}"
: "${LOOSEN_SECCOMP:=0}"     # 1 = add --security-opt seccomp=unconfined (quiets Xwayland warning)
: "${KEEP_WORKDIR:=0}"

say()  { printf "\033[1;36m[bootstrap]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[warn]\033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m[error]\033[0m %s\n" "$*"; }

command -v docker >/dev/null || { err "Docker not found."; exit 1; }
if ! docker info >/dev/null 2>&1; then
  if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    warn "Docker daemon not reachable. Trying sudo..."
    exec sudo -E bash "$0" "$@"
  fi
fi
if command -v systemctl >/dev/null 2>&1; then
  systemctl is-active --quiet docker 2>/dev/null || sudo systemctl enable --now docker || true
fi
docker info >/dev/null 2>&1 || { err "Cannot access Docker daemon."; exit 1; }

RUNTIME_DIR_HOST="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
[[ -d "$RUNTIME_DIR_HOST" ]] || { err "No XDG_RUNTIME_DIR ($RUNTIME_DIR_HOST)."; exit 1; }
if [[ -S "$RUNTIME_DIR_HOST/wayland-0" ]]; then WAYSOCK="wayland-0"
else WAYSOCK="$(ls "$RUNTIME_DIR_HOST" | grep -E '^wayland(-[0-9]+)?$' | head -n1 || true)"; fi
[[ -n "${WAYSOCK:-}" ]] || { err "No wayland-* socket found in $RUNTIME_DIR_HOST."; exit 1; }

PIPEWIRE_FLAGS=()
if [[ "$ENABLE_PIPEWIRE" == "1" && -S "$RUNTIME_DIR_HOST/pipewire-0" ]]; then
  PIPEWIRE_FLAGS+=(-v "$RUNTIME_DIR_HOST/pipewire-0:/tmp/xdg-runtime/pipewire-0")
fi

SELINUX_SUFFIX=""
[[ -f /etc/selinux/config ]] && SELINUX_SUFFIX=":Z"

CFG_MOUNTS=()
if [[ "$USE_HOST_CONFIGS" == "1" ]]; then
  if [[ -d "$HOME/.config/hypr" ]]; then
    if [[ -f "$HOME/.config/hypr/hyprland.conf" ]]; then
      CFG_MOUNTS+=(-v "$HOME/.config/hypr:/home/hypr/.config/hypr${SELINUX_SUFFIX}")
    else
      warn "~/.config/hypr exists but has no hyprland.conf; not mounting so baked config is used."
    fi
  fi
  [[ -d "$HOME/.config/waybar" ]] && CFG_MOUNTS+=(-v "$HOME/.config/waybar:/home/hypr/.config/waybar${SELINUX_SUFFIX}")
fi

GPU_FLAGS=(--device /dev/dri)
if [[ "$NVIDIA" == "1" ]]; then
  if docker run --rm --gpus all --entrypoint true alpine:3.20 >/dev/null 2>&1; then
    GPU_FLAGS+=(--gpus all -e __GLX_VENDOR_LIBRARY_NAME=nvidia)
  else
    warn "--gpus all not available; continuing without NVIDIA. (Install nvidia-container-toolkit; then 'sudo nvidia-ctk runtime configure --runtime=docker' and restart docker)"
  fi
fi

SEC_FLAGS=()
if [[ "$LOOSEN_SECCOMP" == "1" ]]; then
  SEC_FLAGS+=(--security-opt seccomp=unconfined)
fi

USE_BUILDX=0; docker buildx version >/dev/null 2>&1 && USE_BUILDX=1
WORKDIR="$(mktemp -d -p "${TMPDIR:-/tmp}" hyprland-docker-XXXXXX)"
cleanup(){ [[ "$KEEP_WORKDIR" == "1" ]] || rm -rf "$WORKDIR"; }
trap cleanup EXIT
say "Using temp workdir: $WORKDIR"; cd "$WORKDIR"

cat > Dockerfile.hyprland <<'EOF'
FROM archlinux:latest
ENV LANG=C.UTF-8 TZ=UTC
RUN pacman -Syu --noconfirm \
    hyprland waybar xdg-desktop-portal-hyprland xdg-desktop-portal \
    xorg-xwayland wl-clipboard grim slurp swappy \
    foot kitty alacritty dbus polkit seatd git curl wget unzip nano vim \
    xkeyboard-config \
    && pacman -Scc --noconfirm
ARG USERNAME=hypr ARG UID=1000 ARG GID=1000
RUN groupadd -g ${GID} ${USERNAME} && useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME}
ENV XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=Hyprland WLR_NO_HARDWARE_CURSORS=1
RUN mkdir -p /home/${USERNAME}/.config/hypr && \
    printf '%s\n' \
      'monitor=,preferred,auto,1' \
      'exec-once=waybar' \
      'input:kb_layout=us' \
      > /home/${USERNAME}/.config/hypr/hyprland.conf && \
    chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.config
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
USER ${USERNAME}
WORKDIR /home/${USERNAME}
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
EOF

cat > entrypoint.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export HYPRLAND_NO_SPLASH=1
export WLR_BACKENDS=wayland
export WLR_RENDERER_ALLOW_SOFTWARE=1
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/xdg-runtime}"
mkdir -p "$XDG_RUNTIME_DIR" || true
chmod 700 "$XDG_RUNTIME_DIR" 2>/dev/null || true
if ! pgrep -u "$(id -u)" -f "dbus-daemon --session" >/dev/null 2>&1; then
  dbus-daemon --session --address=unix:path=${XDG_RUNTIME_DIR}/bus --fork || true
  export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
fi
exec Hyprland
EOF
chmod +x entrypoint.sh

printf '%s\n' '**/.git' '**/.DS_Store' > .dockerignore

say "Building image: $IMAGE_NAME"
if [[ "$USE_BUILDX" -eq 1 ]]; then
  export DOCKER_BUILDKIT=1
  docker buildx build --load -t "$IMAGE_NAME" -f Dockerfile.hyprland .
else
  export DOCKER_BUILDKIT=0
  warn "buildx not found; using legacy builder (DOCKER_BUILDKIT=0)."
  docker build -t "$IMAGE_NAME" -f Dockerfile.hyprland .
fi

say "Launching Hyprland (nested)…"
say "Wayland socket: $RUNTIME_DIR_HOST/$WAYSOCK"
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

set -x
docker run --rm -it \
  --tmpfs /tmp/xdg-runtime:uid=1000,gid=1000,mode=700 \
  -e NESTED=1 \
  -e WAYLAND_DISPLAY="$WAYSOCK" \
  -e XDG_RUNTIME_DIR="/tmp/xdg-runtime" \
  -v "$RUNTIME_DIR_HOST/$WAYSOCK:/tmp/xdg-runtime/$WAYSOCK${SELINUX_SUFFIX}" \
  "${PIPEWIRE_FLAGS[@]}" \
  "${CFG_MOUNTS[@]}" \
  "${GPU_FLAGS[@]}" \
  "${SEC_FLAGS[@]}" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"
set +x
