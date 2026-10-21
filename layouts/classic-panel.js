// Opt-in: refuses to replace existing panels. Remove your existing panel through
// Plasma Edit Mode first if you want this layout. Original config is backed up
// before apply. Re-running this script will not duplicate the DreamUI panel.
var existing = panels();
var dreamPanel = null;
for (var i = 0; i < existing.length; i++) {
    existing[i].currentConfigGroup = ["DreamUI"];
    if (existing[i].readConfig("managed", "false") === "true") dreamPanel = existing[i];
}
if (dreamPanel) {
    print("DREAMUI_PANEL_OK: already installed");
} else if (existing.length > 0) {
    throw new Error("Existing panels preserved. Remove them in Edit Mode before applying the optional DreamUI layout.");
} else {
    var panel = new Panel;
    panel.location = "bottom";
    panel.height = 44;
    panel.hiding = "none";
    var launcher = panel.addWidget("org.kde.plasma.kickoff");
    launcher.currentConfigGroup = ["General"];
    launcher.writeConfig("icon", "start-here");
    panel.addWidget("org.kde.plasma.pager");
    panel.addWidget("org.kde.plasma.taskmanager");
    panel.addWidget("org.kde.plasma.systemtray");
    panel.addWidget("org.kde.plasma.digitalclock");
    panel.addWidget("org.kde.plasma.showdesktop");
    panel.currentConfigGroup = ["DreamUI"];
    panel.writeConfig("managed", "true");
    print("DREAMUI_PANEL_OK: created");
}
