import QtQuick 1.1
import com.nokia.meego 1.0

Item {
    id: listItem
    height: 88
    anchors.left: parent.left
    anchors.right: parent.right
    clip: true

    signal clicked
    signal pressAndHold
    property alias title: title.text
    property alias subtitle: subtitle.text
    property alias iconSource: icon.source

    BorderImage {
        id: background
        anchors.fill: parent
        visible: mouseArea.pressed
        source: "image://theme/meegotouch-list-background-pressed-center"
    }

    Row {
        anchors.fill: parent
        anchors.leftMargin: 16
        spacing: 18

        Image {
            id: icon
            anchors.verticalCenter: parent.verticalCenter
            width: 64
            height: 64
            fillMode: "PreserveAspectFit"
            smooth: true
            source: ''
            visible: source != ''
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter

            Label {
                id: title
                font.weight: Font.Bold
                font.pixelSize: 26
                color: theme.inverted ? "#ffffff" : "#282828"
            }

            Label {
                id: subtitle
                font.weight: Font.Light
                font.pixelSize: 22
                color: theme.inverted ? "#d2d2d2" : "#505050"

                visible: text != ""
            }
        }
    }

    Image {
        source: "image://theme/icon-m-common-drilldown-arrow" + (theme.inverted ? "-inverse" : "")
        anchors.right: parent.right;
        anchors.verticalCenter: parent.verticalCenter
    }

    MouseArea {
        id: mouseArea
        anchors.fill: background
        onClicked: listItem.clicked()
        onPressAndHold: listItem.pressAndHold()
    }
}
