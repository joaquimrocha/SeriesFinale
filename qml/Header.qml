import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    id: header
    width: parent.width
    anchors.right: parent.right
    anchors.left: parent.left
    height: label.height + 30

    property alias text: label.text
    property bool hasRefreshAction: false
    property bool busy: false
    property alias anchorPoint: refreshAction.left
    property alias textWidth: label.width
    signal refreshActionActivated()

    Text{
        id: label
        color: "white"
        font.weight: Font.Bold
        font.pixelSize: 28
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 16
        font.family: "Nokia Pure Text Light"
        wrapMode: Text.WordWrap
        width: parent.width - refreshIcon.width - 10
    }

    Item {
        id: refreshAction
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 10
        width: refreshIcon.width
        height: refreshIcon.height
        visible: hasRefreshAction

        Image {
            id: refreshIcon
            source: 'icons/refresh-icon.png'
            visible: !busy && hasRefreshAction
        }

        BusyIndicator {
            id: busyIndicator
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            visible: busy
            running: busy
            platformStyle: BusyIndicatorStyle {
                                spinnerFrames: "image://theme/spinnerinverted"
                           }
        }

        MouseArea {
            enabled: !busy && hasRefreshAction
            anchors.fill: parent
            onClicked: { header.refreshActionActivated() }
        }
    }
}
