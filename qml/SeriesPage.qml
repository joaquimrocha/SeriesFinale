import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    Header {
        id: header;
        text: "SeriesFinale"
        busy: series_manager.busy
    }
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
            ContextMenu {
                id: contextMenu
                MenuLayout {
                    MenuItem {text: "Delete show"; onClicked: { series_manager.delete_show(model.data) } }
                }
            }

            onClicked: pageStack.push(showPageComponent.createObject(pageStack))
            onPressAndHold: {
                contextMenu.open()
            }
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
                text: "Add shows"
                onClicked: pageStack.push(addShowComponent.createObject(pageStack))
            }
            MenuItem {
                text: "Update all"
                onClicked: series_manager.update_all_shows_episodes()
            }
            MenuItem {
                text: "Settings"
                onClicked: settingsComponent.createObject(page).open()
                Component { id: settingsComponent; SettingsPage {} }
            }
        }
    }

    Component {
        id: addShowComponent
        AddShow {}
    }
}
