import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    id: header
    width: parent.width
    height: 64

    property alias text: label.text
    property bool hasRefreshAction: false
    property bool busy: false
    property alias anchorPoint: refreshAction.left
    signal refreshActionActivated()

    Text{
        id: label
        color: "white"
        font.weight: Font.Bold
        font.pixelSize: 26
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 16
        font.family: "Nokia Pure Text Light"
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
