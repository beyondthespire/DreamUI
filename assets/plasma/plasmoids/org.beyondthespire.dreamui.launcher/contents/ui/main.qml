import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.private.kicker as Kicker

PlasmoidItem {
    id: root
    Plasmoid.icon: "start-here"
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: compactRepresentation
    switchWidth: fullRepresentationItem ? fullRepresentationItem.Layout.minimumWidth : 330
    switchHeight: fullRepresentationItem ? fullRepresentationItem.Layout.minimumHeight : 480
    property bool allApplications: false
    property var allAppsModel: null
    property var matches: null
    property string errorText: ""

    function launch(model, row) {
        if (model && row >= 0 && model.trigger(row, "", null)) {
            root.expanded = false;
            root.errorText = "";
        } else {
            root.errorText = i18n("The application could not be opened.");
        }
    }

    // Models are supplied by KDE; no shell commands are constructed from queries.
    Kicker.RootModel {
        id: apps
        autoPopulate: true
        appletInterface: root
        appNameFormat: 0
        flat: true
        sorted: true
        showSeparators: false
        showAllApps: true
        showAllAppsCategorized: false
        showRecentApps: false
        showRecentDocs: false
        showPowerSession: false
        showFavoritesPlaceholder: false
        onRefreshed: root.allAppsModel = apps.modelForRow(0)
        Component.onCompleted: root.allAppsModel = apps.modelForRow(0)

        property Kicker.FavoritesModel shortcuts: Kicker.FavoritesModel {
            favorites: ["org.kde.dolphin.desktop", "systemsettings.desktop",
                        "org.kde.gwenview.desktop", "org.kde.elisa.desktop",
                        "org.kde.kate.desktop", "org.kde.konsole.desktop"]
        }
        property Kicker.FavoritesModel session: Kicker.FavoritesModel {
            favorites: ["logout", "shutdown"]
        }
    }
    Kicker.RunnerModel {
        id: search
        appletInterface: root
        favoritesModel: apps.shortcuts
        runners: ["krunner_services", "krunner_systemsettings"]
        mergeResults: true
        onCountChanged: root.matches = count > 0 ? modelForRow(0) : null
        onQueryFinished: root.matches = count > 0 ? modelForRow(0) : null
    }

    compactRepresentation: Controls.AbstractButton {
        id: startButton
        Layout.minimumWidth: 100
        Layout.preferredWidth: 108
        implicitHeight: 44
        Accessible.name: i18n("Open Dream Launcher")
        onClicked: root.expanded = !root.expanded
        background: Rectangle {
            radius: 5
            color: startButton.hovered || root.expanded ? "#b9d9f5" : "transparent"
            border.color: startButton.activeFocus ? "#3670bf" : "transparent"
        }
        contentItem: RowLayout {
            spacing: 5
            Kirigami.Icon { source: "start-here"; Layout.preferredWidth: 38; Layout.preferredHeight: 38 }
            Text { text: i18n("Dream"); color: "#1b3656"; font.bold: true; font.pixelSize: 14 }
        }
    }

    fullRepresentation: Rectangle {
        id: menu
        Layout.minimumWidth: 310
        Layout.minimumHeight: 420
        Layout.preferredWidth: 330
        Layout.preferredHeight: 480
        radius: 7
        border.color: "#a5c8eb"
        gradient: Gradient {
            GradientStop { position: 0; color: "#7898c0" }
            GradientStop { position: 0.24; color: "#35557f" }
            GradientStop { position: 1; color: "#28456b" }
        }
        Keys.onEscapePressed: root.expanded = false
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                Kirigami.Icon { source: "dreamui"; Layout.preferredWidth: 42; Layout.preferredHeight: 42 }
                Text { text: i18n("Welcome home"); color: "#f5faff"; font.pixelSize: 18; Layout.fillWidth: true }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#f1f6ff"
                radius: 4
                border.color: "#c4d8ed"
                ListView {
                    id: list
                    anchors.fill: parent
                    anchors.margins: 5
                    clip: true
                    model: field.text.trim().length ? root.matches : root.allApplications ? root.allAppsModel : apps.shortcuts
                    currentIndex: 0
                    keyNavigationEnabled: true
                    Controls.ScrollBar.vertical: Controls.ScrollBar {}
                    Keys.onReturnPressed: root.launch(model, currentIndex)
                    Keys.onEnterPressed: root.launch(model, currentIndex)
                    delegate: Controls.ItemDelegate {
                        id: entry
                        required property int index
                        required property string display
                        required property var decoration
                        width: ListView.view.width
                        height: 43
                        text: display
                        Accessible.name: display
                        onClicked: root.launch(list.model, index)
                        background: Rectangle {
                            radius: 3
                            color: entry.hovered || (list.activeFocus && list.currentIndex === entry.index) ? "#c7e1f8" : "transparent"
                            border.color: entry.hovered ? "#9ec0df" : "transparent"
                        }
                        contentItem: RowLayout {
                            Kirigami.Icon { source: entry.decoration; Layout.preferredWidth: 29; Layout.preferredHeight: 29 }
                            Text { text: entry.display; color: "#203954"; font.pixelSize: 14; elide: Text.ElideRight; Layout.fillWidth: true }
                        }
                    }
                    Text {
                        anchors.centerIn: parent
                        visible: list.count === 0
                        text: i18n("No applications found")
                        color: "#586c86"
                    }
                }
            }
            Controls.Button {
                Layout.fillWidth: true
                text: root.allApplications ? i18n("Back to favorites") : i18n("All applications")
                onClicked: { root.allApplications = !root.allApplications; field.clear(); list.currentIndex = 0; }
            }
            Controls.TextField {
                id: field
                Layout.fillWidth: true
                placeholderText: i18n("Search applications…")
                color: "#213b58"
                onTextChanged: { search.query = text; list.currentIndex = 0; }
                Keys.onDownPressed: { list.forceActiveFocus(); list.currentIndex = 0; }
                onAccepted: root.launch(list.model, list.currentIndex)
                background: Rectangle { color: "#f6faff"; radius: 4; border.color: field.activeFocus ? "#8dbce8" : "#bacce1" }
            }
            Text { visible: root.errorText.length > 0; text: root.errorText; color: "#fff"; wrapMode: Text.Wrap; Layout.fillWidth: true }
            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }
                Repeater {
                    model: apps.session
                    Controls.Button {
                        required property int index
                        required property string display
                        text: display
                        onClicked: root.launch(apps.session, index)
                    }
                }
            }
        }
        Connections {
            target: root
            function onExpandedChanged() {
                if (root.expanded) { field.clear(); root.errorText = ""; field.forceActiveFocus(); }
            }
        }
    }
}
