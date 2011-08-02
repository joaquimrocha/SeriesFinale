import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Sheet {
    acceptButtonText: "Close"

    content: Flickable {
        id: content
        anchors.fill: parent
        anchors.margins: 18
        contentWidth: grid.width
        contentHeight:  grid.height
        flickableDirection: Flickable.VerticalFlick
        Column {
            id: grid
            width: parent.width
            spacing: 18

            Text {
                text: "Show sorting:"
                font.pixelSize: 26
            }
            ButtonRow {
                Button { text: "By title"; onClicked: settings.showsSort=0 }
                Button { text: "By episode date"; onClicked: settings.showsSort=1; checked: settings.showsSort == 1 }
            }

            Text {
                text: "Episode sorting:"
                font.pixelSize: 26
            }
            ButtonRow {
                Button { text: "1-9"; onClicked: settings.episodesOrder=0 }
                Button { text: "9-1"; onClicked: settings.episodesOrder=1; checked: settings.episodesOrder == 1 }
            }

            Item {
                height: addSpeciealSeasons.height
                width: content.width

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Add special seasons:"
                    font.pixelSize: 26
                }

                Switch {
                    id: addSpeciealSeasons
                    anchors.right: parent.right
                    checked: settings.addSpecialSeasons
                    onCheckedChanged: settings.addSpecialSeasons = checked
                }
            }

            Item {
                height: hideCompletedShows.height
                width: content.width

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Hide completely watched:"
                    font.pixelSize: 26
                }

                Switch {
                    id: hideCompletedShows
                    anchors.right: parent.right
                    checked: settings.hideCompletedShows
                    onCheckedChanged: settings.hideCompletedShows = checked
                }
            }
        }
    }
}
