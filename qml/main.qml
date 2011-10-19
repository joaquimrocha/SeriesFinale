import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

PageStackWindow {
    id: rootWindow
    showStatusBar: true
    showToolBar: true
    initialPage: seriesPage

    property string activeTextColor: "#fff"
    property string inactiveTextColor: "#707070"
    property string secondaryTextColor: "#d2d2d2"

    Component {
        id: seriesPage
        SeriesPage {}
    }

    Component.onCompleted: {
        theme.inverted = true
        series_manager.updateShowEpisodesComplete.connect(function (show) {
            infoBanner.text = 'Updated "' + show.showName + '"'
            infoBanner.show()
        })
        series_manager.updateShowsCallComplete.connect(function() {
            infoBanner.text = "Finished updating the shows"
            infoBanner.show()
        })
    }

    InfoBanner{
        id: infoBanner
        timerEnabled: true
        timerShowTime: 3000
        topMargin: 44
    }

    platformStyle: PageStackWindowStyle {
        background: 'image://theme/meegotouch-video-background'
        backgroundFillMode: Image.Stretch
    }
}
