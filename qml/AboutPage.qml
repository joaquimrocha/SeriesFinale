import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: aboutPage

    property string license: 'SeriesFinale is free software: you can redistribute it ' +
'and/or modify it under the terms of the GNU General Public License as published by ' +
'the Free Software Foundation, either version 3 of the License, or ' +
'(at your option) any later version.<br/><br/>' +

'SeriesFinale is distributed in the hope that it will be useful, ' +
'but WITHOUT ANY WARRANTY; without even the implied warranty of ' +
'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the ' +
'GNU General Public License for more details.<br/><br/>' +

'You should have received a copy of the GNU General Public License ' +
'along with SeriesFinale.  If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.'

    Flickable {
        id: flickableText
        height: parent.height
        width: parent.width
        contentHeight: contents.height
        clip: true

        Column {
            id: contents
            spacing: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 40

            Image {
                id: aboutImage
                anchors.horizontalCenter: parent.horizontalCenter
                source: 'icons/seriesfinale.svg'
            }

            Text {
                font.weight: Font.Bold
                font.pixelSize: 24
                text: 'SeriesFinale ' + version + '<br/>Harmattan Edition'
                color: 'white'
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                font.weight: Font.Bold
                font.pixelSize: 20
                text: 'Copyright © 2011-2015 Joaquim Rocha'
                color: 'white'
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                font.pixelSize: 20
                text: '<strong>Special thanks to:</strong> <br/>&nbsp;&nbsp;Juan Suarez Romero\
                      <br/>&nbsp;&nbsp;Micke Prag'
                color: 'white'
                anchors.left: parent.left
                onLinkActivated: Qt.openUrlExternally(link)
            }

            Text {
                font.weight: Font.Bold
                font.pixelSize: 16
                text: 'SeriesFinale uses <a href="http://www.thetvdb.com">TheTVDB</a> API but is not endorsed or certified by TheTVDB. Please contribute to it if you can.'
                color: 'white'
                wrapMode: Text.WordWrap
                font.family: "Nokia Pure Text Light"
                width: parent.width
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                font.weight: Font.Bold
                font.pixelSize: 16
                text: license
                color: 'white'
                wrapMode: Text.WordWrap
                font.family: "Nokia Pure Text Light"
                width: parent.width
                anchors.horizontalCenter: parent.horizontalCenter
                onLinkActivated: Qt.openUrlExternally(link)
            }
        }
    }
    ScrollDecorator{ flickableItem: flickableText }

    tools: ToolBarLayout {
        ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
    }
}
