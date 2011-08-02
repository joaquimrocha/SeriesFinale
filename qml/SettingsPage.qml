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
                Button { text: "By episode date"; checked: true }
            }

            Text {
                text: "Episode sorting:"
                font.pixelSize: 26
            }
            ButtonRow {
                Button { text: "1-9" }
                Button { text: "9-1"; checked: true }
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
