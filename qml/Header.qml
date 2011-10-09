import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    id: header
    width: parent.width
    height: 64

    property alias text: label.text
    property bool busy: false

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

    BusyIndicator {
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 18
        visible: busy
        running: busy
        platformStyle: BusyIndicatorStyle {
                           spinnerFrames: "image://theme/spinnerinverted"
                       }
    }

    Rectangle {
        height: 1
        color: '#fff'
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
        }
    }
}
