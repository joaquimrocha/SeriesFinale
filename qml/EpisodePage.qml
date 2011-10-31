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

    Item {
        id: dataItem
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.topMargin: 10
        width: rootWindow.inPortrait ? parent.width : parent.width / 2
        anchors.margins: 15

        Grid {
              columns: 2
              spacing: 10

              Text {
                  text: "Air date:"
                  font.pixelSize: 22
                  color: 'white'
                  font.weight: Font.Bold
              }
              Text {
                  text: episode.airDateText
                  font.pixelSize: 22
                  color: 'white'
              }
              Text {
                  text: "Rating:"
                  font.pixelSize: 22
                  color: 'white'
                  font.weight: Font.Bold
              }
              RatingIndicator {
                  maximumValue: 10
                  ratingValue: episode.episodeRating
              }
          }
    }

    Item {
        id: overviewItem
        anchors.top: rootWindow.inPortrait ? dataItem.bottom : dataItem.top
        anchors.left: rootWindow.inPortrait ? parent.left : dataItem.right
        anchors.right: parent.right
        anchors.bottom: watched.top
        anchors.margins: 16

        Flickable {
            id: flickableText
            height: parent.height
            width: parent.width
            contentHeight: text.height
            clip: true

            Text {
                id: overviewTitle
                font.weight: Font.Bold
                font.pixelSize: 22
                text: 'Overview:'
                color: 'white'
            }

            Text {
                id: text
                anchors.top: overviewTitle.bottom
                anchors.topMargin: 10
                width: parent.width
                text: episode.overviewText
                font.weight: Font.Light
                font.pixelSize: 22
                color: 'white'
                wrapMode: Text.Wrap
            }
        }
        ScrollDecorator{ flickableItem: flickableText }
    }

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
            PropertyChanges {
                target: dataItem
                width: parent.width / 2
            }
            AnchorChanges {
                target: overviewItem
                anchors.top: header.bottom
                anchors.left: dataItem.right
                anchors.bottom: page.bottom
            }
        },
        State {
            name: "inPortrait"
            when: rootWindow.inPortrait
            PropertyChanges {
                target: dataItem
                width: parent.width
            }
            AnchorChanges {
                target: overviewItem
                anchors.top: dataItem.bottom
                anchors.left: dataItem.left
                anchors.bottom: page.bottom
            }
        }

    ]
}
