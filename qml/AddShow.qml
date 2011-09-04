import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

Page {
    id: page

    Component.onCompleted: searchTextField.forceActiveFocus()

    Header {
        id: header
        text: "Add show"
        busy: series_manager.isSearching
    }

    TextField {
        id: searchTextField
        anchors.top: header.bottom
        anchors.topMargin: 18
        anchors.left: parent.left
        anchors.leftMargin: 18
        anchors.right: parent.right
        anchors.rightMargin: 18
        placeholderText: "Search"
        platformSipAttributes: SipAttributes { actionKeyLabel: "Search"; actionKeyEnabled: true }
        platformStyle: TextFieldStyle { paddingRight: searchButton.width }

        Keys.onReturnPressed: search()

        Image {
            id: searchButton
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            source: "image://theme/icon-m-common-search"
            MouseArea {
                anchors.fill: parent
                onClicked: search()
            }
        }
    }

    ListView {
        id: listView
        anchors.top: searchTextField.bottom
        anchors.topMargin: 18
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        clip: true
            model: series_manager.search_result_model()
            delegate: ListRowDelegate {
                title: model.data
                height: 64
                onClicked: {
                    series_manager.get_complete_show(model.data);
                    pageStack.pop()
                }
            }
	}
	ScrollDecorator{ flickableItem: listView }

	tools: ToolBarLayout {
		ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop() } }
	}

    function search() {
        parent.focus = true //Make sure the keyboard closes and the text is updated
        series_manager.search_shows(searchTextField.text)
    }
}
