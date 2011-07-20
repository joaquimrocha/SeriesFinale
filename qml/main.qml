import QtQuick 1.1
import com.nokia.meego 1.0

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
}
