import QtQuick 1.1
import com.nokia.meego 1.0

Rectangle {
	width: parent.width
	height: 64
	color: "blue"

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
	}

    BusyIndicator {
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 18
        visible: busy
        running: busy
        platformStyle: BusyIndicatorStyle { spinnerFrames: "image://theme/spinnerinverted" }
    }
}
