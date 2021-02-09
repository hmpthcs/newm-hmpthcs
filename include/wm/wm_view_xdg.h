#ifndef WM_VIEW_XDG_H
#define WM_VIEW_XDG_H

#include <wayland-server.h>
#include <wlr/types/wlr_xdg_shell.h>

#include "wm/wm_view.h"

struct wm_view_xdg;

struct wm_popup_xdg {
    struct wm_view_xdg* toplevel;

    struct wlr_xdg_popup* wlr_xdg_popup;

    struct wl_listener map;
    struct wl_listener unmap;
    struct wl_listener destroy;
    struct wl_listener new_popup;
};

void wm_popup_xdg_init(struct wm_popup_xdg* popup, struct wm_view_xdg* toplevel, struct wlr_xdg_popup* wlr_xdg_popup);
void wm_popup_xdg_destroy(struct wm_popup_xdg* popup);

struct wm_view_xdg {
    struct wm_view super;

    struct wlr_xdg_surface* wlr_xdg_surface;

    bool floating;
    bool constrain_popups_to_toplevel; /* false = constrain to output */

    struct wl_listener map;
    struct wl_listener unmap;
    struct wl_listener destroy;
    struct wl_listener new_popup;
};

void wm_view_xdg_init(struct wm_view_xdg* view, struct wm_server* server, struct wlr_xdg_surface* surface);


#endif
