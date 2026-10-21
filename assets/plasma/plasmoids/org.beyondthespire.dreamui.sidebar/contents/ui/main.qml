import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.private.mpris as Mpris

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation
    property date now: new Date()
    readonly property var player: media.currentPlayer
    Mpris.Mpris2Model { id: media }
    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }
    fullRepresentation: ColumnLayout {
        Layout.minimumWidth: 205
        Layout.minimumHeight: 370
        Layout.preferredWidth: 230
        Layout.preferredHeight: 420
        spacing: 14
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 175
            radius: 9
            border.color: "#96b7db"
            gradient: Gradient {
                GradientStop { position: 0; color: "#a387a2c8" }
                GradientStop { position: 0.5; color: "#dd3d5d89" }
                GradientStop { position: 1; color: "#e32c4972" }
            }
            Column {
                anchors.centerIn: parent
                width: parent.width - 20
                spacing: 7
                Text { width: parent.width; horizontalAlignment: Text.AlignHCenter; text: Qt.formatTime(root.now, "hh:mm"); color: "#fff"; font.pixelSize: 42; font.weight: Font.Light }
                Text { width: parent.width; horizontalAlignment: Text.AlignHCenter; text: Qt.formatDate(root.now, "dddd"); color: "#ecf3ff"; font.pixelSize: 16 }
                Text { width: parent.width; horizontalAlignment: Text.AlignHCenter; text: Qt.formatDate(root.now, "MMMM d"); color: "#dfebff"; font.pixelSize: 13 }
                Rectangle { width: parent.width - 16; x: 8; height: 1; color: "#7695bd" }
                Text { width: parent.width; horizontalAlignment: Text.AlignHCenter; text: i18n("Make room to dream."); color: "#e8f1ff"; font.pixelSize: 11 }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 190
            radius: 9
            border.color: "#96b7db"
            gradient: Gradient {
                GradientStop { position: 0; color: "#dd6687b0" }
                GradientStop { position: 1; color: "#ed2c4972" }
            }
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 13
                spacing: 7
                Text { text: i18n("NOW PLAYING"); color: "#dfedff"; font.pixelSize: 11; font.bold: true }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 55
                    color: "#253c61"
                    radius: 3
                    Image { id: art; anchors.fill: parent; fillMode: Image.PreserveAspectFit; source: root.player ? root.player.artUrl : ""; asynchronous: true }
                    Kirigami.Icon { anchors.centerIn: parent; width: 40; height: 40; source: "folder-music"; visible: art.status !== Image.Ready }
                }
                Text { text: root.player && root.player.track ? root.player.track : i18n("Your music, right here"); color: "#fff"; font.pixelSize: 13; elide: Text.ElideRight; Layout.fillWidth: true }
                Text { text: root.player ? (root.player.artist || root.player.identity) : i18n("Play something in Elisa or a browser"); color: "#d3e3f9"; font.pixelSize: 11; elide: Text.ElideRight; Layout.fillWidth: true }
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Controls.ToolButton { icon.name: "media-skip-backward"; Accessible.name: i18n("Previous track"); enabled: !!root.player && root.player.canGoPrevious; onClicked: root.player.Previous() }
                    Controls.ToolButton { icon.name: root.player && root.player.playbackStatus === Mpris.PlaybackStatus.Playing ? "media-playback-pause" : "media-playback-start"; Accessible.name: i18n("Play or pause"); enabled: !!root.player && (root.player.canPlay || root.player.canPause); onClicked: root.player.PlayPause() }
                    Controls.ToolButton { icon.name: "media-skip-forward"; Accessible.name: i18n("Next track"); enabled: !!root.player && root.player.canGoNext; onClicked: root.player.Next() }
                }
            }
        }
    }
}
