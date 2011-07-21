import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property variant show: undefined
    property variant episode: undefined
    property string seasonImg: ''
    
    Column {
        id: metaData
        anchors.top: parent.top
        width: parent.width
        spacing: 18
        
        Header { text: episode.title }
        
        Row {
            width: parent.width
            clip: true
            spacing: 18
            
            Image {
                id: image
                width: 192
                //height: 192
                source: '/home/user/.local/share/seriesfinale/95441_episode_1142761.jpg'
                //source: 'http://www.thetvdb.com/banners/episodes/95441/3510451.jpg' //seasonImg
                fillMode: "PreserveAspectFit"
                smooth: true
            }
            
            Grid {
                columns: 2
                Text { text: "Air date: "; font.pixelSize: 22 }
                Text { text: episode.airDateText; font.pixelSize: 22 }
                Text { text: "Rating: "; font.pixelSize: 22 }
                RatingIndicator {
                    maximumValue: 10
                    ratingValue: 4
                    //count: 97
                }
            }
        }
        
        Header { text: "Bio" }
    }
    
    Flickable {
        id: flickableText
        anchors.top: metaData.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 16
        contentHeight: text.height
        clip: true

        Text {
            id: text
            width: parent.width
            text: episode.overviewText
            font.weight: Font.Light
            font.pixelSize: 22
            color: theme.inverted ? "#d2d2d2" : "#505050"
            wrapMode: Text.Wrap
        }
    }
    ScrollDecorator{ flickableItem: flickableText }

	tools: ToolBarLayout {
		ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
        ToolIcon { iconId: "toolbar-up"; onClicked: episode = show.get_previous_episode(episode) }
        ToolIcon { iconId: "toolbar-down"; onClicked: episode = show.get_next_episode(episode) }
	}

	/*Menu {
		id: myMenu
		MenuLayout {
			MenuItem { 
                text: "Update show"
            }
		}
	}*/
}
