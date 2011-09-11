import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

PageStackWindow {
    id: rootWindow
    showStatusBar: true
    showToolBar: true
    initialPage: seriesPage

    Component {
        id: seriesPage
        SeriesPage {}
    }

    Component.onCompleted: {
        //theme.inverted = true
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
}
