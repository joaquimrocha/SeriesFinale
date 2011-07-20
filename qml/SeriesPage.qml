import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    Header { id: header; text: "SeriesFinale" }
	ListView {
		id: listView
		anchors.top: header.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
		//anchors.margins: 16
        clip: true
		model: seriesList
		delegate: ListRowDelegate {
            title: model.data.showName
            subtitle: model.data.infoMarkup
            iconSource: model.data.coverImage
            Component {
                id: showPageComponent
                ShowPage { show: model.data }
            }
            onClicked: pageStack.push(showPageComponent.createObject(pageStack))

        }
	}
	ScrollDecorator{ flickableItem: listView }

	tools: ToolBarLayout {
		ToolIcon { iconId: "toolbar-back"; onClicked: { Qt.quit() } }
		ToolIcon { iconId: "toolbar-view-menu"; onClicked: (myMenu.status == DialogStatus.Closed) ? myMenu.open() : myMenu.close() }
	}

	Menu {
		id: myMenu
		MenuLayout {
			MenuItem {
				text: "Update all"
				onClicked: {
                    console.log("Update started")
                    series_manager.update_all_shows_episodes()
                }
			}
		}
	}
    
    Connections {
        target: series_manager
        onUpdateShowEpisodesComplete: {
            console.log("updateShowEpisodesComplete")
            console.log(arguments.length)
        }
    }
}
