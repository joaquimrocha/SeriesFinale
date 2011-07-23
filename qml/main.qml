import QtQuick 1.1
import com.nokia.meego 1.0
import com.nokia.extras 1.0

PageStackWindow {
	showStatusBar: true
	showToolBar: true
	initialPage: seriesPage

	Component {
		id: seriesPage
		SeriesPage {}
	}

	Component.onCompleted: {
		//theme.inverted = true
	}

    InfoBanner{
        id: infoBanner
        timerEnabled: true
        timerShowTime: 3000
        topMargin: 44
    }

    Connections {
        target: series_manager
        onUpdateShowEpisodesComplete: {
            infoBanner.text = 'Updated "xxx"'
            infoBanner.show()
        }
        onUpdateShowsCallComplete: {
            infoBanner.text = "Finished updating the shows"
            infoBanner.show()
        }
    }
}
