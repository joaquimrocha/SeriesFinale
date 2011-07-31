import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Sheet {
    acceptButtonText: "Close"
    //MouseArea { anchors.fill: parent }
    
    content: Flickable {
        anchors.fill: parent
        anchors.margins: 18
        contentWidth: grid.width
        contentHeight:  grid.height
        flickableDirection: Flickable.VerticalFlick
        Column {
            id: grid
            width: parent.width
            spacing: 18
            //columns: 2
            
            Text {
                text: "Show sorting:"
                font.pixelSize: 26
            }
            ButtonRow {
                Button { text: "By title" }
                Button { text: "By episode date" }
            }

            Text {
                text: "Season sorting:"
                font.pixelSize: 26
            }
            ButtonRow {
                Button { text: "A-Z" }
                Button { text: "Z-A" }
            }

            Text {
                text: "Episode sorting:"
                font.pixelSize: 26
            }
            ButtonRow {
                Button { text: "A-Z" }
                Button { text: "Z-A" }
            }
            
            Row {
                Text {
                    text: "Add special seasons"
                    font.pixelSize: 26
                }

                Switch {
                    checked: true
                }
            }
        }
    }
}