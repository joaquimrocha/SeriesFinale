import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property variant show: undefined
    property variant episode: undefined
    property string seasonImg: ''

    Header {
        id: header
        text: episode.title
        anchors.top: parent.top
    }

    Column {
        id: metaData
        anchors.top: header.bottom
        anchors.topMargin: 18
        anchors.left: parent.left
        anchors.leftMargin: 18
        width: parent.width
        spacing: 18
        
        Row {
            width: parent.width
            clip: true
            spacing: 18
            
            Image {
                id: image
                width: 128
                //height: 192
                source: seasonImg
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
                    ratingValue: episode.episodeRating
                    //count: 97
                }
            }
        }
    }

    Header {
        id: bioHeader
        anchors.top: metaData.bottom
        anchors.topMargin: 18
        text: "Bio"
    }

    Flickable {
        id: flickableText
        anchors.top: bioHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: watched.top
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

    CheckBox {
        id: watched
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 18
        anchors.left: parent.left
        anchors.leftMargin: 18
        text: "Watched"
        onClicked: episode.isWatched = !episode.isWatched
    }
    onEpisodeChanged: watched.checked = episode.isWatched

	tools: ToolBarLayout {
		ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
        ToolIcon { iconId: "toolbar-up"; onClicked: episode = show.get_previous_episode(episode) }
        ToolIcon { iconId: "toolbar-down"; onClicked: episode = show.get_next_episode(episode) }
	}

    states: [
        State {
            name: "inLandscape"
            when: !rootWindow.inPortrait
            PropertyChanges { target: metaData; width: parent.width / 2 }
            AnchorChanges {
                target: flickableText
                anchors.top: header.bottom
                anchors.left: metaData.right
                anchors.bottom: page.bottom
            }
            PropertyChanges { target: bioHeader; visible: false }
        }
    ]
}
