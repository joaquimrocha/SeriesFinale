import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property string season: ''
    property variant show: undefined

    ListView {
        id: listView
        anchors.fill: parent
        clip: true

header: Header {
        id: header
        text: show.showName + ' - ' + show.get_season_name(season)
    }


        model: show.get_sorted_episode_list_by_season(season)
        delegate: EpisodeListRowDelegate {
            episode: model.data
            Component {
                id: episodePageComponent
                EpisodePage {
                    show: page.show;
                    episode: model.data;
                    seasonImg: show.get_season_image(season)
                }
            }
            onClicked: pageStack.push(episodePageComponent.createObject(pageStack))
        }
    }

    ScrollDecorator { flickableItem: listView }

    tools: ToolBarLayout {
        ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
        ToolIcon {
            iconId: "toolbar-view-menu";
            onClicked: (myMenu.status == DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
    }

    Menu {
        id: myMenu
        MenuLayout {
            MenuItem {
                text: "Mark all"
                onClicked: show.mark_all_episodes_as_watched(season)
            }
            MenuItem {
                text: "Mark none"
                onClicked: show.mark_all_episodes_as_not_watched(season)
            }
        }
    }
}
