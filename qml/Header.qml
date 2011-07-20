import QtQuick 1.1

Rectangle {
	width: parent.width
	height: 64
	color: "blue"

	property alias text: label.text

	Text{
		id: label
		color: "white"
		font.weight: Font.Bold
		font.pixelSize: 26
		anchors.verticalCenter: parent.verticalCenter
		anchors.left: parent.left
		anchors.leftMargin: 16
	}
}
