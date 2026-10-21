// Install replacement before removing old panels. Preserve other screens/widgets.
var required = ["org.beyondthespire.dreamui.launcher", "org.beyondthespire.dreamui.sidebar", "org.beyondthespire.dreamui.places", "org.kde.plasma.taskmanager", "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock", "org.kde.plasma.showdesktop"];
for (var i = 0; i < required.length; i++) {
    if (knownWidgetTypes.indexOf(required[i]) < 0) throw new Error("DREAMUI_WAIT: Missing widget " + required[i]);
}
var desktop = desktopForScreen(0);
if (!desktop) throw new Error("DREAMUI_WAIT: No desktop on screen 0");
var old = panels().filter(function(p) { return p.screen === 0; });
var added = [];
var panel;
try {
    panel = new Panel;
    panel.screen = 0;
    panel.location = "bottom";
    panel.height = 44;
    panel.lengthMode = "fill";
    panel.hiding = "none";
    panel.floating = false;
    [required[0], required[3], required[4], required[5], required[6]].forEach(function(id) {
        var w = panel.addWidget(id);
        if (!w) throw new Error("Could not create " + id);
    });
    var bounds = screenGeometry(0);
    [required[1], required[2]].forEach(function(id, index) {
        var exists = desktop.widgets().some(function(w) { return w.type === id; });
        if (!exists) {
            var width = index === 0 ? 230 : 100;
            var height = index === 0 ? Math.min(420, bounds.height - 100) : 285;
            var x = index === 0 ? Math.max(0, bounds.width - width - 24) : 20;
            var widget = desktop.addWidget(id, x, 24, width, height);
            if (!widget) throw new Error("Could not create " + id);
            added.push(widget);
        }
    });
} catch (error) {
    added.forEach(function(w) { w.remove(); });
    if (panel) panel.remove();
    throw error;
}
old.forEach(function(p) { p.remove(); });
print("DREAMUI_DESKTOP_OK");
