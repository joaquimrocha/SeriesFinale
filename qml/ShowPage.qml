import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page
    property variant show: undefined

    Dialog {
        id: showInfoDialog
        anchors.fill: parent
        anchors.verticalCenter: parent.verticalCenter

        content: Item {
            id: contents
            width: parent.width * .8
            height: page.height
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            Flickable {
                id: flickableContent
                width: parent.width
                height: parent.height
                contentHeight: showInfoDescription.height + titleItem.height
                contentWidth: width

                Item {
                    id: titleItem
                    width: parent.width
                    height: showNameText.height + 5

                    Text {
                        id: showNameText
                        text: show.showName
                        font.family: "Nokia Pure Text Light"
                        font.pixelSize: 26
                        font.weight: Font.Bold
                        color: 'white'
                    }
                    Rectangle {
                        anchors.top: parent.bottom
                        width: parent.width
                        height: 1
                        color: 'white'
                    }
                }

                Image {
                    id: showCover
                    source: show.coverImage
                    height: 300
                    fillMode: "PreserveAspectFit"
                    smooth: true
                    anchors.top: titleItem.bottom
                    anchors.topMargin: 10
                    anchors.horizontalCenter: rootWindow.inPortrait ? parent.horizontalCenter : undefined
                    anchors.left: !rootWindow.inPortrait ? parent.left : undefined

                }

                Text {
                    id: showInfoDescription
                    width: parent.width
                    anchors.top: rootWindow.inPortrait ? showCover.bottom : showCover.top
                    anchors.right: parent.right
                    anchors.left: rootWindow.inPortrait ? parent.left : showCover.right
                    anchors.leftMargin: 10
                    text: show.showOverview
                    font.weight: Font.Light
                    font.pixelSize: 22
                    color: theme.inverted ? secondaryTextColor : "#505050"
                    wrapMode: Text.Wrap
                }
            }
            ScrollDecorator{ flickableItem: flickableContent }
            }

    }


    Column {
        id: metaData
        anchors.top: parent.top
        width: parent.width
        spacing: 18

        Header {
            id: header
            text: show.showName
            busy: show.busy
            hasRefreshAction: true
            onRefreshActionActivated: series_manager.update_show_episodes(show)
            textWidth: header.width - infoIcon.width * 2.5

            Item {
                height: parent.height
                width: infoIcon.width
                anchors.right: header.anchorPoint
                anchors.rightMargin: 20

                Image {
                    id: infoIcon
                    source: 'icons/info-icon.png'
                    fillMode: "PreserveAspectFit"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            MouseArea {
                anchors.left: parent.left
                anchors.right: infoIcon.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: parent.width - infoIcon.width - 20
                height: parent.height
                onClicked: showInfoDialog.open()
            }
        }
    }

    ListView {
        id: listView
        anchors.top: metaData.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: show.get_seasons_model()
        delegate: ListRowDelegate {
            id: delegate
            title: show.get_season_name(model.data)
            subtitle: show.get_season_info_markup(model.data)
            iconSource: show.get_season_image(model.data)
            Connections {
                target: show
                onInfoMarkupChanged: subtitle = show.get_season_info_markup(model.data)
                onShowArtChanged: iconSource = show.get_season_image(model.data)
            }

            Component {
                id: seasonPageComponent
                SeasonPage { show: page.show; season: model.data }
            }
            ContextMenu {
                id: contextMenu
                MenuLayout {
                    MenuItem {
                        text: "Delete season";
                        onClicked: {
                            show.delete_season(model.data)
                            listView.model = show.get_seasons_model()
                        }
                    }
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
    }

    states: [
        State {
            name: "inLandscape"
            when: !rootWindow.inPortrait
            AnchorChanges {
                target: showCover
                anchors.horizontalCenter: undefined
                anchors.left: showCover.parent.left
            }
            AnchorChanges {
                target: showInfoDescription
                anchors.left: showCover.right
            }
            PropertyChanges {
                target: flickableContent
                contentHeight: showCover.height < showInfoDescription.height ? showInfoDescription.height + titleItem.height : showCover.height + titleItem.height
            }
        },
        State {
            name: "inPortrait"
            when: rootWindow.inPortrait
            AnchorChanges {
                target: showCover
                anchors.left: undefined
                anchors.horizontalCenter: showCover.parent.horizontalCenter
            }
            AnchorChanges {
                target: showInfoDescription
                anchors.left: showInfoDescription.parent.left
                anchors.top: showCover.bottom
            }
            PropertyChanges {
                target: flickableContent
                contentHeight: showCover.height + showInfoDescription.height + titleItem.height
            }
        }
    ]
}
