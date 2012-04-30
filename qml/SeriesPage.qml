import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page

    Header {
       id: header;
       text: "SeriesFinale"
       busy: series_manager.busy
       hasRefreshAction: !emptyText.visible
       onRefreshActionActivated: series_manager.update_all_shows_episodes()
    }

    ListView {
        id: listView
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: seriesList
        interactive: !emptyText.visible

        Text {
            id: emptyText
            text: 'No shows were added so far'
            font.pixelSize: 32
            visible: listView.count == 0
            color: 'white'
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
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
                onClicked: pageStack.push(settingsComponent.createObject(pageStack))
                Component { id: settingsComponent; SettingsPage {} }
            }
            MenuItem {
                text: "About"
                onClicked: pageStack.push(aboutComponent.createObject(pageStack))
                Component { id: aboutComponent; AboutPage {} }
            }
        }
    }

    Component {
        id: addShowComponent
        AddShow {}
    }
}
