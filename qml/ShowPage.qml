import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property variant show: undefined
    
    Column {
        id: metaData
        anchors.top: parent.top
        width: parent.width
        spacing: 18
        
        Header {
            text: show.showName
        }
        
        Item {
            width: parent.width
            height: 192
            clip: true
            
            Image {
                anchors.left: parent.left
                anchors.leftMargin: 18
                id: image
                height: parent.height
                source: show.coverImage
                fillMode: "PreserveAspectFit"
                smooth: true
            }
            
            Flickable {
                id: flickableText
                anchors.left: image.right
                anchors.right: parent.right
                anchors.rightMargin: 18
                anchors.leftMargin: 18
                height: parent.height
                contentHeight: text.height
                contentWidth: width

                Text {
                    id: text
                    width: parent.width
                    text: show.showOverview
                    font.weight: Font.Light
                    font.pixelSize: 22
                    color: theme.inverted ? "#d2d2d2" : "#505050"
                    wrapMode: Text.Wrap
                }
            }
            ScrollDecorator{ flickableItem: flickableText }
        }
        
        /*Rectangle {
            color: theme.inverted ? "#d2d2d2" : "#505050"
            height: 1
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 16
            anchors.rightMargin: 16
        }*/
        Header {
            text: 'Seasons'
        }
    }

	ListView {
		id: listView
		anchors.top: metaData.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
		//anchors.leftMargin: 16
        clip: true
		model: show.get_seasons_model()
		delegate: ListRowDelegate {
            id: delegate
            title: show.get_season_name(model.data)
            subtitle: show.get_season_info_markup(model.data)
            iconSource: show.get_season_image(model.data)
            Component {
                id: seasonPageComponent
                SeasonPage { show: page.show; season: model.data }
            }
            ContextMenu {
                id: contextMenu
                MenuLayout {
                    MenuItem {
                        text: "Mark all";
                        onClicked: {
                            page.show.mark_all_as_watched(model.data);
                            delegate.subtitle = show.get_season_info_markup(model.data);
                        }
                    }
                }
            }
            onClicked: pageStack.push(seasonPageComponent.createObject(pageStack))
            onPressAndHold: contextMenu.open()
        }
	}
	ScrollDecorator{ flickableItem: listView }
    
	tools: ToolBarLayout {
		ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
		ToolIcon { iconId: "toolbar-view-menu"; onClicked: (myMenu.status == DialogStatus.Closed) ? myMenu.open() : myMenu.close() }
	}

	Menu {
		id: myMenu
		MenuLayout {
			MenuItem { 
                text: "Update show"
                onClicked: series_manager.update_show_episodes(show)
            }
		}
	}
}
