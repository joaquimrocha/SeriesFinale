import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    ListView {
        id: listView
        anchors.fill: parent
        clip: true
        model: seriesList

        header: Header {
            id: header;
            text: "SeriesFinale"
            busy: series_manager.busy
            hasRefreshAction: true
            onRefreshActionActivated: series_manager.update_all_shows_episodes()
        }

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
        ToolIcon {
            iconId: "toolbar-add"
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: { pageStack.push(addShowComponent.createObject(pageStack)) }
        }
        ToolIcon {
            anchors.right: parent.right
            iconId: "toolbar-view-menu"
            onClicked: (myMenu.status == DialogStatus.Closed) ? myMenu.open() : myMenu.close()
        }
    }

    Menu {
        id: myMenu
        MenuLayout {
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
