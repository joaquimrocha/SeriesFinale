import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property string season: ''
    property variant show: undefined
    
    Header {
        id: header
        text: show.showName + ' - ' + show.get_season_name(season)
        
    }

	ListView {
		id: listView
		anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
		//anchors.leftMargin: 16
        clip: true
		model: show.get_sorted_episode_list_by_season(season)
		delegate: ListRowDelegate {
            title: model.data.title
            subtitle: model.data.airDateText
            iconSource: model.data.isWatched ? 'image://theme/icon-m-common-done' : 'image://theme/icon-m-common-aqua'
            Component {
                id: episodePageComponent
                EpisodePage { show: page.show; episode: model.data; seasonImg: show.get_season_image(season) }
            }
            onClicked: pageStack.push(episodePageComponent.createObject(pageStack))
            
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
                text: "Mark all"
                onClicked: show.mark_all_as_watched(season)
            }
		}
	}
}
