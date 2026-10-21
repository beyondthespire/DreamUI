import QtQuick
import QtCore
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    fullRepresentation: ColumnLayout {
        Layout.minimumWidth: 95
        Layout.minimumHeight: 270
        Layout.preferredWidth: 100
        Layout.preferredHeight: 285
        spacing: 12
        Repeater {
            model: [
                {label: i18n("Computer"), icon: "computer", url: "file:///"},
                {label: i18n("Home"), icon: "user-home", url: "file://" + StandardPaths.writableLocation(StandardPaths.HomeLocation)},
                {label: i18n("Trash"), icon: "user-trash", url: "trash:/"}
            ]
            Controls.AbstractButton {
                id: place
                required property var modelData
                Layout.fillWidth: true
                Layout.fillHeight: true
                Accessible.name: modelData.label
                onClicked: Qt.openUrlExternally(modelData.url)
                background: Rectangle { radius: 4; color: place.hovered || place.activeFocus ? "#557cace0" : "transparent"; border.color: place.activeFocus ? "#d3e8ff" : "transparent" }
                contentItem: Column {
                    spacing: 5
                    Kirigami.Icon { anchors.horizontalCenter: parent.horizontalCenter; source: place.modelData.icon; width: 46; height: 46 }
                    Text { width: parent.width; text: place.modelData.label; color: "white"; horizontalAlignment: Text.AlignHCenter; style: Text.Outline; styleColor: "#263a60"; font.pixelSize: 13 }
                }
            }
        }
    }
}
